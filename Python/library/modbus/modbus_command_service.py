"""
Modbus命令构建服务
封装读写命令参数解析、校验与帧构建
"""

import re


class ModbusCommandService:
    """负责解析输入并构建Modbus读写帧。"""

    def __init__(self, modbus_protocol):
        self._modbus_protocol = modbus_protocol

    def build_read_frame(self, dev_addr_text, fc_text, start_addr_text, reg_len_text):
        """构建读命令帧，返回(frame, error_message)。"""
        try:
            dev_addr = int(dev_addr_text.strip())
            fc = int(fc_text.strip()[:2], 16)
            start_addr = self._modbus_protocol.parse_hex_u16(start_addr_text)
            reg_len = int(reg_len_text.strip())
        except (ValueError, TypeError, IndexError):
            return None, "Modbus 参数解析失败，请检查输入"

        if fc not in (0x01, 0x02, 0x03, 0x04):
            return None, "读命令仅支持功能码 01/02/03/04"

        if fc in (0x01, 0x02) and not (1 <= reg_len <= 2000):
            return None, "读线圈/离散输入数量范围应为 1-2000"

        if fc in (0x03, 0x04) and not (1 <= reg_len <= 125):
            return None, "读寄存器数量范围应为 1-125"

        frame = self._modbus_protocol.build_frame(dev_addr, fc, start_addr, reg_len)
        if frame is None:
            return None, "不支持的功能码"

        return frame, ""

    def build_write_frame(self, dev_addr_text, fc_text, register_addr_text, value_text):
        """构建写命令帧，返回(frame, fc, error_message)。"""
        try:
            dev_addr = int(dev_addr_text.strip())
            fc = int(fc_text.strip()[:2], 16)
            register_addr = self._modbus_protocol.parse_hex_u16(register_addr_text)
            tokens = self._split_value_tokens(value_text)
        except (ValueError, TypeError, IndexError):
            return None, None, "写命令参数解析失败，请检查输入"

        if fc not in (0x05, 0x06, 0x0F, 0x10):
            return None, None, "写命令仅支持功能码 05/06/0F/10"

        try:
            if fc in (0x05, 0x06):
                if len(tokens) != 1:
                    return None, None, "功能码 05/06 仅支持单个写入值"
                if fc == 0x05:
                    values = [self._parse_coil_value(tokens[0])]
                else:
                    values = [self._parse_u16_value(tokens[0])]
            elif fc == 0x0F:
                values = [self._parse_coil_value(token) for token in tokens]
            else:
                values = [self._parse_u16_value(token) for token in tokens]
        except ValueError:
            return None, None, "写入值格式无效，请检查输入"

        frame = self._modbus_protocol.build_write_frame(dev_addr, fc, register_addr, values)
        if frame is None:
            return None, None, "构建写命令失败，请检查地址/数量/数值范围"

        return frame, fc, ""

    @staticmethod
    def _parse_u16_value(text):
        """解析寄存器写入值，支持十进制或0x前缀HEX。"""
        raw = str(text).strip()
        if not raw:
            raise ValueError("empty register value")

        base = 16 if raw.lower().startswith("0x") else 10
        value = int(raw, base)
        if value < 0 or value > 0xFFFF:
            raise ValueError("register value out of range")
        return value

    @staticmethod
    def _split_value_tokens(text):
        """将输入值拆分为多个token，支持空格/逗号/分号分隔。"""
        raw = str(text).strip()
        if not raw:
            raise ValueError("empty value input")
        tokens = [token for token in re.split(r"[\s,;]+", raw) if token]
        if not tokens:
            raise ValueError("empty value token list")
        return tokens

    @staticmethod
    def _parse_coil_value(text):
        """解析线圈值，支持 0/1/false/true/off/on。"""
        raw = str(text).strip().lower()
        if raw in ("1", "true", "on"):
            return 1
        if raw in ("0", "false", "off"):
            return 0
        raise ValueError("invalid coil value")
