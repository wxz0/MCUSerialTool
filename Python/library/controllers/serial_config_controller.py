"""
SerialConfig控制器模块
负责协调串口配置、数据传输和Modbus协议处理
"""

from PySide6.QtCore import Property, QObject, Signal, Slot, QTimer
from PySide6.QtSerialPort import QSerialPort

from library.serial.serial_config_parser import SerialConfigParser
from library.common.data_handler import DataHandler
from library.common.receive_text_service import ReceiveTextService
from library.modbus.modbus_protocol import ModbusProtocol
from library.serial.serial_port_manager import SerialPortManager
from library.serial.serial_service import SerialService
from library.modbus.modbus_address_scanner import ModbusAddressScanner
from library.modbus.modbus_command_service import ModbusCommandService
from library.bluetooth.bluetooth_scanner import BluetoothScanner
from library.bluetooth.bluetooth_device_list_model import BluetoothDeviceListModel
from library.bluetooth.bluetooth_connection_service import BluetoothConnectionService
from library.controllers.controller_context import ControllerContext
from library.controllers.serial_controller import SerialController
from library.controllers.modbus_controller import ModbusController
from library.controllers.bluetooth_controller import BluetoothController


class SerialConfig(QObject):
    """
    主控制类：协调串口配置、数据传输和Modbus协议处理
    使用模块化设计将具体功能委托给专用模块
    """

    availablePortsChanged = Signal()
    serialOpenChanged = Signal()
    serialStatusChanged = Signal()
    receivedTextChanged = Signal()
    modbusScanActiveChanged = Signal()
    bluetoothDevicesChanged = Signal()
    bluetoothScanningChanged = Signal()
    bluetoothStatusChanged = Signal()
    bluetoothSupportedChanged = Signal()
    bluetoothLinkConnectedChanged = Signal()
    bluetoothLinkConnectingChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initialize_properties()
        self._initialize_serial_port()
        self._initialize_timers()
        self._initialize_modules()

    def _initialize_properties(self):
        """初始化所有属性"""
        self._available_ports = []
        self._raw_port_names = []
        self._serial_open = False
        self._serial_status = "串口未打开"
        self._received_text = ""
        self._receive_hex_mode = False
        self._send_hex_mode = False
        self._timestamp_enabled = False
        self._modbus_mode = False
        self._modbus_rx_buffer = b""
        self._modbus_query_timeout_ms = 220
        self._modbus_scanner = None
        self._bluetooth_devices = []
        self._bluetooth_devices_model = None
        self._bluetooth_status = ""
        self._bluetooth_scanning = False
        self._bluetooth_supported = False
        self._bluetooth_link_connected = False
        self._bluetooth_link_connecting = False
        self._bluetooth_link_device_name = ""
        self._bluetooth_connection_service = None

    def _initialize_modules(self):
        """初始化各功能模块"""
        self._config_parser = SerialConfigParser()
        self._data_handler = DataHandler()
        self._modbus_protocol = ModbusProtocol()
        self._modbus_command_service = ModbusCommandService(self._modbus_protocol)
        self._port_manager = SerialPortManager(self._serial)
        self._serial_service = SerialService(self._config_parser, self._port_manager)
        self._receive_text_service = ReceiveTextService()
        self._modbus_scanner = ModbusAddressScanner(
            self._port_manager,
            self._modbus_protocol,
            self,
        )
        self._modbus_scanner.set_query_timeout(self._modbus_query_timeout_ms)
        self._modbus_scanner.activeChanged.connect(self._on_modbus_scan_active_changed)
        self._modbus_scanner.scanFinished.connect(self._on_modbus_scan_finished)
        self._bluetooth_devices_model = BluetoothDeviceListModel(self)
        self._bluetooth_connection_service = BluetoothConnectionService(self)
        self._controller_context = ControllerContext(self)
        self._serial_controller = SerialController(self._controller_context)
        self._modbus_controller = ModbusController(self._controller_context)
        self._bluetooth_scanner = BluetoothScanner(self)
        self._bluetooth_controller = BluetoothController(self._controller_context, self._bluetooth_scanner)
        self._bluetooth_scanner.devicesChanged.connect(self._on_bluetooth_devices_changed)
        self._bluetooth_scanner.scanningChanged.connect(self._on_bluetooth_scanning_changed)
        self._bluetooth_scanner.statusChanged.connect(self._on_bluetooth_status_changed)
        self._bluetooth_scanner.supportedChanged.connect(self._on_bluetooth_supported_changed)
        self._bluetooth_connection_service.dataReceived.connect(self._on_bluetooth_data_received)
        self._bluetooth_connection_service.statusChanged.connect(self._on_bluetooth_link_status_changed)
        self._bluetooth_connection_service.connectedChanged.connect(self._on_bluetooth_link_connected_changed)
        self._bluetooth_connection_service.connectingChanged.connect(self._on_bluetooth_link_connecting_changed)

    def _initialize_serial_port(self):
        """初始化串口对象和相关连接"""
        self._serial = QSerialPort(self)
        self._serial.errorOccurred.connect(self._on_serial_error)
        self._serial.readyRead.connect(self._on_ready_read)

    def _initialize_timers(self):
        """初始化定时器"""
        # Modbus超时定时器
        self._modbus_timeout_timer = QTimer(self)
        self._modbus_timeout_timer.setSingleShot(True)
        self._modbus_timeout_timer.setInterval(1000)
        self._modbus_timeout_timer.timeout.connect(self._on_modbus_timeout)

        # 串口监控定时器 (用于热拔插检测)
        self._port_monitor_timer = QTimer(self)
        self._port_monitor_timer.setInterval(1000)
        self._port_monitor_timer.timeout.connect(self._auto_refresh_ports)
        self._port_monitor_timer.start()

    # ============================================================
    # 属性定义 (Properties)
    # ============================================================

    @Property(bool, notify=serialOpenChanged)
    def serialOpen(self):
        return self._serial_open

    @Property(str, notify=serialStatusChanged)
    def serialStatus(self):
        return self._serial_status

    @Property(str, notify=receivedTextChanged)
    def receivedText(self):
        return self._received_text

    @Property(bool, notify=receivedTextChanged)
    def timestampEnabled(self):
        return self._timestamp_enabled

    @Property(bool, notify=modbusScanActiveChanged)
    def modbusScanActive(self):
        return bool(self._modbus_scanner and self._modbus_scanner.active)

    @Property(bool, notify=availablePortsChanged)
    def hasAvailablePorts(self):
        return bool(self._available_ports) and self._available_ports[0] != "无可用串口"

    @Property("QStringList", notify=availablePortsChanged)
    def availablePorts(self):
        return self._available_ports

    @Property("QStringList", constant=True)
    def baudRates(self):
        return self._config_parser.BAUD_RATES

    @Property("QStringList", constant=True)
    def parityOptions(self):
        return self._config_parser.PARITY_OPTIONS

    @Property("QStringList", constant=True)
    def stopBitsOptions(self):
        return self._config_parser.STOP_BITS_OPTIONS

    @Property("QStringList", constant=True)
    def encodingOptions(self):
        return ["UTF-8", "GBK", "GB2312", "ASCII", "Latin-1", "UTF-16"]

    @Property("QVariantList", notify=bluetoothDevicesChanged)
    def bluetoothDevices(self):
        return self._bluetooth_devices

    @Property(QObject, notify=bluetoothDevicesChanged)
    def bluetoothDevicesModel(self):
        return self._bluetooth_devices_model

    @Property(bool, notify=bluetoothScanningChanged)
    def bluetoothScanning(self):
        return self._bluetooth_scanning

    @Property(str, notify=bluetoothStatusChanged)
    def bluetoothStatus(self):
        return self._bluetooth_status

    @Property(bool, notify=bluetoothSupportedChanged)
    def bluetoothSupported(self):
        return self._bluetooth_supported

    @Property(bool, notify=bluetoothLinkConnectedChanged)
    def bluetoothLinkConnected(self):
        return self._bluetooth_link_connected

    @Property(str, notify=bluetoothLinkConnectedChanged)
    def bluetoothLinkDeviceName(self):
        return self._bluetooth_link_device_name

    @Property(bool, notify=bluetoothLinkConnectingChanged)
    def bluetoothLinkConnecting(self):
        return self._bluetooth_link_connecting

    # ============================================================
    # 串口操作 (Serial Operations)
    # ============================================================

    @Slot()
    def refreshPorts(self):
        """手动刷新串口列表"""
        self._serial_controller.refresh_ports()

    def _auto_refresh_ports(self):
        """自动刷新串口列表（由定时器触发）"""
        self._serial_controller.auto_refresh_ports()

    @Slot(str, str, str, str, result=bool)
    def openSerial(self, port_text, baud_text, parity_text, stop_bits_text):
        """打开串口"""
        return self._serial_controller.open_serial(port_text, baud_text, parity_text, stop_bits_text)

    @Slot()
    def closeSerial(self):
        """关闭串口"""
        self._serial_controller.close_serial()

    @Slot(str, str, str, str)
    def toggleSerial(self, port_text, baud_text, parity_text, stop_bits_text):
        """切换串口状态 (打开/关闭)"""
        self._serial_controller.toggle_serial(port_text, baud_text, parity_text, stop_bits_text)

    # ============================================================
    # 数据传输 (Data Transfer)
    # ============================================================

    @Slot(str)
    def setEncoding(self, encoding):
        """设置数据编码格式"""
        self._serial_controller.set_encoding(encoding)

    @Slot(bool)
    def setReceiveHexMode(self, enabled):
        """设置接收HEX模式"""
        self._serial_controller.set_receive_hex_mode(enabled)

    @Slot(bool)
    def setSendHexMode(self, enabled):
        """设置发送HEX模式"""
        self._serial_controller.set_send_hex_mode(enabled)

    @Slot(bool)
    def setTimestampEnabled(self, enabled):
        """启用/禁用时间戳"""
        self._serial_controller.set_timestamp_enabled(enabled)

    @Slot(str, result=bool)
    def sendData(self, text):
        """发送数据"""
        return self._serial_controller.send_data(text)

    @Slot()
    def clearReceivedText(self):
        """清空接收数据显示"""
        self._serial_controller.clear_received_text()

    # ============================================================
    # 蓝牙操作 (Bluetooth Operations)
    # ============================================================

    @Slot()
    def scanBluetoothDevices(self):
        return self._bluetooth_controller.scan_devices()

    @Slot()
    def stopBluetoothScan(self):
        self._bluetooth_controller.stop_scan()

    @Slot()
    def clearBluetoothDevices(self):
        self._bluetooth_controller.clear_devices()

    @Slot(str, str, str)
    def connectBluetoothDevice(self, device_id, device_name, device_uuid):
        self._bluetooth_controller.connect_device(device_id, device_name, device_uuid)

    @Slot()
    def disconnectBluetoothDevice(self):
        self._bluetooth_controller.disconnect_device()

    # ============================================================
    # Modbus操作 (Modbus Operations)
    # ============================================================

    @Slot(bool)
    def setModbusMode(self, enabled):
        """启用/禁用Modbus模式"""
        self._modbus_controller.set_modbus_mode(enabled)

    @Slot(int)
    def setModbusQueryTimeout(self, timeout_ms):
        """设置Modbus查询超时时间"""
        self._modbus_controller.set_query_timeout(timeout_ms)

    @Slot(str, str, str, str, result=str)
    def sendModbusReadCommand(self, dev_addr_text, fc_text, start_addr_text, reg_len_text):
        """发送Modbus读命令（01/02/03/04）"""
        return self._modbus_controller.send_read_command(
            dev_addr_text,
            fc_text,
            start_addr_text,
            reg_len_text,
        )

    @Slot(str, str, str, str, result=str)
    def sendModbusWriteCommand(self, dev_addr_text, fc_text, register_addr_text, value_text):
        """发送Modbus写命令（05/06/0F/10）"""
        return self._modbus_controller.send_write_command(
            dev_addr_text,
            fc_text,
            register_addr_text,
            value_text,
        )

    @Slot(str, result=str)
    def queryModbusDeviceAddresses(self, register_addr_text):
        """非阻塞扫描并查询Modbus设备地址"""
        return self._modbus_controller.query_device_addresses(register_addr_text)

    # ============================================================
    # 内部事件处理 (Internal Event Handlers)
    # ============================================================

    @Slot(QSerialPort.SerialPortError)
    def _on_serial_error(self, error):
        """处理串口错误"""
        self._serial_controller.on_serial_error(error, QSerialPort.ResourceError)

    @Slot()
    def _on_modbus_scan_active_changed(self):
        """转发扫描激活状态变化给QML。"""
        self._modbus_controller.on_scan_active_changed()

    @Slot(str, int)
    def _on_modbus_scan_finished(self, result, hit_count):
        """处理地址扫描结束回调。"""
        self._modbus_controller.on_scan_finished(result, hit_count)

    @Slot()
    def _on_ready_read(self):
        """处理串口数据可读事件"""
        raw_data = self._port_manager.read_all()
        if not raw_data:
            return

        if self._modbus_scanner and self._modbus_scanner.active:
            self._modbus_scanner.handle_ready_read(raw_data)
            return

        # 停止Modbus超时定时器（表示数据正在到达）
        if self._modbus_timeout_timer.isActive():
            self._modbus_timeout_timer.stop()

        # Modbus模式：累积并解析完整的RTU帧
        if self._modbus_mode:
            self._modbus_controller.handle_modbus_mode(raw_data)
            return

        # 普通模式：处理文本或HEX数据
        self._serial_controller.handle_normal_mode(raw_data)

    @Slot()
    def _on_modbus_timeout(self):
        """处理Modbus通信超时"""
        self._modbus_controller.on_modbus_timeout()

    @Slot()
    def _on_bluetooth_devices_changed(self):
        self._bluetooth_controller.on_devices_changed()

    @Slot()
    def _on_bluetooth_scanning_changed(self):
        self._bluetooth_controller.on_scanning_changed()

    @Slot()
    def _on_bluetooth_status_changed(self):
        self._bluetooth_controller.on_status_changed()

    @Slot()
    def _on_bluetooth_supported_changed(self):
        self._bluetooth_controller.on_supported_changed()

    @Slot(bytes)
    def _on_bluetooth_data_received(self, raw_data):
        if not raw_data:
            return
        self._received_text = self._receive_text_service.append_normal_data(
            self._received_text,
            raw_data,
            self._receive_hex_mode,
            self._timestamp_enabled,
            self._data_handler,
        )
        self.receivedTextChanged.emit()

    @Slot()
    def _on_bluetooth_link_status_changed(self):
        if self._bluetooth_connection_service is None:
            return
        self._bluetooth_status = self._bluetooth_connection_service.status
        self.bluetoothStatusChanged.emit()

    @Slot()
    def _on_bluetooth_link_connected_changed(self):
        if self._bluetooth_connection_service is None:
            return
        self._bluetooth_link_connected = self._bluetooth_connection_service.connected
        self._bluetooth_link_device_name = self._bluetooth_connection_service.connected_device_name
        self.bluetoothLinkConnectedChanged.emit()

    @Slot()
    def _on_bluetooth_link_connecting_changed(self):
        if self._bluetooth_connection_service is None:
            return
        self._bluetooth_link_connecting = self._bluetooth_connection_service.connecting
        self.bluetoothLinkConnectingChanged.emit()

    def _set_status(self, text):
        """更新状态消息"""
        if text != self._serial_status:
            self._serial_status = text
            self.serialStatusChanged.emit()
