"""主程序入口。"""

import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from autogen.settings import setup_qt_environment
from library.controllers.serial_config_controller import SerialConfig


def main():
    """主程序入口"""
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    serial_config = SerialConfig()
    serial_config.refreshPorts()
    app.aboutToQuit.connect(serial_config.closeSerial)

    engine.rootContext().setContextProperty("serialConfig", serial_config)
    setup_qt_environment(engine)

    if not engine.rootObjects():
        sys.exit(-1)

    ex = app.exec()
    del engine
    return ex


if __name__ == "__main__":
    sys.exit(main())



