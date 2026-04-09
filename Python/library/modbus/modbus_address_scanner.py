"""
Modbus地址扫描状态机模块
负责非阻塞扫描地址 1..247，并通过信号通知状态变化与结果
"""

from PySide6.QtCore import QObject, QTimer, Signal, Slot


class ModbusAddressScanner(QObject):
    """非阻塞Modbus地址扫描器。"""

    activeChanged = Signal()
    scanFinished = Signal(str, int)

    def __init__(self, port_manager, modbus_protocol, parent=None):
        super().__init__(parent)
        self._port_manager = port_manager
        self._modbus_protocol = modbus_protocol

        self._active = False
        self._query_timeout_ms = 220
        self._register_addr = 0
        self._current_addr = 1
        self._waiting_addr = 0
        self._found = []
        self._buffer = b""

        self._step_timer = QTimer(self)
        self._step_timer.setSingleShot(True)
        self._step_timer.timeout.connect(self._on_step_timeout)

    @property
    def active(self):
        return self._active

    @property
    def query_timeout_ms(self):
        return self._query_timeout_ms

    def set_query_timeout(self, timeout_ms):
        """设置单地址扫描超时时间。"""
        try:
            value = int(timeout_ms)
        except (TypeError, ValueError):
            value = 220
        self._query_timeout_ms = max(20, min(value, 2000))

    def start(self, register_addr):
        """启动扫描，成功返回True。"""
        if self._active:
            return False

        self._register_addr = int(register_addr)
        self._current_addr = 1
        self._waiting_addr = 0
        self._found = []
        self._buffer = b""
        self._set_active(True)

        self._port_manager.clear_read_buffer()
        QTimer.singleShot(0, self._scan_next_address)
        return True

    def stop(self):
        """停止扫描并清理状态。"""
        self._step_timer.stop()
        self._waiting_addr = 0
        self._buffer = b""
        self._found = []
        self._set_active(False)

    def handle_ready_read(self, raw_data):
        """处理扫描期间的串口输入数据。"""
        if not self._active or self._waiting_addr == 0:
            return

        self._buffer += raw_data
        expected = self._modbus_protocol.expected_frame_length(self._buffer)
        if expected is None or len(self._buffer) < expected:
            return

        frame = self._buffer[:expected]
        if (self._modbus_protocol.is_valid_frame(frame)
                and frame[0] == self._waiting_addr
                and frame[1] == 0x03
                and len(frame) >= 7
                and frame[2] == 2):
            self._found.append(frame[0])

        self._advance()

    def _scan_next_address(self):
        """发送当前地址查询帧。"""
        if not self._active:
            return

        if self._current_addr > 247:
            self._finish()
            return

        addr = self._current_addr
        req = self._modbus_protocol.build_frame(addr, 0x03, self._register_addr, 1)
        if req is None:
            self._advance()
            return

        self._waiting_addr = addr
        self._buffer = b""
        self._port_manager.clear_read_buffer()
        sent = self._port_manager.write(req)
        if sent == -1:
            self._advance()
            return

        self._step_timer.start(self._query_timeout_ms)

    def _advance(self):
        """推进到下一地址。"""
        if not self._active:
            return

        self._step_timer.stop()
        self._waiting_addr = 0
        self._buffer = b""
        self._current_addr += 1
        QTimer.singleShot(0, self._scan_next_address)

    def _finish(self):
        """结束扫描并发出结果信号。"""
        found = self._found[:]
        reg = self._register_addr

        if found:
            result = f"寄存器地址 0x{reg:04X} 对应设备地址: {', '.join(map(str, found))}"
            hit_count = len(found)
        else:
            result = f"寄存器地址 0x{reg:04X} 未找到可响应设备"
            hit_count = 0

        self.stop()
        self.scanFinished.emit(result, hit_count)

    def _set_active(self, active):
        active = bool(active)
        if self._active == active:
            return
        self._active = active
        self.activeChanged.emit()

    @Slot()
    def _on_step_timeout(self):
        """单地址超时，自动推进。"""
        if self._active:
            self._advance()
