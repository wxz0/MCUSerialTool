"""
Modbus协议处理模块
支持Modbus RTU格式的帧构建和解析
"""


class ModbusProtocol:
    """Modbus RTU协议相关的功能"""

    # 支持的功能码
    SUPPORTED_FC = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0F, 0x10}

    @staticmethod
    def crc16(data: bytes) -> int:
        """
        计算Modbus CRC-16校验码
        使用CRC-16-CCITT-False算法
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    @staticmethod
    def build_frame(dev_addr: int, fc: int, start_addr: int, reg_len: int) -> bytes:
        """
        构建Modbus RTU帧
        
        参数:
            dev_addr: 设备地址 (1-247)
            fc: 功能码
            start_addr: 起始地址
            reg_len: 寄存器数量或值
            
        返回:
            完整的Modbus帧（包含CRC）或None
        """
        if fc in (0x01, 0x02, 0x03, 0x04):
            # 读取线圈/寄存器
            payload = bytes([
                dev_addr, fc,
                (start_addr >> 8) & 0xFF, start_addr & 0xFF,
                (reg_len >> 8) & 0xFF, reg_len & 0xFF,
            ])
        elif fc in (0x05, 0x06):
            # 写单个线圈/寄存器
            payload = bytes([
                dev_addr, fc,
                (start_addr >> 8) & 0xFF, start_addr & 0xFF,
                (reg_len >> 8) & 0xFF, reg_len & 0xFF,
            ])
        elif fc in (0x0F, 0x10):
            # 写多个线圈/寄存器
            payload = bytes([
                dev_addr, fc,
                (start_addr >> 8) & 0xFF, start_addr & 0xFF,
                (reg_len >> 8) & 0xFF, reg_len & 0xFF,
                0x00,
            ])
        else:
            return None

        crc = ModbusProtocol.crc16(payload)
        return payload + bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    @staticmethod
    def build_write_frame(dev_addr: int, fc: int, start_addr: int, values) -> bytes:
        """
        构建Modbus写命令RTU帧（05/06/0F/10）

        参数:
            dev_addr: 设备地址 (1-247)
            fc: 写功能码 (0x05, 0x06, 0x0F, 0x10)
            start_addr: 起始地址
            values: 写入值列表
        """
        if dev_addr < 1 or dev_addr > 247:
            return None
        if start_addr < 0 or start_addr > 0xFFFF:
            return None
        if not values:
            return None

        if fc == 0x05:
            if len(values) != 1:
                return None
            coil_on = bool(values[0])
            out_val = 0xFF00 if coil_on else 0x0000
            payload = bytes([
                dev_addr, fc,
                (start_addr >> 8) & 0xFF, start_addr & 0xFF,
                (out_val >> 8) & 0xFF, out_val & 0xFF,
            ])
        elif fc == 0x06:
            if len(values) != 1:
                return None
            reg_val = int(values[0])
            if reg_val < 0 or reg_val > 0xFFFF:
                return None
            payload = bytes([
                dev_addr, fc,
                (start_addr >> 8) & 0xFF, start_addr & 0xFF,
                (reg_val >> 8) & 0xFF, reg_val & 0xFF,
            ])
        elif fc == 0x0F:
            qty = len(values)
            if qty < 1 or qty > 1968:
                return None
            byte_count = (qty + 7) // 8
            packed = [0] * byte_count
            for i, coil_val in enumerate(values):
                if int(coil_val):
                    packed[i // 8] |= 1 << (i % 8)
            payload = bytes([
                dev_addr, fc,
                (start_addr >> 8) & 0xFF, start_addr & 0xFF,
                (qty >> 8) & 0xFF, qty & 0xFF,
                byte_count,
                *packed,
            ])
        elif fc == 0x10:
            qty = len(values)
            if qty < 1 or qty > 123:
                return None
            data = []
            for reg_val in values:
                reg_val = int(reg_val)
                if reg_val < 0 or reg_val > 0xFFFF:
                    return None
                data.extend([(reg_val >> 8) & 0xFF, reg_val & 0xFF])
            payload = bytes([
                dev_addr, fc,
                (start_addr >> 8) & 0xFF, start_addr & 0xFF,
                (qty >> 8) & 0xFF, qty & 0xFF,
                qty * 2,
                *data,
            ])
        else:
            return None

        crc = ModbusProtocol.crc16(payload)
        return payload + bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    @staticmethod
    def is_valid_frame(frame: bytes) -> bool:
        """验证Modbus帧的CRC校验"""
        if len(frame) < 5:
            return False
        calc_crc = ModbusProtocol.crc16(frame[:-2])
        recv_crc = frame[-2] | (frame[-1] << 8)
        return calc_crc == recv_crc

    @staticmethod
    def expected_frame_length(buf: bytes) -> int:
        """
        计算期望的Modbus帧长度
        用于确定是否收到完整帧
        """
        if len(buf) < 2:
            return None
        
        fc = buf[1]
        
        # 异常响应长度为5
        if fc & 0x80:
            return 5
        
        # 读取线圈/输入状态的响应
        if fc in (0x01, 0x02):
            if len(buf) < 3:
                return None
            return 5 + buf[2]
        
        # 读/写寄存器的响应
        if fc in (0x03, 0x04):
            if len(buf) < 3:
                return None
            return 5 + buf[2]
        
        # 写单个或多个线圈/寄存器的响应
        if fc in (0x05, 0x06, 0x0F, 0x10):
            return 8
        
        return None

    @staticmethod
    def parse_response(frame: bytes) -> str:
        """
        解析Modbus响应帧为可读文本
        返回格式化的响应信息
        """
        if len(frame) < 4:
            return None

        addr = frame[0]
        fc = frame[1]
        recv_crc = frame[-2] | (frame[-1] << 8)

        # 检查CRC
        calc_crc = ModbusProtocol.crc16(frame[:-2])
        if calc_crc != recv_crc:
            return (f"[Modbus] CRC 校验失败\n"
                    f"  设备地址: {addr}\n"
                    f"  功能码:   0x{fc & 0x7F:02X}\n"
                    f"  计算校验: {calc_crc:04X}  接收校验: {recv_crc:04X}")

        # 异常响应
        if fc & 0x80:
            real_fc = fc & 0x7F
            err = frame[2]
            desc = {
                0x01: "非法功能码",
                0x02: "非法数据地址",
                0x03: "非法数据值",
                0x04: "从设备故障"
            }.get(err, f"未知(0x{err:02X})")
            return (f"[Modbus] 从机异常响应\n"
                    f"  设备地址: {addr}\n"
                    f"  功能码:   0x{real_fc:02X}（异常）\n"
                    f"  错误码:   0x{err:02X} {desc}\n"
                    f"  校验码:   {recv_crc:04X}")

        # 读取线圈/离散输入
        if fc in (0x01, 0x02):
            byte_count = frame[2]
            data_hex = " ".join(f"{b:02X}" for b in frame[3:3 + byte_count])
            return (f"[Modbus] 读取线圈/离散输入\n"
                    f"  设备地址: {addr}\n"
                    f"  功能码:   0x{fc:02X}\n"
                    f"  数据长度: {byte_count} 字节\n"
                    f"  数据:     {data_hex}\n"
                    f"  校验码:   {recv_crc:04X}")

        # 读取寄存器
        if fc in (0x03, 0x04):
            byte_count = frame[2]
            data_bytes = frame[3:3 + byte_count]
            data_hex = " ".join(f"{b:02X}" for b in data_bytes)
            regs = [str((data_bytes[i] << 8) | data_bytes[i + 1])
                    for i in range(0, len(data_bytes) - 1, 2)]
            return (f"[Modbus] 读取寄存器\n"
                    f"  设备地址: {addr}\n"
                    f"  功能码:   0x{fc:02X}\n"
                    f"  数据长度: {byte_count} 字节\n"
                    f"  数据:     {data_hex}\n"
                    f"  寄存器值: {', '.join(regs)}\n"
                    f"  校验码:   {recv_crc:04X}")

        # 写单个线圈/寄存器
        if fc in (0x05, 0x06):
            out_addr = (frame[2] << 8) | frame[3]
            out_val = (frame[4] << 8) | frame[5]
            return (f"[Modbus] 写单个线圈/寄存器\n"
                    f"  设备地址: {addr}\n"
                    f"  功能码:   0x{fc:02X}\n"
                    f"  输出地址: {out_addr}\n"
                    f"  输出值:   {out_val}\n"
                    f"  校验码:   {recv_crc:04X}")

        # 写多个线圈/寄存器
        if fc in (0x0F, 0x10):
            s_addr = (frame[2] << 8) | frame[3]
            qty = (frame[4] << 8) | frame[5]
            return (f"[Modbus] 写多个线圈/寄存器\n"
                    f"  设备地址: {addr}\n"
                    f"  功能码:   0x{fc:02X}\n"
                    f"  起始地址: {s_addr}\n"
                    f"  数量:     {qty}\n"
                    f"  校验码:   {recv_crc:04X}")

        # 未知响应
        raw_hex = " ".join(f"{b:02X}" for b in frame)
        return (f"[Modbus] 未知响应\n"
                f"  设备地址: {addr}\n"
                f"  功能码:   0x{fc:02X}\n"
                f"  原始数据: {raw_hex}")

    @staticmethod
    def parse_hex_u16(text: str) -> int:
        """
        解析16位HEX数值
        返回0-0xFFFF范围内的值
        """
        raw = str(text).strip()
        if not raw:
            raise ValueError("empty hex text")
        value = int(raw, 16)
        if value < 0 or value > 0xFFFF:
            raise ValueError("hex value out of range")
        return value
