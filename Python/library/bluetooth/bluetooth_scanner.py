"""
蓝牙扫描服务
使用系统蓝牙栈扫描周围设备，并收集名称、设备ID和RSSI
"""

try:
    from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothLocalDevice, QBluetoothAddress
    from PySide6.QtCore import QObject, Signal, Slot, QTimer
    BLUETOOTH_AVAILABLE = True
except ImportError:  # pragma: no cover - 运行环境缺少QtBluetooth时优雅降级
    from PySide6.QtCore import QObject, Signal, Slot, QTimer
    QBluetoothDeviceDiscoveryAgent = None
    QBluetoothLocalDevice = None
    QBluetoothAddress = None
    BLUETOOTH_AVAILABLE = False


class BluetoothScanner(QObject):
    """系统蓝牙扫描器。"""

    devicesChanged = Signal()
    scanningChanged = Signal()
    statusChanged = Signal()
    supportedChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._supported = BLUETOOTH_AVAILABLE
        self._scanning = False
        self._status = ""
        self._devices = []
        self._device_map = {}
        self._device_info_map = {}
        self._pending_updates = {}

        self._agent = None
        self._local_device = None
        self._flush_timer = QTimer(self)
        self._flush_timer.setSingleShot(True)
        self._flush_timer.setInterval(120)
        self._flush_timer.timeout.connect(self._flush_pending_updates)

        if self._supported:
            try:
                self._local_device = QBluetoothLocalDevice(self)
            except Exception:
                self._local_device = None
            self._agent = QBluetoothDeviceDiscoveryAgent(self)
            try:
                self._agent.setLowEnergyDiscoveryTimeout(40000)
            except Exception:
                pass
            self._agent.deviceDiscovered.connect(self._on_device_discovered)
            try:
                self._agent.deviceUpdated.connect(self._on_device_updated)
            except Exception:
                pass
            self._agent.finished.connect(self._on_finished)
            self._agent.canceled.connect(self._on_canceled)
            try:
                self._agent.errorOccurred.connect(self._on_error)
            except Exception:
                pass

    @property
    def supported(self):
        return self._supported

    @property
    def scanning(self):
        return self._scanning

    @property
    def status(self):
        return self._status

    @property
    def devices(self):
        return list(self._devices)

    def devices_as_display_list(self):
        return list(self._devices)

    def set_status(self, text):
        text = str(text)
        if text != self._status:
            self._status = text
            self.statusChanged.emit()

    def _set_scanning(self, scanning):
        scanning = bool(scanning)
        if self._scanning == scanning:
            return
        self._scanning = scanning
        self.scanningChanged.emit()

    def _set_supported(self, supported):
        supported = bool(supported)
        if self._supported == supported:
            return
        self._supported = supported
        self.supportedChanged.emit()

    def _set_devices(self, devices):
        self._devices = devices
        self.devicesChanged.emit()

    @Slot()
    def start_scan(self):
        """开始扫描蓝牙设备。"""
        if not self._supported:
            self.set_status("当前环境不支持 QtBluetooth，无法扫描蓝牙设备")
            return False

        if self._local_device is not None:
            try:
                if not self._local_device.isValid():
                    self.set_status("未检测到可用的本地蓝牙适配器")
                    return False
                if self._local_device.hostMode() == QBluetoothLocalDevice.HostMode.HostPoweredOff:
                    self.set_status("系统蓝牙处于关闭状态，请先打开蓝牙后再扫描")
                    return False
            except Exception:
                pass

        if self._agent.isActive():
            self._agent.stop()

        self._device_map = {}
        self._device_info_map = {}
        self._pending_updates = {}
        self._set_devices([])
        self.set_status("正在扫描周围蓝牙设备...")
        self._set_scanning(True)

        try:
            methods = QBluetoothDeviceDiscoveryAgent.supportedDiscoveryMethods()
            if methods and methods != QBluetoothDeviceDiscoveryAgent.DiscoveryMethod.NoMethod:
                self._agent.start(methods)
            else:
                self._agent.start()
        except Exception:
            self._agent.start()
        return True

    @Slot()
    def stop_scan(self):
        """停止扫描。"""
        if self._agent and self._agent.isActive():
            self._agent.stop()
        self._set_scanning(False)

    @Slot()
    def clear_devices(self):
        """清空设备列表。"""
        self._device_map = {}
        self._device_info_map = {}
        self._pending_updates = {}
        self._set_devices([])
        self.set_status("蓝牙设备列表已清空")

    def _format_rssi(self, rssi):
        if isinstance(rssi, int) and rssi != 127:
            return f"{rssi} dBm"
        return "未知"

    def _format_device(self, name, device_id, rssi):
        name = name or "未知设备"
        device_id = device_id or "未知ID"
        rssi_text = self._format_rssi(rssi)
        return f"{name} | Device id: {device_id} | RSSI: {rssi_text}"

    def _device_identifier(self, info, name, device_id):
        if device_id:
            return device_id
        try:
            uuid = info.deviceUuid()
            if hasattr(uuid, "isNull") and not uuid.isNull():
                return str(uuid.toString())
        except Exception:
            pass
        return name or "unknown"

    def _extract_uuid(self, info):
        try:
            service_uuids = info.serviceUuids()
            if service_uuids:
                first = service_uuids[0]
                text = str(first.toString()) if hasattr(first, "toString") else str(first)
                if text:
                    return text
        except Exception:
            pass

        try:
            uuid = info.deviceUuid()
            if hasattr(uuid, "isNull") and not uuid.isNull():
                return str(uuid.toString())
        except Exception:
            pass
        return "null"

    def _build_device_payload(self, info, name, device_id, rssi):
        return {
            "name": name or "未知设备",
            "device_id": device_id or "未知ID",
            "uuid": self._extract_uuid(info),
            "rssi": rssi,
            "rssi_text": self._format_rssi(rssi),
            "is_cached": bool(getattr(info, "isCached", lambda: False)()),
            "core_configurations": str(getattr(info, "coreConfigurations", lambda: "")()),
            "display": self._format_device(name, device_id, rssi),
        }

    def _sort_devices(self, devices):
        def score(item):
            rssi = item.get("rssi", 127)
            if not isinstance(rssi, int) or rssi == 127:
                return -999
            return rssi

        return sorted(devices, key=score, reverse=True)

    def _queue_device_update(self, key, payload):
        self._pending_updates[key] = payload
        if not self._flush_timer.isActive():
            self._flush_timer.start()

    def _flush_pending_updates(self):
        if not self._pending_updates:
            return

        self._device_map.update(self._pending_updates)
        self._pending_updates.clear()
        self._set_devices(self._sort_devices(list(self._device_map.values())))

    def _add_or_update_device(self, info, name, device_id, rssi):
        identifier = self._device_identifier(info, name, device_id)
        key = identifier or name or "unknown"
        self._device_info_map[key] = info
        payload = self._build_device_payload(info, name, device_id, rssi)
        payload["identifier"] = identifier
        self._queue_device_update(key, payload)

    def find_device_payload(self, device_id, device_name=""):
        did = str(device_id or "")
        dname = str(device_name or "")
        for item in self._devices:
            if str(item.get("device_id", "")) == did and did:
                return item
            if dname and str(item.get("name", "")) == dname:
                return item
        return None

    def find_device_info(self, device_id, device_name=""):
        payload = self.find_device_payload(device_id, device_name)
        if not payload:
            return None
        key = payload.get("identifier")
        return self._device_info_map.get(key)

    def try_pair_device(self, device_id):
        if self._local_device is None or QBluetoothLocalDevice is None:
            return False
        did = str(device_id or "")
        if ":" not in did:
            return False
        try:
            addr = QBluetoothAddress(did)
            self._local_device.requestPairing(addr, QBluetoothLocalDevice.Pairing.Paired)
            return True
        except Exception:
            return False

    @Slot(object)
    def _on_device_discovered(self, info):
        name = ""
        device_id = ""
        rssi = 127

        try:
            name = info.name()
        except Exception:
            pass

        try:
            device_id = info.address().toString()
        except Exception:
            pass

        try:
            rssi = int(info.rssi())
        except Exception:
            rssi = 127

        self._add_or_update_device(info, name, device_id, rssi)

    @Slot(object, object)
    def _on_device_updated(self, info, updated_fields):
        try:
            name = info.name()
        except Exception:
            name = ""

        try:
            device_id = info.address().toString()
        except Exception:
            device_id = ""

        try:
            rssi = int(info.rssi())
        except Exception:
            rssi = 127

        self._add_or_update_device(info, name, device_id, rssi)

    @Slot()
    def _on_finished(self):
        if self._flush_timer.isActive():
            self._flush_timer.stop()
        self._flush_pending_updates()

        try:
            cached_devices = list(self._agent.discoveredDevices()) if self._agent else []
            for info in cached_devices:
                self._on_device_discovered(info)
            if self._flush_timer.isActive():
                self._flush_timer.stop()
            self._flush_pending_updates()
        except Exception:
            pass

        if self._devices:
            self.set_status(f"蓝牙扫描完成，发现 {len(self._devices)} 个设备")
        else:
            self.set_status("蓝牙扫描完成，但未发现设备。请确认附近设备处于可发现状态")
        self._set_scanning(False)

    @Slot()
    def _on_canceled(self):
        self.set_status("蓝牙扫描已取消")
        self._set_scanning(False)

    @Slot(object)
    def _on_error(self, error):
        error_text = str(error)
        if self._agent is not None:
            try:
                error_text = self._agent.errorString() or error_text
            except Exception:
                pass
        self.set_status(f"蓝牙扫描失败: {error_text}")
        self._set_scanning(False)
