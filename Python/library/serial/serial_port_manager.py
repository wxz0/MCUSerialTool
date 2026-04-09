"""
串口底层操作封装模块
处理串口的打开、关闭、读写等基本操作
"""

from PySide6.QtSerialPort import QSerialPort


class SerialPortManager:
    """管理串口的底层操作"""

    def __init__(self, serial_port: QSerialPort):
        """初始化串口管理器"""
        self.serial = serial_port

    def is_open(self) -> bool:
        """检查串口是否已打开"""
        return self.serial.isOpen()

    def get_port_name(self) -> str:
        """获取当前串口名称"""
        return self.serial.portName()

    def open(self, port_name: str, baud_rate: int, parity, stop_bits) -> bool:
        """
        打开串口
        
        参数:
            port_name: 串口号 (如 COM1)
            baud_rate: 波特率
            parity: 校验位 (QSerialPort枚举值)
            stop_bits: 停止位 (QSerialPort枚举值)
            
        返回:
            True表示打开成功，False表示失败
        """
        # 关闭已打开的串口
        if self.serial.isOpen():
            self.serial.close()

        # 配置串口参数
        self.serial.setPortName(port_name)
        self.serial.setBaudRate(baud_rate)
        self.serial.setDataBits(QSerialPort.Data8)
        self.serial.setParity(parity)
        self.serial.setStopBits(stop_bits)
        self.serial.setFlowControl(QSerialPort.NoFlowControl)

        # 尝试打开串口
        return self.serial.open(QSerialPort.ReadWrite)

    def close(self):
        """关闭串口"""
        if self.serial.isOpen():
            self.serial.close()

    def write(self, data: bytes) -> int:
        """
        向串口写入数据
        
        参数:
            data: 要写入的字节数据
            
        返回:
            实际写入的字节数，-1表示失败
        """
        return self.serial.write(data)

    def read_all(self) -> bytes:
        """读取所有可用的串口数据"""
        return bytes(self.serial.readAll())

    def wait_for_bytes_written(self, timeout_ms: int) -> bool:
        """等待数据写入完成"""
        return self.serial.waitForBytesWritten(timeout_ms)

    def wait_for_ready_read(self, timeout_ms: int) -> bool:
        """等待有数据可读"""
        return self.serial.waitForReadyRead(timeout_ms)

    def get_error_string(self) -> str:
        """获取最后一次错误的描述"""
        return self.serial.errorString()

    def clear_read_buffer(self):
        """清空读取缓冲区"""
        self.read_all()
