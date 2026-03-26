"""
串口配置参数的解析和验证模块
"""

from PySide6.QtSerialPort import QSerialPort


class SerialConfigParser:
    """处理串口配置参数的解析和验证"""

    # 波特率选项
    BAUD_RATES = [
        "300", "600", "1200", "2400", "4800", "9600",
        "14400", "19200", "38400", "57600", "115200",
        "230400", "460800", "921600"
    ]

    # 校验位选项
    PARITY_OPTIONS = ["无校验 (None)", "奇校验 (Odd)", "偶校验 (Even)", "Mark", "Space"]

    # 停止位选项
    STOP_BITS_OPTIONS = ["1", "1.5", "2"]

    @staticmethod
    def extract_port_name(port_text):
        """
        从端口文本中提取端口号
        例如：从 "COM1 (USB串口)" 提取 "COM1"
        """
        if not port_text or port_text == "无可用串口":
            return None

        if " (" in port_text:
            return port_text.split(" (", 1)[0]

        return port_text

    @staticmethod
    def parse_baud_rate(baud_text):
        """解析波特率"""
        try:
            return int(baud_text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def parse_parity(parity_text):
        """
        解析校验位
        返回 QSerialPort 中对应的校验位值
        """
        mapping = {
            "无校验 (None)": QSerialPort.NoParity,
            "奇校验 (Odd)": QSerialPort.OddParity,
            "偶校验 (Even)": QSerialPort.EvenParity,
            "Mark": QSerialPort.MarkParity,
            "Space": QSerialPort.SpaceParity,
        }
        return mapping.get(parity_text)

    @staticmethod
    def parse_stop_bits(stop_bits_text):
        """
        解析停止位
        返回 QSerialPort 中对应的停止位值
        """
        mapping = {
            "1": QSerialPort.OneStop,
            "1.5": QSerialPort.OneAndHalfStop,
            "2": QSerialPort.TwoStop,
        }
        return mapping.get(stop_bits_text)

    @staticmethod
    def parity_label(parity):
        """将校验位枚举转换为标签文本"""
        labels = {
            QSerialPort.NoParity: "None",
            QSerialPort.OddParity: "Odd",
            QSerialPort.EvenParity: "Even",
            QSerialPort.MarkParity: "Mark",
            QSerialPort.SpaceParity: "Space",
        }
        return labels.get(parity, "Unknown")

    @staticmethod
    def stop_bits_label(stop_bits):
        """将停止位枚举转换为标签文本"""
        labels = {
            QSerialPort.OneStop: "1",
            QSerialPort.OneAndHalfStop: "1.5",
            QSerialPort.TwoStop: "2",
        }
        return labels.get(stop_bits, "Unknown")
