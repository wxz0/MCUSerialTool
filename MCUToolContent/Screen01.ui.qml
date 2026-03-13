

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

    // ── 接收缓冲区容器 ──────────────────────────────────────────────
    Rectangle {
        id: receiveContainer
        x: 10
        y: 5
        width: 638
        height: 521
        color: "transparent"
        border.color: "#A0A0A0"
        border.width: 1
        radius: 4

        Text {
            id: text1
            x: 22
            y: 14
            text: qsTr("接收缓冲区")
            font.pixelSize: 29
            font.bold: true
        }

        Frame {
            id: frame
            x: 7
            y: 3
            width: 175
            height: 58
        }

        Switch {
            id: switchModbusReceive
            x: 15
            y: 65
            text: qsTr("Modbus模式")
            onToggled: serialConfig.setModbusMode(checked)
        }

        Switch {
            id: switch1
            x: 15
            y: 115
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
            x: 15
            y: 165
            text: qsTr("HEX模式")
            ButtonGroup.group: receiveModeGroup
            onToggled: {
                if (checked)
                    serialConfig.setReceiveHexMode(true)
            }
        }

        Switch {
            id: switchTimestamp
            x: 15
            y: 215
            text: qsTr("时间戳模式")
            onToggled: serialConfig.setTimestampEnabled(checked)
        }

        Button {
            id: button
            x: 15
            y: 275
            width: 146
            height: 52
            text: qsTr("清空接收区")
            onClicked: serialConfig.clearReceivedText()
        }

        Button {
            id: button1
            x: 15
            y: 335
            width: 146
            height: 52
            text: qsTr("保存接收区")
        }

        Button {
            id: button2
            x: 15
            y: 395
            text: qsTr("复制接受区数据")
        }

        Label {
            id: labelEncoding
            x: 15
            y: 455
            width: 60
            height: 23
            text: qsTr("编码")
            font.pointSize: 12
        }

        ComboBox {
            id: comboBoxEncoding
            x: 22
            y: 475
            width: 146
            height: 36
            model: serialConfig.encodingOptions
            currentIndex: 0
            onCurrentTextChanged: serialConfig.setEncoding(currentText)
        }

        // 串口接收数据：顶部与 switchModbusReceive 顶部对齐（y=65），
        // 底部与 comboBoxEncoding 底部对齐（475+36=511），高度=511-65=446
        Flickable {
            id: flickableReceive
            x: 191
            y: 65
            width: 427
            height: 446
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
    }

    // ── 发送缓冲区容器 ──────────────────────────────────────────────
    Rectangle {
        id: sendContainer
        x: 10
        y: 535
        width: 638
        height: 315
        color: "transparent"
        border.color: "#A0A0A0"
        border.width: 1
        radius: 4

        Text {
            id: text2
            x: 22
            y: 19
            text: qsTr("发送缓冲区")
            font.pixelSize: 29
            font.bold: true
        }

        Frame {
            id: frame1
            x: 7
            y: 8
            width: 175
            height: 58
        }

        Switch {
            id: switch3
            x: 15
            y: 85
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
            x: 15
            y: 135
            text: qsTr("HEX模式")
            ButtonGroup.group: sendModeGroup
            onToggled: {
                if (checked)
                    serialConfig.setSendHexMode(true)
            }
        }

        Button {
            id: button3
            x: 15
            y: 195
            width: 146
            height: 52
            text: qsTr("清空发送区")
            onClicked: textArea1.text = ""
        }

        Button {
            id: button4
            x: 15
            y: 255
            width: 146
            height: 52
            text: qsTr("发送")
            onClicked: serialConfig.sendData(textArea1.text)
        }

        TextArea {
            id: textArea1
            x: 191
            y: 68
            width: 427
            height: 237
            wrapMode: TextArea.WrapAnywhere
            placeholderText: qsTr("输入待发送内容；HEX 模式示例: 01 03 00 00 00 01")
        }
    }

    // ── 串口参数容器（顶部与接收缓冲区容器对齐 y=5）──────────────────
    Rectangle {
        id: serialParamContainer
        x: 658
        y: 5
        width: 612
        height: 323
        color: "transparent"
        border.color: "#A0A0A0"
        border.width: 1
        radius: 4

        // 标题（左列起始 x=66，与两列内容水平居中对齐）
        Text {
            id: text4
            x: 66
            y: 14
            text: qsTr("串口参数")
            font.pixelSize: 29
            font.bold: true
        }

        Frame {
            id: frame2
            x: 56
            y: 3
            width: 139
            height: 58
        }

        // 第一行：串口 | 波特率
        Label {
            id: label
            x: 66
            y: 78
            width: 90
            height: 23
            text: qsTr("串口")
            font.pointSize: 18
        }

        ComboBox {
            id: comboBox
            x: 66
            y: 103
            width: 220
            height: 36
            model: serialConfig.availablePorts
            currentIndex: 0
            enabled: !serialConfig.serialOpen
        }

        Label {
            id: label1
            x: 306
            y: 78
            width: 90
            height: 23
            text: qsTr("波特率")
            font.pointSize: 18
        }

        ComboBox {
            id: comboBox1
            x: 306
            y: 103
            width: 240
            height: 36
            model: serialConfig.baudRates
            currentIndex: 10
            enabled: !serialConfig.serialOpen
        }

        // 第二行：校验位 | 停止位
        Label {
            id: label2
            x: 66
            y: 157
            width: 90
            height: 23
            text: qsTr("校验位")
            font.pointSize: 18
        }

        ComboBox {
            id: comboBox2
            x: 66
            y: 182
            width: 220
            height: 36
            layer.enabled: false
            model: serialConfig.parityOptions
            currentIndex: 0
            enabled: !serialConfig.serialOpen
        }

        Label {
            id: label3
            x: 306
            y: 157
            width: 90
            height: 23
            text: qsTr("停止位")
            font.pointSize: 18
        }

        ComboBox {
            id: comboBox3
            x: 306
            y: 182
            width: 240
            height: 36
            model: serialConfig.stopBitsOptions
            currentIndex: 0
            enabled: !serialConfig.serialOpen
        }

        // 操作按钮行（与两列对齐）
        Button {
            id: button5
            x: 66
            y: 236
            width: 220
            height: 42
            text: qsTr("刷新串口")
            enabled: !serialConfig.serialOpen
            onClicked: serialConfig.refreshPorts()
        }

        Button {
            id: button6
            x: 306
            y: 236
            width: 240
            height: 42
            text: serialConfig.serialOpen ? qsTr("关闭串口") : qsTr("打开串口")
            onClicked: serialConfig.toggleSerial(comboBox.currentText, comboBox1.currentText, comboBox2.currentText, comboBox3.currentText)
        }

        // 状态栏
        Label {
            id: label8
            x: 66
            y: 290
            width: 480
            height: 23
            text: serialConfig.serialStatus
            elide: Label.ElideRight
        }
    }

    // ── Modbus快捷发送容器 ────────────────────────────────────────
    Rectangle {
        id: modbusContainer
        x: 658
        y: 338
        width: 612
        height: 342
        color: "transparent"
        border.color: "#A0A0A0"
        border.width: 1
        radius: 4

        Text {
            id: text3
            x: 66
            y: 14
            text: qsTr("ModBus快捷发送")
            font.pixelSize: 29
            font.bold: true
        }

        Frame {
            id: frame3
            x: 56
            y: 3
            width: 255
            height: 58
        }

        // 第一行：设备地址 | 功能码
        Label {
            id: label4
            x: 66
            y: 78
            width: 100
            height: 23
            text: qsTr("设备地址")
            font.pointSize: 18
        }

        ComboBox {
            id: comboBox4
            x: 66
            y: 103
            width: 220
            height: 36
            editable: true
            model: [
                "1", "2", "3", "4", "5",
                "10", "16", "32", "64", "128", "247"
            ]
            currentIndex: 0
            validator: IntValidator {
                bottom: 1
                top: 247
            }
        }

        Label {
            id: label5
            x: 306
            y: 78
            width: 90
            height: 23
            text: qsTr("功能码")
            font.pointSize: 18
        }

        ComboBox {
            id: comboBox5
            x: 306
            y: 103
            width: 240
            height: 36
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

        // 第二行：起始地址 | 寄存器长度
        Label {
            id: label6
            x: 66
            y: 157
            width: 100
            height: 23
            text: qsTr("起始地址")
            font.pointSize: 18
        }

        TextField {
            id: textFieldStartAddress
            x: 66
            y: 182
            width: 220
            height: 40
            placeholderText: qsTr("例如: 0010 或 0x0010")
            text: "0000"
            inputMethodHints: Qt.ImhPreferUppercase
            validator: RegularExpressionValidator {
                regularExpression: /^(0x|0X)?[0-9A-Fa-f]{1,4}$/
            }
        }

        Label {
            id: label7
            x: 306
            y: 157
            width: 140
            height: 23
            text: qsTr("寄存器长度")
            font.pointSize: 18
        }

        TextField {
            id: textFieldRegisterLength
            x: 306
            y: 182
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

        // 操作按钮（横跨两列）
        Button {
            id: buttonModbusSend
            x: 66
            y: 240
            width: 480
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
            x: 66
            y: 292
            width: 480
            height: 42
            text: qsTr("查询 Modbus 设备地址")
            enabled: serialConfig.serialOpen
            onClicked: modbusQueryDialog.open()
        }

        Dialog {
            id: modbusQueryDialog
            modal: true
            x: 100
            y: 50
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
    }

}
