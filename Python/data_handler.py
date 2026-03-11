"""
数据编码/解码和格式转换模块
"""

import codecs
from datetime import datetime


class DataHandler:
    """处理数据的编码、解码和格式转换"""

    def __init__(self, encoding="UTF-8"):
        """初始化数据处理器"""
        self.encoding = encoding
        self._rx_decoder = codecs.getincrementaldecoder(encoding)(errors="replace")

    def set_encoding(self, encoding):
        """设置编码格式"""
        try:
            codecs.lookup(encoding)
        except LookupError:
            encoding = "UTF-8"
        self.encoding = encoding
        self._reset_decoder()

    def _reset_decoder(self):
        """重置增量解码器，清除缓冲区状态"""
        self._rx_decoder = codecs.getincrementaldecoder(self.encoding)(errors="replace")

    def decode_raw_data(self, raw_data):
        """
        将原始字节解码为字符串
        使用增量解码器处理可能的不完整字符序列
        """
        return self._rx_decoder.decode(raw_data)

    def build_send_payload(self, text, hex_mode=False):
        """
        构建发送数据负载
        
        参数:
            text: 输入文本或HEX字符串
            hex_mode: 是否为HEX模式
            
        返回:
            bytes对象或None（如果格式错误）
        """
        if hex_mode:
            return self._parse_hex_string(text)
        else:
            return self._encode_text(text)

    def _parse_hex_string(self, text):
        """
        解析HEX字符串，支持多种格式
        支持: "01 03 00 00", "0x01,0x03", etc.
        返回None表示格式错误
        """
        normalized = (
            text.replace("\n", " ")
            .replace("\r", " ")
            .replace(",", " ")
            .replace("\t", " ")
        )
        # 支持 "0x01 0x03" 格式
        normalized = normalized.replace("0x", " ").replace("0X", " ")
        normalized = " ".join(normalized.split())
        
        if not normalized:
            return None

        try:
            return bytes.fromhex(normalized)
        except ValueError:
            return None

    def _encode_text(self, text):
        """将文本编码为字节"""
        try:
            return text.encode(self.encoding, errors="replace")
        except LookupError:
            # 编码无效时回退到 UTF-8
            return text.encode("utf-8", errors="replace")

    @staticmethod
    def format_received_data(raw_data, hex_mode=False, timestamp_enabled=False):
        """
        格式化接收到的数据用于显示
        
        参数:
            raw_data: 原始接收数据
            hex_mode: 是否以HEX模式显示
            timestamp_enabled: 是否添加时间戳
        """
        ts = DataHandler._get_timestamp() if timestamp_enabled else ""
        
        if hex_mode:
            return ts + " ".join(f"{byte:02X}" for byte in raw_data)
        
        return ts + raw_data

    @staticmethod
    def _get_timestamp():
        """生成时间戳字符串 [HH:MM:SS.mmm]"""
        return datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "] "

    @staticmethod
    def add_timestamp_to_lines(text, include_timestamp=True):
        """
        为多行文本的每一行添加时间戳
        """
        if not include_timestamp:
            return text
        
        ts = DataHandler._get_timestamp()
        lines = text.split("\n")
        result = []
        
        for line in lines:
            if line:  # 非空行才添加时间戳
                result.append(ts + line)
            else:
                result.append("")
        
        return "\n".join(result)
