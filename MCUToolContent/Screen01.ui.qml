

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
    width: parent ? parent.width : Constants.width
    height: parent ? parent.height : Constants.height
    visible: true

    property int pageMargin: 10
    property int panelGap: 10
    property int compactLabelX: 18
    property int compactFieldX: 90
    property int compactFieldWidth: 190
    property int compactRightPadding: 12
    property int rightColumnWidth: compactFieldX + compactFieldWidth + compactRightPadding
    property color panelBorderColor: "#A0A0A0"
    property color titleColor: "#404040"
    property color labelColor: "#404040"
    property color statusColor: "#555555"
    property int panelRadius: 4
    property int titlePixelSize: 20
    property int labelPointSize: 11
    property int fieldHeight: 32
    property int buttonHeight: 34
    property int smallButtonWidth: 126
    property int sideNavWidth: 44
    property int settingsTopMargin: 5
    property int currentSettingsPanel: 0

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

    ButtonGroup {
        id: settingsPanelGroup
        exclusive: true
    }

    Rectangle {
        id: settingsNavContainer
        anchors.top: parent.top
        anchors.topMargin: settingsTopMargin
        anchors.left: parent.left
        anchors.leftMargin: pageMargin
        anchors.bottom: parent.bottom
        anchors.bottomMargin: pageMargin
        width: sideNavWidth
        color: "transparent"
        border.color: panelBorderColor
        border.width: 1
        radius: panelRadius

        Column {
            anchors.top: parent.top
            anchors.topMargin: 8
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 8

            Button {
                id: buttonPanelSerial
                width: 34
                height: 48
                text: qsTr("串口")
                checkable: true
                checked: currentSettingsPanel === 0
                font.pointSize: 9
                ButtonGroup.group: settingsPanelGroup
                onClicked: currentSettingsPanel = 0
            }

            Button {
                id: buttonPanelModbus
                width: 34
                height: 48
                text: qsTr("Mod")
                checkable: true
                checked: currentSettingsPanel === 1
                font.pointSize: 9
                ButtonGroup.group: settingsPanelGroup
                onClicked: currentSettingsPanel = 1
            }
        }
    }

    // ── 接收缓冲区容器 ──────────────────────────────────────────────
    Rectangle {
        id: receiveContainer
        anchors.left: serialParamContainer.right
        anchors.leftMargin: panelGap
        anchors.top: parent.top
        anchors.topMargin: settingsTopMargin
        anchors.right: parent.right
        anchors.rightMargin: pageMargin
        anchors.bottom: sendContainer.top
        anchors.bottomMargin: panelGap
        color: "transparent"
        border.color: panelBorderColor
        border.width: 1
        radius: panelRadius

        Text {
            id: text1
            x: 18
            y: 12
            text: qsTr("接收缓冲区")
            font.pixelSize: titlePixelSize
            font.bold: true
            color: titleColor
        }

        Switch {
            id: switch1
            x: 18
            y: 44
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
            x: 18
            y: 80
            text: qsTr("HEX模式")
            ButtonGroup.group: receiveModeGroup
            onToggled: {
                if (checked)
                    serialConfig.setReceiveHexMode(true)
            }
        }

        Switch {
            id: switchTimestamp
            x: 18
            y: 116
            text: qsTr("时间戳模式")
            onToggled: serialConfig.setTimestampEnabled(checked)
        }

        Button {
            id: button
            x: 18
            y: 194
            width: switchTimestamp.x + switchTimestamp.width - x
            height: buttonHeight
            text: qsTr("清空接收区")
            onClicked: serialConfig.clearReceivedText()
        }

        Button {
            id: button1
            x: 18
            y: 234
            width: switchTimestamp.x + switchTimestamp.width - x
            height: buttonHeight
            text: qsTr("保存接收区")
        }

        Button {
            id: button2
            x: 18
            y: 274
            width: switchTimestamp.x + switchTimestamp.width - x
            height: buttonHeight
            text: qsTr("复制接受区")
        }

        Label {
            id: labelEncoding
            x: 20
            width: 48
            height: 20
            y: 158
            text: qsTr("编码")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBoxEncoding
            x: 60
            width: 100
            height: fieldHeight
            y: 152
            model: serialConfig.encodingOptions
            currentIndex: 0
            onCurrentTextChanged: serialConfig.setEncoding(currentText)
        }

        Flickable {
            id: flickableReceive
            anchors.left: button.right
            anchors.leftMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 44
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 10
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
        anchors.left: serialParamContainer.right
        anchors.leftMargin: panelGap
        anchors.right: parent.right
        anchors.rightMargin: pageMargin
        anchors.bottom: parent.bottom
        anchors.bottomMargin: pageMargin
        height: Math.max(250, Math.round(parent.height * 0.34))
        color: "transparent"
        border.color: panelBorderColor
        border.width: 1
        radius: panelRadius

        Text {
            id: text2
            x: 18
            y: 12
            text: qsTr("发送缓冲区")
            font.pixelSize: titlePixelSize
            font.bold: true
            color: titleColor
        }

        Switch {
            id: switch3
            x: 18
            y: 44
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
            x: 18
            y: 80
            text: qsTr("HEX模式")
            ButtonGroup.group: sendModeGroup
            onToggled: {
                if (checked)
                    serialConfig.setSendHexMode(true)
            }
        }

        Button {
            id: button3
            x: 18
            y: 116
            width: switch4.x + switch4.width - x
            height: buttonHeight
            text: qsTr("清空发送区")
            onClicked: textArea1.text = ""
        }

        Button {
            id: button4
            x: 18
            y: 156
            width: switch4.x + switch4.width - x
            height: buttonHeight
            text: qsTr("发送")
            onClicked: serialConfig.sendData(textArea1.text)
        }

        TextArea {
            id: textArea1
            anchors.left: button3.right
            anchors.leftMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 44
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 10
            wrapMode: TextArea.WrapAnywhere
            placeholderText: qsTr("输入待发送内容；HEX 模式示例: 01 03 00 00 00 01")
        }
    }

    // ── 串口参数容器（顶部与接收缓冲区容器对齐 y=5）──────────────────
    Rectangle {
        id: serialParamContainer
        visible: currentSettingsPanel === 0
        anchors.top: parent.top
        anchors.topMargin: settingsTopMargin
        anchors.left: parent.left
        anchors.leftMargin: pageMargin + sideNavWidth + panelGap
        anchors.bottom: parent.bottom
        anchors.bottomMargin: pageMargin
        width: rightColumnWidth
        color: "transparent"
        border.color: panelBorderColor
        border.width: 1
        radius: panelRadius

        // 紧凑串口设置样式（参考传统串口工具）
        Text {
            id: text4
            x: 18
            y: 12
            text: qsTr("串口设置")
            font.pixelSize: titlePixelSize
            font.bold: true
            color: titleColor
        }

        Label {
            id: label
            x: 18
            y: 50
            text: qsTr("串口")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBox
            x: 90
            y: 44
            width: parent.width - x - 12
            height: fieldHeight
            model: serialConfig.availablePorts
            currentIndex: 0
            enabled: !serialConfig.serialOpen
        }

        Label {
            id: label1
            x: 18
            y: 86
            text: qsTr("波特率")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBox1
            x: 90
            y: 80
            width: parent.width - x - 12
            height: fieldHeight
            model: serialConfig.baudRates
            currentIndex: 10
            enabled: !serialConfig.serialOpen
        }

        Label {
            id: labelDataBits
            x: 18
            y: 122
            text: qsTr("数据位")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBoxDataBits
            x: 90
            y: 116
            width: parent.width - x - 12
            height: fieldHeight
            model: ["8"]
            currentIndex: 0
            enabled: false
        }

        Label {
            id: label2
            x: 18
            y: 158
            text: qsTr("停止位")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBox3
            x: 90
            y: 152
            width: parent.width - x - 12
            height: fieldHeight
            layer.enabled: false
            model: serialConfig.stopBitsOptions
            currentIndex: 0
            enabled: !serialConfig.serialOpen
        }

        Label {
            id: label3
            x: 18
            y: 194
            text: qsTr("校验位")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBox2
            x: 90
            y: 188
            width: parent.width - x - 12
            height: fieldHeight
            model: serialConfig.parityOptions
            currentIndex: 0
            enabled: !serialConfig.serialOpen
        }

        Button {
            id: button5
            x: 18
            y: 232
            width: smallButtonWidth
            height: buttonHeight
            text: qsTr("刷新")
            enabled: !serialConfig.serialOpen
            onClicked: serialConfig.refreshPorts()
        }

        Button {
            id: button6
            x: 154
            y: 232
            width: smallButtonWidth
            height: buttonHeight
            text: serialConfig.serialOpen ? qsTr("关闭串口") : qsTr("打开串口")
            onClicked: serialConfig.toggleSerial(comboBox.currentText, comboBox1.currentText, comboBox2.currentText, comboBox3.currentText)
        }

        Label {
            id: label8
            x: 18
            y: 272
            width: parent.width - 30
            height: 30
            text: serialConfig.serialStatus
            elide: Label.ElideRight
            wrapMode: Label.Wrap
            font.pointSize: 9
            color: statusColor
        }
    }

    // ── Modbus快捷发送容器 ────────────────────────────────────────
    Rectangle {
        id: modbusContainer
        visible: currentSettingsPanel === 1
        anchors.top: parent.top
        anchors.topMargin: settingsTopMargin
        anchors.left: parent.left
        anchors.leftMargin: pageMargin + sideNavWidth + panelGap
        anchors.bottom: parent.bottom
        anchors.bottomMargin: pageMargin
        width: rightColumnWidth
        color: "transparent"
        border.color: panelBorderColor
        border.width: 1
        radius: panelRadius

        Text {
            id: text3
            x: 18
            y: 12
            text: qsTr("Modbus设置")
            font.pixelSize: titlePixelSize
            font.bold: true
            color: titleColor
        }

        Label {
            id: switchModbusReceiveLabel
            x: 18
            y: 50
            text: qsTr("Modbus模式")
            font.pointSize: labelPointSize
            color: labelColor
        }

        Switch {
            id: switchModbusReceive
            x: 90
            y: 44
            text: ""
            onToggled: serialConfig.setModbusMode(checked)
        }

        Label {
            id: label4
            x: 18
            y: 86
            text: qsTr("设备地址")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBox4
            x: 90
            y: 80
            width: parent.width - x - 12
            height: fieldHeight
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
            x: 18
            y: 122
            text: qsTr("功能码")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBox5
            x: 90
            y: 116
            width: parent.width - x - 12
            height: fieldHeight
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

        Label {
            id: label6
            x: 18
            y: 158
            text: qsTr("起始地址")
            font.pointSize: labelPointSize
            color: labelColor
        }

        TextField {
            id: textFieldStartAddress
            x: 90
            y: 152
            width: parent.width - x - 12
            height: fieldHeight
            placeholderText: qsTr("如: 0010")
            text: "0000"
            inputMethodHints: Qt.ImhPreferUppercase
            validator: RegularExpressionValidator {
                regularExpression: /^(0x|0X)?[0-9A-Fa-f]{1,4}$/
            }
        }

        Label {
            id: label7
            x: 18
            y: 194
            text: qsTr("寄存器长度")
            font.pointSize: labelPointSize
            color: labelColor
        }

        TextField {
            id: textFieldRegisterLength
            x: 90
            y: 188
            width: parent.width - x - 12
            height: fieldHeight
            placeholderText: qsTr("如: 1")
            text: "1"
            inputMethodHints: Qt.ImhDigitsOnly
            validator: IntValidator {
                bottom: 1
                top: 125
            }
        }

        Button {
            id: buttonModbusSend
            x: 18
            y: 230
            width: parent.width - 30
            height: buttonHeight
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
            x: 18
            y: 270
            width: parent.width - 30
            height: buttonHeight
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
