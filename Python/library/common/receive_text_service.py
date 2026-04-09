"""
接收文本拼装服务
封装普通文本、HEX以及Modbus结果文本的拼接逻辑
"""

from library.common.data_handler import DataHandler


class ReceiveTextService:
    """负责接收区文本格式化与拼接。"""

    def append_normal_data(self, current_text, raw_data, receive_hex_mode, timestamp_enabled, data_handler):
        """拼接普通模式接收数据并返回新文本。"""
        ts = DataHandler._get_timestamp() if timestamp_enabled else ""

        if receive_hex_mode:
            chunk = " ".join(f"{byte:02X}" for byte in raw_data)
            if current_text:
                return current_text + "\n" + ts + chunk
            return ts + chunk

        decoded = data_handler.decode_raw_data(raw_data)
        if not decoded:
            return current_text

        if not timestamp_enabled:
            return current_text + decoded

        lines = decoded.split("\n")
        stamped = []
        for i, line in enumerate(lines):
            if i == 0:
                if not current_text or current_text.endswith("\n"):
                    stamped.append(ts + line)
                else:
                    stamped.append(line)
            else:
                if i == len(lines) - 1 and line == "":
                    stamped.append("")
                else:
                    stamped.append(ts + line)

        return current_text + "\n".join(stamped)

    def append_modbus_scan_result(self, current_text, result, timestamp_enabled):
        """拼接Modbus地址扫描结果。"""
        ts = DataHandler._get_timestamp() if timestamp_enabled else ""
        prefix = "\n" if current_text else ""
        return current_text + f"{prefix}{ts}[Modbus地址查询] {result}"

    def append_modbus_parse_result(self, current_text, result, timestamp_enabled):
        """拼接Modbus解析结果行。"""
        ts = DataHandler._get_timestamp() if timestamp_enabled else ""
        return current_text + ts + result + "\n"

    def append_modbus_timeout(self, current_text, timestamp_enabled):
        """拼接Modbus超时提示行。"""
        ts = DataHandler._get_timestamp() if timestamp_enabled else ""
        return current_text + f"\n{ts}[Modbus] ⚠ 超时未收到从机回应\n"
