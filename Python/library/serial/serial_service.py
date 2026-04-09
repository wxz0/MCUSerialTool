"""
串口业务服务模块
封装串口列表获取、参数解析与开关串口流程
"""

from PySide6.QtSerialPort import QSerialPortInfo


class SerialService:
    """串口业务服务。"""

    def __init__(self, config_parser, port_manager):
        self._config_parser = config_parser
        self._port_manager = port_manager

    def get_available_ports(self):
        """获取可用串口显示文本列表和原始端口名列表。"""
        ports = []
        raw_port_names = []

        for port in QSerialPortInfo.availablePorts():
            raw_port_names.append(port.portName())
            description = port.description().strip()
            display_text = f"{port.portName()} ({description})" if description else port.portName()
            ports.append(display_text)

        if not ports:
            ports = ["无可用串口"]

        return ports, raw_port_names

    def open_serial(self, port_text, baud_text, parity_text, stop_bits_text):
        """解析并打开串口，返回(success, status_message)。"""
        port_name = self._config_parser.extract_port_name(port_text)
        if not port_name:
            return False, "没有可用串口，无法打开"

        baud_rate = self._config_parser.parse_baud_rate(baud_text)
        if baud_rate is None:
            return False, f"无效波特率: {baud_text}"

        parity = self._config_parser.parse_parity(parity_text)
        if parity is None:
            return False, f"无效校验位: {parity_text}"

        stop_bits = self._config_parser.parse_stop_bits(stop_bits_text)
        if stop_bits is None:
            return False, f"无效停止位: {stop_bits_text}"

        if not self._port_manager.open(port_name, baud_rate, parity, stop_bits):
            return False, f"打开失败: {self._port_manager.get_error_string()}"

        status = (
            f"已打开 {port_name} | {baud_rate}bps | "
            f"{self._config_parser.parity_label(parity)} | "
            f"{self._config_parser.stop_bits_label(stop_bits)}"
        )
        return True, status

    def close_serial(self):
        """关闭串口。"""
        self._port_manager.close()
