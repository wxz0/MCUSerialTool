"""
蓝牙连接服务
负责设备连接、断开和数据收发（优先 BLE，兼容 RFCOMM）
"""

try:
    from PySide6.QtCore import QObject, Signal, Slot, QByteArray
    from PySide6.QtBluetooth import (
        QBluetoothAddress,
        QBluetoothSocket,
        QBluetoothUuid,
        QBluetoothServiceInfo,
        QLowEnergyController,
        QLowEnergyService,
        QLowEnergyCharacteristic,
    )
    BLUETOOTH_CONNECT_AVAILABLE = True
except ImportError:  # pragma: no cover
    from PySide6.QtCore import QObject, Signal, Slot, QByteArray

    QBluetoothAddress = None
    QBluetoothSocket = None
    QBluetoothUuid = None
    QBluetoothServiceInfo = None
    QLowEnergyController = None
    QLowEnergyService = None
    QLowEnergyCharacteristic = None
    BLUETOOTH_CONNECT_AVAILABLE = False


class BluetoothConnectionService(QObject):
    """蓝牙连接和通信服务。"""

    dataReceived = Signal(bytes)
    statusChanged = Signal()
    connectedChanged = Signal()
    connectingChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._supported = BLUETOOTH_CONNECT_AVAILABLE
        self._connected = False
        self._connecting = False
        self._status = ""
        self._connected_device_name = ""
        self._mode = ""

        self._socket = None
        self._controller = None
        self._service = None
        self._write_char = None
        self._service_uuids = []

    @property
    def supported(self):
        return self._supported

    @property
    def connected(self):
        return self._connected

    @property
    def connecting(self):
        return self._connecting

    @property
    def status(self):
        return self._status

    @property
    def connected_device_name(self):
        return self._connected_device_name

    def _set_status(self, text):
        text = str(text)
        if text != self._status:
            self._status = text
            self.statusChanged.emit()

    def _set_connected(self, connected, device_name=""):
        connected = bool(connected)
        if self._connected != connected or self._connected_device_name != device_name:
            self._connected = connected
            self._connected_device_name = device_name if connected else ""
            self.connectedChanged.emit()

    def _set_connecting(self, connecting):
        connecting = bool(connecting)
        if self._connecting != connecting:
            self._connecting = connecting
            self.connectingChanged.emit()

    def disconnect(self):
        if self._socket is not None:
            try:
                self._socket.abort()
                self._socket.close()
            except Exception:
                pass
            self._socket = None

        if self._service is not None:
            try:
                self._service.deleteLater()
            except Exception:
                pass
            self._service = None

        if self._controller is not None:
            try:
                self._controller.disconnectFromDevice()
                self._controller.deleteLater()
            except Exception:
                pass
            self._controller = None

        self._write_char = None
        self._mode = ""
        self._service_uuids = []
        self._set_connecting(False)
        self._set_connected(False)

    def _is_le_device(self, device_info):
        if device_info is None:
            return False
        try:
            configs = device_info.coreConfigurations()
            le = int(QLowEnergyController.RemoteAddressType.PublicAddress)  # dummy usage for lint happiness
            _ = le
            # Qt 枚举在 Python 下是 Flag，可直接按位判断
            return bool(configs & device_info.CoreConfiguration.LowEnergyCoreConfiguration) or bool(
                configs & device_info.CoreConfiguration.BaseRateAndLowEnergyCoreConfiguration
            )
        except Exception:
            return True

    def connect_device(self, device_info, device_name, device_id):
        if not self._supported:
            self._set_status("当前环境不支持蓝牙连接")
            return False

        self.disconnect()
        self._set_connecting(True)

        if device_info is not None and self._is_le_device(device_info):
            return self._connect_le(device_info, device_name)

        # 回退 RFCOMM（经典蓝牙）
        return self._connect_rfcomm(device_id, device_name)

    def _connect_rfcomm(self, device_id, device_name):
        if QBluetoothSocket is None or QBluetoothAddress is None or QBluetoothUuid is None:
            self._set_status("RFCOMM 连接不可用")
            return False

        if not device_id or ":" not in str(device_id):
            self._set_status("设备地址不是经典蓝牙 MAC，无法 RFCOMM 连接")
            self._set_connecting(False)
            return False

        try:
            address = QBluetoothAddress(str(device_id))
            socket = QBluetoothSocket(QBluetoothServiceInfo.Protocol.RfcommProtocol, self)
            socket.connected.connect(self._on_rfcomm_connected)
            socket.disconnected.connect(self._on_rfcomm_disconnected)
            socket.readyRead.connect(self._on_rfcomm_ready_read)
            try:
                socket.errorOccurred.connect(self._on_rfcomm_error)
            except Exception:
                pass

            uuid = QBluetoothUuid(QBluetoothUuid.ServiceClassUuid.SerialPort)
            socket.connectToService(address, uuid)
            self._socket = socket
            self._mode = "rfcomm"
            self._connected_device_name = str(device_name or "未知设备")
            self._set_status(f"正在通过 RFCOMM 连接 {self._connected_device_name}...")
            return True
        except Exception as exc:
            self._set_status(f"RFCOMM 连接失败: {exc}")
            self._set_connecting(False)
            return False

    def _connect_le(self, device_info, device_name):
        if QLowEnergyController is None:
            self._set_status("BLE 连接不可用")
            self._set_connecting(False)
            return False

        try:
            controller = QLowEnergyController.createCentral(device_info, self)
            controller.connected.connect(self._on_le_connected)
            controller.disconnected.connect(self._on_le_disconnected)
            controller.serviceDiscovered.connect(self._on_le_service_discovered)
            controller.discoveryFinished.connect(self._on_le_service_discovery_finished)
            try:
                controller.errorOccurred.connect(self._on_le_error)
            except Exception:
                pass

            self._controller = controller
            self._mode = "ble"
            self._service_uuids = []
            self._connected_device_name = str(device_name or "未知设备")
            self._set_status(f"正在连接 BLE 设备 {self._connected_device_name}...")
            controller.connectToDevice()
            return True
        except Exception as exc:
            self._set_status(f"BLE 连接失败: {exc}")
            self._set_connecting(False)
            return False

    @Slot()
    def _on_rfcomm_connected(self):
        self._set_connecting(False)
        self._set_connected(True, self._connected_device_name)
        self._set_status(f"已连接 RFCOMM: {self._connected_device_name}")

    @Slot()
    def _on_rfcomm_disconnected(self):
        self._set_connecting(False)
        self._set_connected(False)
        self._set_status("RFCOMM 连接已断开")

    @Slot()
    def _on_rfcomm_ready_read(self):
        if self._socket is None:
            return
        try:
            data = bytes(self._socket.readAll())
            if data:
                self.dataReceived.emit(data)
        except Exception:
            pass

    @Slot(object)
    def _on_rfcomm_error(self, error):
        self._set_status(f"RFCOMM 错误: {error}")
        self._set_connecting(False)

    @Slot()
    def _on_le_connected(self):
        if self._controller is None:
            return
        self._set_status(f"BLE 已连接，正在发现服务: {self._connected_device_name}")
        self._controller.discoverServices()

    @Slot()
    def _on_le_disconnected(self):
        self._set_connecting(False)
        self._set_connected(False)
        self._set_status("BLE 连接已断开")

    @Slot(object)
    def _on_le_service_discovered(self, service_uuid):
        self._service_uuids.append(service_uuid)

    @Slot()
    def _on_le_service_discovery_finished(self):
        if not self._service_uuids:
            self._set_status("BLE 未发现可用服务")
            self._set_connecting(False)
            return

        target_uuid = None
        for service_uuid in self._service_uuids:
            text = str(service_uuid).lower()
            if "fff0" in text or "ffe0" in text:
                target_uuid = service_uuid
                break

        if target_uuid is None:
            target_uuid = self._service_uuids[0]

        try:
            self._service = self._controller.createServiceObject(target_uuid, self)
            if self._service is None:
                self._set_status("BLE 服务对象创建失败")
                self._set_connecting(False)
                return

            self._service.stateChanged.connect(self._on_le_service_state_changed)
            self._service.characteristicChanged.connect(self._on_le_characteristic_changed)
            try:
                self._service.errorOccurred.connect(self._on_le_service_error)
            except Exception:
                pass
            self._service.discoverDetails()
            self._set_status("BLE 正在发现特征...")
        except Exception as exc:
            self._set_status(f"BLE 服务连接失败: {exc}")
            self._set_connecting(False)

    @Slot(object)
    def _on_le_service_state_changed(self, state):
        if QLowEnergyService is None:
            return

        if state != QLowEnergyService.ServiceState.ServiceDiscovered:
            return

        chars = self._service.characteristics()
        write_char = None

        for ch in chars:
            props = ch.properties()
            try:
                if props & QLowEnergyCharacteristic.PropertyType.WriteNoResponse:
                    write_char = ch
                    break
                if props & QLowEnergyCharacteristic.PropertyType.Write:
                    write_char = ch
            except Exception:
                continue

        self._write_char = write_char

        # 开启可通知特征
        for ch in chars:
            try:
                props = ch.properties()
                if not (props & QLowEnergyCharacteristic.PropertyType.Notify):
                    continue
                cccd = ch.descriptor(QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration)
                if cccd.isValid():
                    self._service.writeDescriptor(cccd, bytes([0x01, 0x00]))
            except Exception:
                pass

        if self._write_char is None:
            self._set_status("BLE 未找到可写特征，无法通信")
            self._set_connecting(False)
            return

        self._set_connecting(False)
        self._set_connected(True, self._connected_device_name)
        self._set_status(f"BLE 已连接: {self._connected_device_name}")

    @Slot(object, object)
    def _on_le_characteristic_changed(self, characteristic, value):
        _ = characteristic
        try:
            data = bytes(value)
            if data:
                self.dataReceived.emit(data)
        except Exception:
            pass

    @Slot(object)
    def _on_le_error(self, error):
        self._set_status(f"BLE 控制器错误: {error}")
        self._set_connecting(False)

    @Slot(object)
    def _on_le_service_error(self, error):
        self._set_status(f"BLE 服务错误: {error}")
        self._set_connecting(False)

    def send(self, payload: bytes):
        if not payload:
            return False

        if not self._connected:
            self._set_status("蓝牙未连接，无法发送")
            return False

        try:
            if self._mode == "rfcomm" and self._socket is not None:
                written = self._socket.write(payload)
                if written <= 0:
                    self._set_status("RFCOMM 发送失败")
                    return False
                return True

            if self._mode == "ble" and self._service is not None and self._write_char is not None:
                props = self._write_char.properties()
                mode = QLowEnergyService.WriteMode.WriteWithResponse
                try:
                    if props & QLowEnergyCharacteristic.PropertyType.WriteNoResponse:
                        mode = QLowEnergyService.WriteMode.WriteWithoutResponse
                except Exception:
                    pass
                self._service.writeCharacteristic(self._write_char, QByteArray(payload), mode)
                return True

            self._set_status("当前蓝牙连接模式不支持发送")
            return False
        except Exception as exc:
            self._set_status(f"蓝牙发送异常: {exc}")
            return False
