"""
串口控制器模块
负责串口刷新、开关、收发与普通数据处理
"""


class SerialController:
    """串口流程控制器，依赖上下文接口对象。"""

    def __init__(self, context):
        self._ctx = context

    def refresh_ports(self):
        self._refresh_ports_internal(status_on_no_change=True, source="manual")

    def auto_refresh_ports(self):
        self._refresh_ports_internal(status_on_no_change=False, source="auto")

    def _refresh_ports_internal(self, status_on_no_change, source):
        ports, raw_port_names = self._ctx.serial_service.get_available_ports()

        changed = ports != self._ctx.available_ports
        if changed:
            self._ctx.available_ports = ports
            self._ctx.raw_port_names = raw_port_names
            self._ctx.emit_available_ports_changed()

            # 如果已打开的串口被拔出，自动关闭
            if self._ctx.serial.isOpen() and self._ctx.serial.portName() not in self._ctx.raw_port_names:
                lost_port = self._ctx.serial.portName()
                self.close_serial()
                self._ctx.set_status(f"串口 {lost_port} 已断开，已自动关闭")

            if source == "auto":
                if self._ctx.has_available_ports:
                    self._ctx.set_status(f"检测到串口变化，已自动刷新（共 {len(ports)} 个）")
                else:
                    self._ctx.set_status("检测到串口变化，当前无可用串口")
                return

        if status_on_no_change or changed:
            if self._ctx.has_available_ports:
                self._ctx.set_status(f"已刷新串口列表，共 {len(ports)} 个")
            else:
                self._ctx.set_status("未检测到可用串口")

    def open_serial(self, port_text, baud_text, parity_text, stop_bits_text):
        success, status = self._ctx.serial_service.open_serial(
            port_text,
            baud_text,
            parity_text,
            stop_bits_text,
        )

        if not success:
            self._ctx.serial_open = False
            self._ctx.emit_serial_open_changed()
            self._ctx.set_status(status)
            return False

        self._ctx.serial_open = True
        self._ctx.emit_serial_open_changed()
        self._ctx.set_status(status)
        return True

    def close_serial(self):
        if self._ctx.modbus_scanner:
            self._ctx.modbus_scanner.stop()
        self._ctx.serial_service.close_serial()
        if self._ctx.serial_open:
            self._ctx.serial_open = False
            self._ctx.emit_serial_open_changed()
        self._ctx.set_status("串口已关闭")

    def toggle_serial(self, port_text, baud_text, parity_text, stop_bits_text):
        if self._ctx.serial.isOpen():
            self.close_serial()
        else:
            self.open_serial(port_text, baud_text, parity_text, stop_bits_text)

    def set_encoding(self, encoding):
        self._ctx.data_handler.set_encoding(encoding)

    def set_receive_hex_mode(self, enabled):
        self._ctx.receive_hex_mode = bool(enabled)
        self._ctx.data_handler._reset_decoder()

    def set_send_hex_mode(self, enabled):
        self._ctx.send_hex_mode = bool(enabled)

    def set_timestamp_enabled(self, enabled):
        self._ctx.timestamp_enabled = bool(enabled)

    def send_data(self, text):
        payload = self._ctx.data_handler.build_send_payload(text or "", self._ctx.send_hex_mode)
        if payload is None:
            self._ctx.set_status("HEX 发送格式错误，请输入如: 01 03 00 00 00 01 或 0x01,0x03,...")
            return False

        # 若蓝牙链路已连接，优先走蓝牙发送。
        bt = self._ctx.bluetooth_connection_service
        if bt is not None and self._ctx.bluetooth_link_connected:
            ok = bt.send(payload)
            if ok:
                self._ctx.set_status(f"蓝牙已发送 {len(payload)} 字节")
            else:
                self._ctx.set_status(bt.status or "蓝牙发送失败")
            return ok

        if not self._ctx.serial.isOpen():
            self._ctx.set_status("串口未打开，无法发送")
            return False

        sent_len = self._ctx.port_manager.write(payload)
        if sent_len == -1:
            self._ctx.set_status(f"发送失败: {self._ctx.port_manager.get_error_string()}")
            return False

        self._ctx.set_status(f"已发送 {sent_len} 字节")
        return True

    def clear_received_text(self):
        if self._ctx.received_text:
            self._ctx.received_text = ""
            self._ctx.emit_received_text_changed()
        self._ctx.data_handler._reset_decoder()

    def handle_normal_mode(self, raw_data):
        self._ctx.received_text = self._ctx.receive_text_service.append_normal_data(
            self._ctx.received_text,
            raw_data,
            self._ctx.receive_hex_mode,
            self._ctx.timestamp_enabled,
            self._ctx.data_handler,
        )
        self._ctx.emit_received_text_changed()

    def on_serial_error(self, error, resource_error_enum):
        if error == resource_error_enum and self._ctx.serial.isOpen():
            port_name = self._ctx.serial.portName()
            self.close_serial()
            self._ctx.set_status(f"串口 {port_name} 发生资源错误，已自动关闭")
