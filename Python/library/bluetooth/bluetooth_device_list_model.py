"""
蓝牙设备列表模型
使用 QAbstractListModel 为 QML 提供稳定的增量显示数据源
"""

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class BluetoothDeviceListModel(QAbstractListModel):
    ROLE_DEVICE_NAME = Qt.UserRole + 1
    ROLE_DEVICE_ID = Qt.UserRole + 2
    ROLE_UUID = Qt.UserRole + 3
    ROLE_RSSI_TEXT = Qt.UserRole + 4
    ROLE_RSSI_VALUE = Qt.UserRole + 5
    ROLE_IS_CACHED = Qt.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._items)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        if row < 0 or row >= len(self._items):
            return None

        item = self._items[row]
        if role == self.ROLE_DEVICE_NAME:
            return item.get("name", "未知设备")
        if role == self.ROLE_DEVICE_ID:
            return item.get("device_id", "未知ID")
        if role == self.ROLE_UUID:
            return item.get("uuid", "null")
        if role == self.ROLE_RSSI_TEXT:
            return item.get("rssi_text", "未知")
        if role == self.ROLE_RSSI_VALUE:
            return item.get("rssi", 127)
        if role == self.ROLE_IS_CACHED:
            return bool(item.get("is_cached", False))

        return None

    def roleNames(self):
        return {
            self.ROLE_DEVICE_NAME: b"deviceName",
            self.ROLE_DEVICE_ID: b"deviceId",
            self.ROLE_UUID: b"deviceUuid",
            self.ROLE_RSSI_TEXT: b"rssiText",
            self.ROLE_RSSI_VALUE: b"rssiValue",
            self.ROLE_IS_CACHED: b"isCached",
        }

    def set_devices(self, items):
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()

    def clear(self):
        self.set_devices([])
