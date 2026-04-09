"""
蓝牙控制器模块
负责蓝牙扫描流程与上下文状态同步
"""


class BluetoothController:
    """蓝牙流程控制器，依赖上下文接口与扫描服务。"""

    def __init__(self, context, scanner):
        self._ctx = context
        self._scanner = scanner
        self._sync_from_scanner()

    def _sync_from_scanner(self):
        self._ctx.bluetooth_supported = self._scanner.supported
        self._ctx.bluetooth_scanning = self._scanner.scanning
        self._ctx.bluetooth_status = self._scanner.status
        self._ctx.bluetooth_devices = self._scanner.devices_as_display_list()
        self._ctx.emit_bluetooth_supported_changed()
        self._ctx.emit_bluetooth_scanning_changed()
        self._ctx.emit_bluetooth_status_changed()
        self._ctx.emit_bluetooth_devices_changed()

    def scan_devices(self):
        return self._scanner.start_scan()

    def stop_scan(self):
        self._scanner.stop_scan()

    def clear_devices(self):
        self._scanner.clear_devices()
        self.on_devices_changed()

    def on_devices_changed(self):
        devices = self._scanner.devices_as_display_list()
        self._ctx.bluetooth_devices = devices
        if self._ctx.bluetooth_scanning:
            self._ctx.bluetooth_status = f"正在扫描周围蓝牙设备... 已发现 {len(devices)} 个"
            self._ctx.emit_bluetooth_status_changed()
        self._ctx.emit_bluetooth_devices_changed()

    def on_scanning_changed(self):
        self._ctx.bluetooth_scanning = self._scanner.scanning
        self._ctx.emit_bluetooth_scanning_changed()

    def on_status_changed(self):
        self._ctx.bluetooth_status = self._scanner.status
        self._ctx.emit_bluetooth_status_changed()

    def on_supported_changed(self):
        self._ctx.bluetooth_supported = self._scanner.supported
        self._ctx.emit_bluetooth_supported_changed()

    def connect_device(self, device_id, device_name, device_uuid):
        _ = device_uuid
        name = str(device_name or "")
        did = str(device_id or "")

        info = self._scanner.find_device_info(did, name)
        payload = self._scanner.find_device_payload(did, name) or {}

        if not info and not payload:
            self._ctx.bluetooth_status = "未找到目标设备，请重新扫描后再点击连接"
            self._ctx.emit_bluetooth_status_changed()
            return False

        if "hc08" in name.lower() or "hc-08" in name.lower():
            self._ctx.bluetooth_status = f"正在连接 HC08: {name}"
        else:
            self._ctx.bluetooth_status = f"正在连接蓝牙设备: {name or did}"

        self._ctx.bluetooth_link_connecting = True

        if self._scanner.try_pair_device(did):
            self._ctx.bluetooth_status += "（已发起配对）"

        self._ctx.emit_bluetooth_status_changed()

        svc = self._ctx.bluetooth_connection_service
        ok = svc.connect_device(info, name or payload.get("name", ""), did or payload.get("device_id", ""))
        if not ok:
            self._ctx.bluetooth_status = svc.status
            self._ctx.bluetooth_link_connecting = False
            self._ctx.emit_bluetooth_status_changed()
        return ok

    def disconnect_device(self):
        svc = self._ctx.bluetooth_connection_service
        svc.disconnect()
        self._ctx.bluetooth_link_connected = False
        self._ctx.bluetooth_link_connecting = False
        self._ctx.bluetooth_link_device_name = ""
        self._ctx.emit_bluetooth_link_connected_changed()
