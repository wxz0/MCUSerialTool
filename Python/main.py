"""
主程序入口和SerialConfig类
使用模块化设计，将不同的功能分离到独立的模块中
"""

import sys
from datetime import datetime

from PySide6.QtCore import Property, QObject, Signal, Slot, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo

from autogen.settings import setup_qt_environment
from serial_config_parser import SerialConfigParser
from data_handler import DataHandler
from modbus_protocol import ModbusProtocol
from serial_port_manager import SerialPortManager


class SerialConfig(QObject):
    """
    主控制类：协调串口配置、数据传输和Modbus协议处理
    使用模块化设计将具体功能委托给专用模块
    """
    
    availablePortsChanged = Signal()
    serialOpenChanged = Signal()
    serialStatusChanged = Signal()
    receivedTextChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initialize_properties()
        self._initialize_serial_port()
        self._initialize_timers()
        self._initialize_modules()

    def _initialize_properties(self):
        """初始化所有属性"""
        self._available_ports = []
        self._raw_port_names = []
        self._serial_open = False
        self._serial_status = "串口未打开"
        self._received_text = ""
        self._receive_hex_mode = False
        self._send_hex_mode = False
        self._timestamp_enabled = False
        self._modbus_mode = False
        self._modbus_rx_buffer = b""
        self._modbus_scan_active = False
        self._modbus_query_timeout_ms = 220

    def _initialize_modules(self):
        """初始化各功能模块"""
        self._config_parser = SerialConfigParser()
        self._data_handler = DataHandler()
        self._modbus_protocol = ModbusProtocol()
        self._port_manager = SerialPortManager(self._serial)

    def _initialize_serial_port(self):
        """初始化串口对象和相关连接"""
        self._serial = QSerialPort(self)
        self._serial.errorOccurred.connect(self._on_serial_error)
        self._serial.readyRead.connect(self._on_ready_read)

    def _initialize_timers(self):
        """初始化定时器"""
        # Modbus超时定时器
        self._modbus_timeout_timer = QTimer(self)
        self._modbus_timeout_timer.setSingleShot(True)
        self._modbus_timeout_timer.setInterval(1000)
        self._modbus_timeout_timer.timeout.connect(self._on_modbus_timeout)

        # 串口监控定时器 (用于热拔插检测)
        self._port_monitor_timer = QTimer(self)
        self._port_monitor_timer.setInterval(1000)
        self._port_monitor_timer.timeout.connect(self._auto_refresh_ports)
        self._port_monitor_timer.start()

    # ============================================================
    # 属性定义 (Properties)
    # ============================================================

    @Property(bool, notify=serialOpenChanged)
    def serialOpen(self):
        return self._serial_open

    @Property(str, notify=serialStatusChanged)
    def serialStatus(self):
        return self._serial_status

    @Property(str, notify=receivedTextChanged)
    def receivedText(self):
        return self._received_text

    @Property(bool, notify=receivedTextChanged)
    def timestampEnabled(self):
        return self._timestamp_enabled

    @Property(bool, notify=availablePortsChanged)
    def hasAvailablePorts(self):
        return bool(self._available_ports) and self._available_ports[0] != "无可用串口"

    @Property("QStringList", notify=availablePortsChanged)
    def availablePorts(self):
        return self._available_ports

    @Property("QStringList", constant=True)
    def baudRates(self):
        return self._config_parser.BAUD_RATES

    @Property("QStringList", constant=True)
    def parityOptions(self):
        return self._config_parser.PARITY_OPTIONS

    @Property("QStringList", constant=True)
    def stopBitsOptions(self):
        return self._config_parser.STOP_BITS_OPTIONS

    @Property("QStringList", constant=True)
    def encodingOptions(self):
        return ["UTF-8", "GBK", "GB2312", "ASCII", "Latin-1", "UTF-16"]

    # ============================================================
    # 串口操作 (Serial Operations)
    # ============================================================

    @Slot()
    def refreshPorts(self):
        """手动刷新串口列表"""
        self._refresh_ports_internal(status_on_no_change=True, source="manual")

    def _auto_refresh_ports(self):
        """自动刷新串口列表（由定时器触发）"""
        self._refresh_ports_internal(status_on_no_change=False, source="auto")

    def _refresh_ports_internal(self, status_on_no_change, source):
        """
        内部串口刷新实现
        检测串口变化、处理断开连接等事件
        """
        ports = []
        raw_port_names = []
        
        for port in QSerialPortInfo.availablePorts():
            raw_port_names.append(port.portName())
            description = port.description().strip()
            display_text = f"{port.portName()} ({description})" if description else port.portName()
            ports.append(display_text)

        if not ports:
            ports = ["无可用串口"]

        changed = ports != self._available_ports
        if changed:
            self._available_ports = ports
            self._raw_port_names = raw_port_names
            self.availablePortsChanged.emit()

            # 如果已打开的串口被拔出，自动关闭
            if self._serial.isOpen() and self._serial.portName() not in self._raw_port_names:
                lost_port = self._serial.portName()
                self.closeSerial()
                self._set_status(f"串口 {lost_port} 已断开，已自动关闭")

            if source == "auto":
                if self.hasAvailablePorts:
                    self._set_status(f"检测到串口变化，已自动刷新（共 {len(ports)} 个）")
                else:
                    self._set_status("检测到串口变化，当前无可用串口")
                return

        if status_on_no_change or changed:
            if self.hasAvailablePorts:
                self._set_status(f"已刷新串口列表，共 {len(ports)} 个")
            else:
                self._set_status("未检测到可用串口")

    @Slot(str, str, str, str, result=bool)
    def openSerial(self, port_text, baud_text, parity_text, stop_bits_text):
        """打开串口"""
        # 解析和验证参数
        port_name = self._config_parser.extract_port_name(port_text)
        if not port_name:
            self._set_status("没有可用串口，无法打开")
            return False

        baud_rate = self._config_parser.parse_baud_rate(baud_text)
        if baud_rate is None:
            self._set_status(f"无效波特率: {baud_text}")
            return False

        parity = self._config_parser.parse_parity(parity_text)
        if parity is None:
            self._set_status(f"无效校验位: {parity_text}")
            return False

        stop_bits = self._config_parser.parse_stop_bits(stop_bits_text)
        if stop_bits is None:
            self._set_status(f"无效停止位: {stop_bits_text}")
            return False

        # 尝试打开串口
        if not self._port_manager.open(port_name, baud_rate, parity, stop_bits):
            self._serial_open = False
            self.serialOpenChanged.emit()
            self._set_status(f"打开失败: {self._port_manager.get_error_string()}")
            return False

        self._serial_open = True
        self.serialOpenChanged.emit()
        status = (f"已打开 {port_name} | {baud_rate}bps | "
                  f"{self._config_parser.parity_label(parity)} | "
                  f"{self._config_parser.stop_bits_label(stop_bits)}")
        self._set_status(status)
        return True

    @Slot()
    def closeSerial(self):
        """关闭串口"""
        self._port_manager.close()
        if self._serial_open:
            self._serial_open = False
            self.serialOpenChanged.emit()
        self._set_status("串口已关闭")

    @Slot(str, str, str, str)
    def toggleSerial(self, port_text, baud_text, parity_text, stop_bits_text):
        """切换串口状态 (打开/关闭)"""
        if self._serial.isOpen():
            self.closeSerial()
        else:
            self.openSerial(port_text, baud_text, parity_text, stop_bits_text)

    # ============================================================
    # 数据传输 (Data Transfer)
    # ============================================================

    @Slot(str)
    def setEncoding(self, encoding):
        """设置数据编码格式"""
        self._data_handler.set_encoding(encoding)

    @Slot(bool)
    def setReceiveHexMode(self, enabled):
        """设置接收HEX模式"""
        self._receive_hex_mode = bool(enabled)
        self._data_handler._reset_decoder()

    @Slot(bool)
    def setSendHexMode(self, enabled):
        """设置发送HEX模式"""
        self._send_hex_mode = bool(enabled)

    @Slot(bool)
    def setTimestampEnabled(self, enabled):
        """启用/禁用时间戳"""
        self._timestamp_enabled = bool(enabled)

    @Slot(str, result=bool)
    def sendData(self, text):
        """发送数据"""
        if not self._serial.isOpen():
            self._set_status("串口未打开，无法发送")
            return False

        payload = self._data_handler.build_send_payload(text or "", self._send_hex_mode)
        if payload is None:
            self._set_status("HEX 发送格式错误，请输入如: 01 03 00 00 00 01 或 0x01,0x03,...")
            return False

        sent_len = self._port_manager.write(payload)
        if sent_len == -1:
            self._set_status(f"发送失败: {self._port_manager.get_error_string()}")
            return False

        self._set_status(f"已发送 {sent_len} 字节")
        return True

    @Slot()
    def clearReceivedText(self):
        """清空接收数据显示"""
        if self._received_text:
            self._received_text = ""
            self.receivedTextChanged.emit()
        self._data_handler._reset_decoder()

    # ============================================================
    # Modbus操作 (Modbus Operations)
    # ============================================================

    @Slot(bool)
    def setModbusMode(self, enabled):
        """启用/禁用Modbus模式"""
        self._modbus_mode = bool(enabled)
        self._modbus_rx_buffer = b""
        if not enabled:
            self._modbus_timeout_timer.stop()

    @Slot(int)
    def setModbusQueryTimeout(self, timeout_ms):
        """设置Modbus查询超时时间"""
        try:
            value = int(timeout_ms)
        except (TypeError, ValueError):
            value = 220
        self._modbus_query_timeout_ms = max(20, min(value, 2000))

    @Slot(str, str, str, str, result=str)
    def sendModbusCommand(self, dev_addr_text, fc_text, start_addr_text, reg_len_text):
        """发送Modbus命令"""
        if not self._serial.isOpen():
            self._set_status("串口未打开，无法发送 Modbus 命令")
            return ""

        try:
            dev_addr = int(dev_addr_text.strip())
            fc = int(fc_text.strip()[:2], 16)
            start_addr = self._modbus_protocol.parse_hex_u16(start_addr_text)
            reg_len = int(reg_len_text.strip())
        except (ValueError, TypeError, IndexError):
            self._set_status("Modbus 参数解析失败，请检查输入")
            return ""

        frame = self._modbus_protocol.build_frame(dev_addr, fc, start_addr, reg_len)
        if frame is None:
            self._set_status(f"不支持的功能码")
            return ""

        hex_str = " ".join(f"{b:02X}" for b in frame)
        sent = self._port_manager.write(frame)
        if sent == -1:
            self._set_status(f"发送失败: {self._port_manager.get_error_string()}")
            return ""

        self._modbus_rx_buffer = b""
        self._modbus_timeout_timer.start()
        self._set_status(f"已发送 Modbus 命令: {hex_str}")
        return hex_str

    @Slot(str, result=str)
    def queryModbusDeviceAddresses(self, register_addr_text):
        """扫描并查询Modbus设备地址"""
        if not self._serial.isOpen():
            self._set_status("串口未打开，无法执行地址查询")
            return ""

        try:
            register_addr = self._modbus_protocol.parse_hex_u16(register_addr_text)
        except (ValueError, TypeError):
            self._set_status("寄存器地址无效，请输入 HEX(0000-FFFF)")
            return ""

        self._set_status(
            f"开始扫描寄存器地址 0x{register_addr:04X} 对应的设备，单设备超时 {self._modbus_query_timeout_ms}ms..."
        )
        self._modbus_timeout_timer.stop()
        self._modbus_scan_active = True
        found = []

        try:
            # 扫描地址 1..247
            for addr in range(1, 248):
                req = self._modbus_protocol.build_frame(addr, 0x03, register_addr, 1)
                if req is None:
                    continue

                self._port_manager.clear_read_buffer()
                sent = self._port_manager.write(req)
                if sent == -1:
                    continue
                
                self._port_manager.wait_for_bytes_written(40)

                frame = self._read_modbus_frame_blocking(self._modbus_query_timeout_ms)
                if frame and self._modbus_protocol.is_valid_frame(frame) and frame[0] == addr:
                    if frame[1] == 0x03 and len(frame) >= 7 and frame[2] == 2:
                        found.append(addr)
        finally:
            self._modbus_scan_active = False

        # 生成结果
        if found:
            result = f"寄存器地址 0x{register_addr:04X} 对应设备地址: {', '.join(map(str, found))}"
            self._set_status(f"扫描完成，命中 {len(found)} 个设备")
        else:
            result = f"寄存器地址 0x{register_addr:04X} 未找到可响应设备"
            self._set_status("扫描完成，未找到设备")

        # 添加到接收文本
        ts = DataHandler._get_timestamp() if self._timestamp_enabled else ""
        if self._received_text:
            self._received_text += "\n"
        self._received_text += f"{ts}[Modbus地址查询] {result}"
        self.receivedTextChanged.emit()

        return result

    def _read_modbus_frame_blocking(self, timeout_ms):
        """阻塞式读取完整的Modbus帧"""
        elapsed = 0
        step = 20
        buffer = b""

        while elapsed < timeout_ms:
            wait = min(step, timeout_ms - elapsed)
            if not self._port_manager.wait_for_ready_read(wait):
                elapsed += wait
                continue

            buffer += self._port_manager.read_all()
            expected = self._modbus_protocol.expected_frame_length(buffer)
            if expected is not None and len(buffer) >= expected:
                return buffer[:expected]

            elapsed += wait

        return None

    # ============================================================
    # 内部事件处理 (Internal Event Handlers)
    # ============================================================

    @Slot(QSerialPort.SerialPortError)
    def _on_serial_error(self, error):
        """处理串口错误"""
        if error == QSerialPort.ResourceError and self._serial.isOpen():
            port_name = self._serial.portName()
            self.closeSerial()
            self._set_status(f"串口 {port_name} 发生资源错误，已自动关闭")

    @Slot()
    def _on_ready_read(self):
        """处理串口数据可读事件"""
        if self._modbus_scan_active:
            return

        raw_data = self._port_manager.read_all()
        if not raw_data:
            return

        # 停止Modbus超时定时器（表示数据正在到达）
        if self._modbus_timeout_timer.isActive():
            self._modbus_timeout_timer.stop()

        # Modbus模式：累积并解析完整的RTU帧
        if self._modbus_mode:
            self._handle_modbus_mode(raw_data)
            return

        # 普通模式：处理文本或HEX数据
        self._handle_normal_mode(raw_data)

    def _handle_modbus_mode(self, raw_data):
        """处理Modbus模式下的数据"""
        self._modbus_rx_buffer += raw_data
        result = self._try_parse_modbus(self._modbus_rx_buffer)
        if result is not None:
            self._modbus_timeout_timer.stop()
            self._modbus_rx_buffer = b""
            ts = DataHandler._get_timestamp() if self._timestamp_enabled else ""
            self._received_text += ts + result + "\n"
            self.receivedTextChanged.emit()

    def _handle_normal_mode(self, raw_data):
        """处理普通模式下的数据"""
        ts = DataHandler._get_timestamp() if self._timestamp_enabled else ""

        if self._receive_hex_mode:
            chunk = " ".join(f"{byte:02X}" for byte in raw_data)
            if self._received_text:
                self._received_text += "\n"
            self._received_text += ts + chunk
        else:
            decoded = self._data_handler.decode_raw_data(raw_data)
            if decoded:
                if self._timestamp_enabled:
                    lines = decoded.split("\n")
                    stamped = []
                    for i, line in enumerate(lines):
                        if i == 0:
                            if not self._received_text or self._received_text.endswith("\n"):
                                stamped.append(ts + line)
                            else:
                                stamped.append(line)
                        else:
                            if i == len(lines) - 1 and line == "":
                                stamped.append("")
                            else:
                                stamped.append(ts + line)
                    self._received_text += "\n".join(stamped)
                else:
                    self._received_text += decoded

        self.receivedTextChanged.emit()

    @Slot()
    def _on_modbus_timeout(self):
        """处理Modbus通信超时"""
        self._modbus_rx_buffer = b""
        self._set_status("⚠ Modbus 通信失败：超时未收到从机回应")
        ts = DataHandler._get_timestamp() if self._timestamp_enabled else ""
        self._received_text += f"\n{ts}[Modbus] ⚠ 超时未收到从机回应\n"
        self.receivedTextChanged.emit()

    def _try_parse_modbus(self, buf: bytes):
        """尝试从缓冲区中解析Modbus响应"""
        expected = self._modbus_protocol.expected_frame_length(buf)
        if expected is None or len(buf) < expected:
            return None

        frame = buf[:expected]
        return self._modbus_protocol.parse_response(frame)

    def _set_status(self, text):
        """更新状态消息"""
        if text != self._serial_status:
            self._serial_status = text
            self.serialStatusChanged.emit()


def main():
    """主程序入口"""
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    serial_config = SerialConfig()
    serial_config.refreshPorts()
    app.aboutToQuit.connect(serial_config.closeSerial)

    engine.rootContext().setContextProperty("serialConfig", serial_config)
    setup_qt_environment(engine)

    if not engine.rootObjects():
        sys.exit(-1)

    ex = app.exec()
    del engine
    return ex


if __name__ == "__main__":
    sys.exit(main())



