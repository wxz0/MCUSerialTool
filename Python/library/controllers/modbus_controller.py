"""
Modbus控制器模块
负责Modbus读写、扫描和响应处理
"""


class ModbusController:
    """Modbus流程控制器，依赖上下文接口对象。"""

    def __init__(self, context):
        self._ctx = context

    def set_modbus_mode(self, enabled):
        self._ctx.modbus_mode = bool(enabled)
        self._ctx.modbus_rx_buffer = b""
        if not enabled:
            self._ctx.modbus_timeout_timer.stop()
            if self._ctx.modbus_scanner:
                self._ctx.modbus_scanner.stop()

    def set_query_timeout(self, timeout_ms):
        try:
            value = int(timeout_ms)
        except (TypeError, ValueError):
            value = 220
        self._ctx.modbus_query_timeout_ms = max(20, min(value, 2000))
        if self._ctx.modbus_scanner:
            self._ctx.modbus_scanner.set_query_timeout(self._ctx.modbus_query_timeout_ms)

    def send_read_command(self, dev_addr_text, fc_text, start_addr_text, reg_len_text):
        if not self._ctx.serial.isOpen():
            self._ctx.set_status("串口未打开，无法发送 Modbus 命令")
            return ""

        frame, error = self._ctx.modbus_command_service.build_read_frame(
            dev_addr_text,
            fc_text,
            start_addr_text,
            reg_len_text,
        )
        if frame is None:
            self._ctx.set_status(error)
            return ""

        hex_str = " ".join(f"{b:02X}" for b in frame)
        sent = self._ctx.port_manager.write(frame)
        if sent == -1:
            self._ctx.set_status(f"发送失败: {self._ctx.port_manager.get_error_string()}")
            return ""

        self._ctx.modbus_rx_buffer = b""
        self._ctx.modbus_timeout_timer.start()
        self._ctx.set_status(f"已发送 Modbus 命令: {hex_str}")
        return hex_str

    def send_write_command(self, dev_addr_text, fc_text, register_addr_text, value_text):
        if not self._ctx.serial.isOpen():
            self._ctx.set_status("串口未打开，无法发送 Modbus 命令")
            return ""

        frame, fc, error = self._ctx.modbus_command_service.build_write_frame(
            dev_addr_text,
            fc_text,
            register_addr_text,
            value_text,
        )
        if frame is None:
            self._ctx.set_status(error)
            return ""

        hex_str = " ".join(f"{b:02X}" for b in frame)
        sent = self._ctx.port_manager.write(frame)
        if sent == -1:
            self._ctx.set_status(f"发送失败: {self._ctx.port_manager.get_error_string()}")
            return ""

        self._ctx.modbus_rx_buffer = b""
        self._ctx.modbus_timeout_timer.start()
        self._ctx.set_status(f"已发送 Modbus 写命令(FC={fc:02X}): {hex_str}")
        return hex_str

    def query_device_addresses(self, register_addr_text):
        if not self._ctx.serial.isOpen():
            self._ctx.set_status("串口未打开，无法执行地址查询")
            return ""

        if self._ctx.modbus_scanner and self._ctx.modbus_scanner.active:
            self._ctx.set_status("已有地址扫描任务在运行，请稍候")
            return ""

        try:
            register_addr = self._ctx.modbus_protocol.parse_hex_u16(register_addr_text)
        except (ValueError, TypeError):
            self._ctx.set_status("寄存器地址无效，请输入 HEX(0000-FFFF)")
            return ""

        self._ctx.set_status(
            f"开始扫描寄存器地址 0x{register_addr:04X}，正在后台查询，请耐心等待..."
        )
        self._ctx.modbus_timeout_timer.stop()
        if not self._ctx.modbus_scanner or not self._ctx.modbus_scanner.start(register_addr):
            self._ctx.set_status("启动地址扫描失败")
            return ""
        return "STARTED"

    def on_scan_active_changed(self):
        self._ctx.emit_modbus_scan_active_changed()

    def on_scan_finished(self, result, hit_count):
        if hit_count > 0:
            self._ctx.set_status(f"扫描完成，命中 {hit_count} 个设备")
        else:
            self._ctx.set_status("扫描完成，未找到设备")

        self._ctx.received_text = self._ctx.receive_text_service.append_modbus_scan_result(
            self._ctx.received_text,
            result,
            self._ctx.timestamp_enabled,
        )
        self._ctx.emit_received_text_changed()

    def handle_modbus_mode(self, raw_data):
        self._ctx.modbus_rx_buffer += raw_data
        result = self._try_parse_modbus(self._ctx.modbus_rx_buffer)
        if result is not None:
            self._ctx.modbus_timeout_timer.stop()
            self._ctx.modbus_rx_buffer = b""
            self._ctx.received_text = self._ctx.receive_text_service.append_modbus_parse_result(
                self._ctx.received_text,
                result,
                self._ctx.timestamp_enabled,
            )
            self._ctx.emit_received_text_changed()

    def on_modbus_timeout(self):
        self._ctx.modbus_rx_buffer = b""
        self._ctx.set_status("⚠ Modbus 通信失败：超时未收到从机回应")
        self._ctx.received_text = self._ctx.receive_text_service.append_modbus_timeout(
            self._ctx.received_text,
            self._ctx.timestamp_enabled,
        )
        self._ctx.emit_received_text_changed()

    def _try_parse_modbus(self, buf: bytes):
        expected = self._ctx.modbus_protocol.expected_frame_length(buf)
        if expected is None or len(buf) < expected:
            return None

        frame = buf[:expected]
        return self._ctx.modbus_protocol.parse_response(frame)
