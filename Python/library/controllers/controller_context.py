"""
控制器上下文接口
用于隔离控制器与SerialConfig内部字段，降低隐式耦合
"""


class ControllerContext:
    """为子控制器提供统一的状态与服务访问接口。"""

    def __init__(self, owner):
        self._owner = owner

    @property
    def serial(self):
        return self._owner._serial

    @property
    def serial_service(self):
        return self._owner._serial_service

    @property
    def data_handler(self):
        return self._owner._data_handler

    @property
    def port_manager(self):
        return self._owner._port_manager

    @property
    def receive_text_service(self):
        return self._owner._receive_text_service

    @property
    def modbus_command_service(self):
        return self._owner._modbus_command_service

    @property
    def modbus_protocol(self):
        return self._owner._modbus_protocol

    @property
    def modbus_scanner(self):
        return self._owner._modbus_scanner

    @property
    def modbus_timeout_timer(self):
        return self._owner._modbus_timeout_timer

    @property
    def available_ports(self):
        return self._owner._available_ports

    @available_ports.setter
    def available_ports(self, value):
        self._owner._available_ports = value

    @property
    def raw_port_names(self):
        return self._owner._raw_port_names

    @raw_port_names.setter
    def raw_port_names(self, value):
        self._owner._raw_port_names = value

    @property
    def serial_open(self):
        return self._owner._serial_open

    @serial_open.setter
    def serial_open(self, value):
        self._owner._serial_open = bool(value)

    @property
    def receive_hex_mode(self):
        return self._owner._receive_hex_mode

    @receive_hex_mode.setter
    def receive_hex_mode(self, value):
        self._owner._receive_hex_mode = bool(value)

    @property
    def send_hex_mode(self):
        return self._owner._send_hex_mode

    @send_hex_mode.setter
    def send_hex_mode(self, value):
        self._owner._send_hex_mode = bool(value)

    @property
    def timestamp_enabled(self):
        return self._owner._timestamp_enabled

    @timestamp_enabled.setter
    def timestamp_enabled(self, value):
        self._owner._timestamp_enabled = bool(value)

    @property
    def modbus_mode(self):
        return self._owner._modbus_mode

    @modbus_mode.setter
    def modbus_mode(self, value):
        self._owner._modbus_mode = bool(value)

    @property
    def modbus_rx_buffer(self):
        return self._owner._modbus_rx_buffer

    @modbus_rx_buffer.setter
    def modbus_rx_buffer(self, value):
        self._owner._modbus_rx_buffer = value

    @property
    def modbus_query_timeout_ms(self):
        return self._owner._modbus_query_timeout_ms

    @modbus_query_timeout_ms.setter
    def modbus_query_timeout_ms(self, value):
        self._owner._modbus_query_timeout_ms = int(value)

    @property
    def received_text(self):
        return self._owner._received_text

    @received_text.setter
    def received_text(self, value):
        self._owner._received_text = value

    @property
    def has_available_ports(self):
        return self._owner.hasAvailablePorts

    @property
    def bluetooth_devices(self):
        return self._owner._bluetooth_devices

    @bluetooth_devices.setter
    def bluetooth_devices(self, value):
        self._owner._bluetooth_devices = list(value)
        if self._owner._bluetooth_devices_model is not None:
            self._owner._bluetooth_devices_model.set_devices(self._owner._bluetooth_devices)

    @property
    def bluetooth_status(self):
        return self._owner._bluetooth_status

    @bluetooth_status.setter
    def bluetooth_status(self, value):
        self._owner._bluetooth_status = str(value)

    @property
    def bluetooth_scanning(self):
        return self._owner._bluetooth_scanning

    @bluetooth_scanning.setter
    def bluetooth_scanning(self, value):
        self._owner._bluetooth_scanning = bool(value)

    @property
    def bluetooth_supported(self):
        return self._owner._bluetooth_supported

    @bluetooth_supported.setter
    def bluetooth_supported(self, value):
        self._owner._bluetooth_supported = bool(value)

    @property
    def bluetooth_link_connected(self):
        return self._owner._bluetooth_link_connected

    @bluetooth_link_connected.setter
    def bluetooth_link_connected(self, value):
        self._owner._bluetooth_link_connected = bool(value)

    @property
    def bluetooth_link_device_name(self):
        return self._owner._bluetooth_link_device_name

    @bluetooth_link_device_name.setter
    def bluetooth_link_device_name(self, value):
        self._owner._bluetooth_link_device_name = str(value or "")

    @property
    def bluetooth_link_connecting(self):
        return self._owner._bluetooth_link_connecting

    @bluetooth_link_connecting.setter
    def bluetooth_link_connecting(self, value):
        self._owner._bluetooth_link_connecting = bool(value)

    @property
    def bluetooth_connection_service(self):
        return self._owner._bluetooth_connection_service

    def set_status(self, text):
        self._owner._set_status(text)

    def emit_available_ports_changed(self):
        self._owner.availablePortsChanged.emit()

    def emit_serial_open_changed(self):
        self._owner.serialOpenChanged.emit()

    def emit_received_text_changed(self):
        self._owner.receivedTextChanged.emit()

    def emit_modbus_scan_active_changed(self):
        self._owner.modbusScanActiveChanged.emit()

    def emit_bluetooth_devices_changed(self):
        self._owner.bluetoothDevicesChanged.emit()

    def emit_bluetooth_scanning_changed(self):
        self._owner.bluetoothScanningChanged.emit()

    def emit_bluetooth_status_changed(self):
        self._owner.bluetoothStatusChanged.emit()

    def emit_bluetooth_supported_changed(self):
        self._owner.bluetoothSupportedChanged.emit()

    def emit_bluetooth_link_connected_changed(self):
        self._owner.bluetoothLinkConnectedChanged.emit()
