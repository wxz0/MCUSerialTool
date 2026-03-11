

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import MCUTool

Rectangle {
    width: Constants.width
    height: Constants.height
    visible: true

    color: Constants.backgroundColor
    clip: true

    ButtonGroup {
        id: receiveModeGroup
        exclusive: true
    }

    ButtonGroup {
        id: sendModeGroup
        exclusive: true
    }

    Switch {
        id: switch1
        x: 25
        y: 120
        text: qsTr("文本模式")
        checked: true
        ButtonGroup.group: receiveModeGroup
        onToggled: {
            if (checked)
                serialConfig.setReceiveHexMode(false)
        }
    }

    Switch {
        id: switch2
        x: 25
        y: 170
        text: qsTr("HEX模式")
        ButtonGroup.group: receiveModeGroup
        onToggled: {
            if (checked)
                serialConfig.setReceiveHexMode(true)
        }
    }

    Switch {
        id: switchTimestamp
        x: 25
        y: 220
        text: qsTr("时间戳模式")
        onToggled: serialConfig.setTimestampEnabled(checked)
    }

    Button {
        id: button
        x: 25
        y: 280
        width: 146
        height: 52
        text: qsTr("清空接收区")
        onClicked: serialConfig.clearReceivedText()
    }

    Button {
        id: button1
        x: 25
        y: 340
        width: 146
        height: 52
        text: qsTr("保存接收区")
    }

    Button {
        id: button2
        x: 25
        y: 400
        text: qsTr("复制接受区数据")
    }

    Label {
        id: labelEncoding
        x: 25
        y: 460
        width: 60
        height: 23
        text: qsTr("编码")
        font.pointSize: 12
    }

    ComboBox {
        id: comboBoxEncoding
        x: 32
        y: 480
        width: 146
        height: 36
        model: serialConfig.encodingOptions
        currentIndex: 0
        onCurrentTextChanged: serialConfig.setEncoding(currentText)
    }

    Switch {
        id: switchModbusReceive
        x: 25
        y: 70
        text: qsTr("Modbus模式")
        onToggled: serialConfig.setModbusMode(checked)
    }

    Text {
        id: text1
        x: 32
        y: 19
        text: qsTr("接收缓冲区")
        font.pixelSize: 29
        font.bold: true
    }

    Frame {
        id: frame
        x: 17
        y: 8
        width: 175
        height: 58
    }

    Flickable {
        id: flickableReceive
        x: 201
        y: 67
        width: 427
        height: 433
        clip: true
        property bool autoScroll: true

        onDragStarted: autoScroll = false
        onFlickStarted: autoScroll = false
        onMovementEnded: autoScroll = atYEnd

        TextArea.flickable: TextArea {
            id: textArea
            readOnly: true
            wrapMode: TextArea.WrapAnywhere
            text: serialConfig.receivedText
            placeholderText: qsTr("串口接收数据将显示在这里")

            // Watch TextArea's own content height after layout has settled.
            onContentHeightChanged: {
                if (flickableReceive.autoScroll) {
                    Qt.callLater(function() {
                        flickableReceive.contentY =
                            Math.max(0, flickableReceive.contentHeight - flickableReceive.height)
                    })
                }
            }
        }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AlwaysOn
        }
    }

    Text {
        id: text2
        x: 32
        y: 584
        text: qsTr("发送缓冲区")
        font.pixelSize: 29
        font.bold: true
    }

    Frame {
        id: frame1
        x: 17
        y: 573
        width: 175
        height: 58
    }

    Switch {
        id: switch3
        x: 25
        y: 650
        text: qsTr("文本模式")
        checked: true
        ButtonGroup.group: sendModeGroup
        onToggled: {
            if (checked)
                serialConfig.setSendHexMode(false)
        }
    }

    Switch {
        id: switch4
        x: 25
        y: 700
        text: qsTr("HEX模式")
        ButtonGroup.group: sendModeGroup
        onToggled: {
            if (checked)
                serialConfig.setSendHexMode(true)
        }
    }

    Button {
        id: button3
        x: 25
        y: 760
        width: 146
        height: 52
        text: qsTr("清空发送区")
        onClicked: textArea1.text = ""
    }

    TextArea {
        id: textArea1
        x: 201
        y: 633
        width: 427
        height: 277
        wrapMode: TextArea.WrapAnywhere
        placeholderText: qsTr("输入待发送内容；HEX 模式示例: 01 03 00 00 00 01")
    }

    Button {
        id: button4
        x: 25
        y: 830
        width: 146
        height: 52
        text: qsTr("发送")
        onClicked: serialConfig.sendData(textArea1.text)
    }

    ComboBox {
        id: comboBox
        x: 757
        y: 179
        width: 220
        model: serialConfig.availablePorts
        currentIndex: 0
        enabled: !serialConfig.serialOpen
    }

    ComboBox {
        id: comboBox1
        x: 1005
        y: 179
        width: 240
        model: serialConfig.baudRates
        currentIndex: 10
        enabled: !serialConfig.serialOpen
    }

    ComboBox {
        id: comboBox2
        x: 757
        y: 304
        width: 220
        layer.enabled: false
        model: serialConfig.parityOptions
        currentIndex: 0
        enabled: !serialConfig.serialOpen
    }

    ComboBox {
        id: comboBox3
        x: 1005
        y: 304
        width: 240
        model: serialConfig.stopBitsOptions
        currentIndex: 0
        enabled: !serialConfig.serialOpen
    }

    Button {
        id: button5
        x: 757
        y: 366
        width: 120
        height: 42
        text: qsTr("刷新串口")
        enabled: !serialConfig.serialOpen
        onClicked: serialConfig.refreshPorts()
    }

    Button {
        id: button6
        x: 892
        y: 366
        width: 188
        height: 42
        text: serialConfig.serialOpen ? qsTr("关闭串口") : qsTr("打开串口")
        onClicked: serialConfig.toggleSerial(comboBox.currentText, comboBox1.currentText, comboBox2.currentText, comboBox3.currentText)
    }

    Label {
        id: label8
        x: 757
        y: 417
        width: 430
        height: 23
        text: serialConfig.serialStatus
        elide: Label.ElideRight
    }

    Label {
        id: label
        x: 757
        y: 146
        width: 70
        height: 23
        text: qsTr("串口")
        font.pointSize: 18
    }

    Label {
        id: label1
        x: 1005
        y: 146
        width: 90
        height: 23
        text: qsTr("波特率")
        font.pointSize: 18
    }

    Label {
        id: label2
        x: 757
        y: 271
        width: 90
        height: 23
        text: qsTr("校验位")
        font.pointSize: 18
    }

    Label {
        id: label3
        x: 1005
        y: 271
        width: 90
        height: 23
        text: qsTr("停止位")
        font.pointSize: 18
    }

    Text {
        id: text3
        x: 675
        y: 457
        width: 247
        height: 44
        text: qsTr("ModBus快捷发送")
        font.pixelSize: 29
        font.bold: true
    }

    ComboBox {
        id: comboBox4
        x: 757
        y: 525
        width: 220
        editable: true
        model: [
            "1",
            "2",
            "3",
            "4",
            "5",
            "10",
            "16",
            "32",
            "64",
            "128",
            "247"
        ]
        currentIndex: 0
        validator: IntValidator {
            bottom: 1
            top: 247
        }
    }

    ComboBox {
        id: comboBox5
        x: 1005
        y: 525
        width: 240
        model: [
            "01 读取线圈状态",
            "02 读取离散输入",
            "03 读取保持寄存器",
            "04 读取输入寄存器",
            "05 写单个线圈",
            "06 写单个寄存器",
            "0F 写多个线圈",
            "10 写多个寄存器"
        ]
        currentIndex: 2
    }

    TextField {
        id: textFieldStartAddress
        x: 757
        y: 650
        width: 220
        height: 40
        placeholderText: qsTr("例如: 0010 或 0x0010")
        text: "0000"
        inputMethodHints: Qt.ImhPreferUppercase
        validator: RegularExpressionValidator {
            regularExpression: /^(0x|0X)?[0-9A-Fa-f]{1,4}$/
        }
    }

    TextField {
        id: textFieldRegisterLength
        x: 1005
        y: 650
        width: 240
        height: 40
        placeholderText: qsTr("例如: 1")
        text: "1"
        inputMethodHints: Qt.ImhDigitsOnly
        validator: IntValidator {
            bottom: 1
            top: 125
        }
    }

    Button {
        id: buttonModbusSend
        x: 757
        y: 710
        width: 488
        height: 42
        text: qsTr("发送 Modbus 命令")
        enabled: serialConfig.serialOpen
        onClicked: {
            switch4.checked = true
            var hexStr = serialConfig.sendModbusCommand(
                comboBox4.currentText,
                comboBox5.currentText,
                textFieldStartAddress.text,
                textFieldRegisterLength.text)
            if (hexStr !== "")
                textArea1.text = hexStr
        }
    }

    Button {
        id: buttonModbusQueryAddr
        x: 757
        y: 760
        width: 488
        height: 42
        text: qsTr("查询 Modbus 设备地址")
        enabled: serialConfig.serialOpen
        onClicked: modbusQueryDialog.open()
    }

    Dialog {
        id: modbusQueryDialog
        modal: true
        x: 820
        y: 380
        width: 360
        title: qsTr("输入寄存器位置")
        standardButtons: Dialog.Ok | Dialog.Cancel

        contentItem: Column {
            spacing: 10

            Label {
                text: qsTr("请输入寄存器地址(HEX, 0000-FFFF)")
            }

            Label {
                text: qsTr("扫描速度")
            }

            ComboBox {
                id: comboScanSpeed
                width: 320
                model: ["快 (60ms)", "中 (120ms)", "慢 (220ms)", "更慢 (400ms)"]
                property var scanTimeoutValues: [60, 120, 220, 400]
                currentIndex: 2
                onCurrentIndexChanged: {
                    serialConfig.setModbusQueryTimeout(scanTimeoutValues[currentIndex])
                }
                Component.onCompleted: {
                    serialConfig.setModbusQueryTimeout(scanTimeoutValues[currentIndex])
                }
            }

            TextField {
                id: queryRegisterField
                width: 320
                text: textFieldStartAddress.text
                inputMethodHints: Qt.ImhPreferUppercase
                validator: RegularExpressionValidator {
                    regularExpression: /^(0x|0X)?[0-9A-Fa-f]{1,4}$/
                }
            }
        }

        onAccepted: {
            var result = serialConfig.queryModbusDeviceAddresses(queryRegisterField.text)
            if (result !== "")
                textArea1.text = result
        }
    }

    Label {
        id: label4
        x: 757
        y: 500
        width: 100
        height: 23
        text: qsTr("设备地址")
        font.pointSize: 18
    }

    Label {
        id: label5
        x: 1005
        y: 500
        width: 90
        height: 23
        text: qsTr("功能码")
        font.pointSize: 18
    }

    Label {
        id: label6
        x: 757
        y: 600
        width: 100
        height: 23
        text: qsTr("起始地址")
        font.pointSize: 18
    }

    Label {
        id: label7
        x: 1005
        y: 600
        width: 140
        height: 23
        text: qsTr("寄存器长度")
        font.pointSize: 18
    }

    Text {
        id: text4
        x: 675
        y: 88
        width: 247
        height: 44
        text: qsTr("串口参数")
        font.pixelSize: 29
        font.bold: true
    }

    Frame {
        id: frame2
        x: 667
        y: 78
        width: 139
        height: 62
    }

    Frame {
        id: frame3
        x: 667
        y: 444
        width: 255
        height: 57
    }

}
