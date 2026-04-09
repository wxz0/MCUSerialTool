

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
    property bool modbusQueryNoticeVisible: false

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

            Button {
                id: buttonPanelBluetooth
                width: 34
                height: 48
                text: qsTr("蓝牙")
                checkable: true
                checked: currentSettingsPanel === 2
                font.pointSize: 9
                ButtonGroup.group: settingsPanelGroup
                onClicked: currentSettingsPanel = 2
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
                placeholderText: qsTr("接收的数据将显示在这里")

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
            id: readSectionTitle
            x: 18
            y: 122
            text: qsTr("读寄存器区")
            font.pointSize: labelPointSize
            font.bold: true
            color: labelColor
        }

        Label {
            id: labelReadFc
            x: 18
            y: 158
            text: qsTr("功能码")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBoxReadFc
            x: 90
            y: 152
            width: parent.width - x - 12
            height: fieldHeight
            model: [
                "01 读取线圈状态",
                "02 读取离散输入",
                "03 读取保持寄存器",
                "04 读取输入寄存器"
            ]
            currentIndex: 2
        }

        Label {
            id: labelReadStartAddress
            x: 18
            y: 194
            text: qsTr("起始地址")
            font.pointSize: labelPointSize
            color: labelColor
        }

        TextField {
            id: textFieldStartAddress
            x: 90
            y: 188
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
            id: labelReadRegisterLength
            x: 18
            y: 230
            text: qsTr("读取数量")
            font.pointSize: labelPointSize
            color: labelColor
        }

        TextField {
            id: textFieldRegisterLength
            x: 90
            y: 224
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
            id: buttonReadRegisterSend
            x: 18
            y: 266
            width: parent.width - 30
            height: buttonHeight
            text: qsTr("发送读命令")
            enabled: serialConfig.serialOpen
            onClicked: {
                switch4.checked = true
                var hexStr = serialConfig.sendModbusReadCommand(
                    comboBox4.currentText,
                    comboBoxReadFc.currentText,
                    textFieldStartAddress.text,
                    textFieldRegisterLength.text)
                if (hexStr !== "")
                    textArea1.text = hexStr
            }
        }

        Label {
            id: writeSectionTitle
            x: 18
            y: 306
            text: qsTr("写寄存器区")
            font.pointSize: labelPointSize
            font.bold: true
            color: labelColor
        }

        Label {
            id: labelWriteFc
            x: 18
            y: 342
            text: qsTr("功能码")
            font.pointSize: labelPointSize
            color: labelColor
        }

        ComboBox {
            id: comboBoxWriteFc
            x: 90
            y: 336
            width: parent.width - x - 12
            height: fieldHeight
            model: [
                "05 写单个线圈",
                "06 写单个寄存器",
                "0F 写多个线圈",
                "10 写多个寄存器"
            ]
            currentIndex: 1
        }

        Label {
            id: labelWriteRegisterAddress
            x: 18
            y: 378
            text: qsTr("寄存器地址")
            font.pointSize: labelPointSize
            color: labelColor
        }

        TextField {
            id: textFieldWriteRegisterAddress
            x: 90
            y: 372
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
            id: labelWriteRegisterValue
            x: 18
            y: 414
            text: qsTr("写入数值")
            font.pointSize: labelPointSize
            color: labelColor
        }

        TextField {
            id: textFieldWriteRegisterValue
            x: 90
            y: 408
            width: parent.width - x - 12
            height: fieldHeight
            placeholderText: comboBoxWriteFc.currentIndex <= 1
                             ? qsTr("单值: 十进制或0xHEX")
                             : qsTr("多值: 用空格/逗号分隔")
            text: "0"
        }

        Button {
            id: buttonWriteRegisterSend
            x: 18
            y: 450
            width: parent.width - 30
            height: buttonHeight
            text: qsTr("发送写命令")
            enabled: serialConfig.serialOpen
            onClicked: {
                switch4.checked = true
                var hexStr = serialConfig.sendModbusWriteCommand(
                    comboBox4.currentText,
                    comboBoxWriteFc.currentText,
                    textFieldWriteRegisterAddress.text,
                    textFieldWriteRegisterValue.text)
                if (hexStr !== "")
                    textArea1.text = hexStr
            }
        }

        Button {
            id: buttonModbusQueryAddr
            x: 18
            y: 490
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
                if (result !== "") {
                    modbusQueryNoticeVisible = true
                    textArea1.text = qsTr("正在查询 Modbus 设备地址，请耐心等待...")
                }
            }
        }

        Rectangle {
            id: modbusQueryNotice
            visible: modbusQueryNoticeVisible
            x: 14
            y: 530
            width: parent.width - 28
            height: 66
            radius: 6
            color: "#EAF5FF"
            border.color: "#88B5E8"
            border.width: 1

            BusyIndicator {
                id: queryBusy
                x: 10
                y: 15
                width: 36
                height: 36
                running: modbusQueryNoticeVisible
            }

            Label {
                id: queryNoticeLabel
                x: 52
                y: 12
                width: parent.width - x - 10
                height: 42
                text: qsTr("当前正在查询中，请耐心等待...\n扫描 1-247 地址，完成后结果会自动显示")
                wrapMode: Label.Wrap
                color: "#24517C"
                font.pointSize: 10
            }

            SequentialAnimation on opacity {
                running: modbusQueryNoticeVisible
                loops: Animation.Infinite
                NumberAnimation { from: 0.65; to: 1.0; duration: 650 }
                NumberAnimation { from: 1.0; to: 0.65; duration: 650 }
            }
        }

        Connections {
            target: serialConfig
            function onModbusScanActiveChanged() {
                modbusQueryNoticeVisible = serialConfig.modbusScanActive
            }
        }
    }

    // ── 蓝牙功能容器 ───────────────────────────────────────────────
    Rectangle {
        id: bluetoothContainer
        visible: currentSettingsPanel === 2
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
            id: bluetoothTitle
            x: 18
            y: 12
            text: qsTr("蓝牙设备扫描")
            font.pixelSize: titlePixelSize
            font.bold: true
            color: titleColor
        }

        Label {
            id: bluetoothSupportLabel
            x: 18
            y: 48
            width: parent.width - 36
            text: serialConfig.bluetoothSupported
                  ? qsTr("使用系统蓝牙扫描周围设备")
                  : qsTr("当前运行环境不支持蓝牙扫描")
            wrapMode: Label.Wrap
            color: labelColor
            font.pointSize: 10
        }

        Row {
            id: bluetoothButtonRow
            x: 18
            y: 86
            width: parent.width - 36
            spacing: 8

            Button {
                id: bluetoothScanButton
                width: (parent.width - parent.spacing * 2) / 3
                height: buttonHeight
                text: qsTr("扫描")
                enabled: serialConfig.bluetoothSupported && !serialConfig.bluetoothScanning && !serialConfig.bluetoothLinkConnecting && !serialConfig.bluetoothLinkConnected
                onClicked: serialConfig.scanBluetoothDevices()
            }

            Button {
                id: bluetoothStopButton
                width: (parent.width - parent.spacing * 2) / 3
                height: buttonHeight
                text: qsTr("停止")
                enabled: serialConfig.bluetoothSupported && serialConfig.bluetoothScanning && !serialConfig.bluetoothLinkConnecting && !serialConfig.bluetoothLinkConnected
                onClicked: serialConfig.stopBluetoothScan()
            }

            Button {
                id: bluetoothClearButton
                width: (parent.width - parent.spacing * 2) / 3
                height: buttonHeight
                text: qsTr("清空")
                enabled: serialConfig.bluetoothSupported && !serialConfig.bluetoothLinkConnecting && !serialConfig.bluetoothLinkConnected
                onClicked: serialConfig.clearBluetoothDevices()
            }
        }

        BusyIndicator {
            id: bluetoothBusy
            x: 18
            y: 130
            width: 28
            height: 28
            running: serialConfig.bluetoothScanning || serialConfig.bluetoothLinkConnecting
            visible: running
        }

        Label {
            id: bluetoothStatusLabel
            x: 52
            y: 132
            width: parent.width - 68
            height: 32
            text: serialConfig.bluetoothLinkConnecting
                  ? qsTr("正在连接设备，请稍候...")
                  : serialConfig.bluetoothStatus
            color: statusColor
            font.pointSize: 10
            wrapMode: Label.Wrap
        }

        Label {
            id: bluetoothLinkStateLabel
            x: 18
            y: 162
            width: parent.width - 36
            height: 16
            text: serialConfig.bluetoothLinkConnecting
                  ? qsTr("正在建立连接，请稍候...")
                  : serialConfig.bluetoothLinkConnected
                  ? qsTr("已连接: ") + serialConfig.bluetoothLinkDeviceName + qsTr("，右侧收发框可直接通信")
                  : qsTr("点击设备卡片进行连接（推荐 HC08）")
            color: statusColor
            font.pointSize: 9
            elide: Label.ElideRight
            visible: true
        }

        Rectangle {
            id: bluetoothConnectingPanel
            visible: serialConfig.bluetoothLinkConnecting
            x: 18
            y: 196
            width: parent.width - 36
            height: parent.height - 206
            radius: 10
            color: "#F4F7FB"
            border.color: "#B8C9DB"
            border.width: 1

            BusyIndicator {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 48
                width: 36
                height: 36
                running: true
                visible: true
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 98
                text: qsTr("正在连接蓝牙设备")
                color: titleColor
                font.pixelSize: 18
                font.bold: true
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 132
                width: parent.width - 40
                horizontalAlignment: Text.AlignHCenter
                text: serialConfig.bluetoothLinkDeviceName.length > 0
                      ? serialConfig.bluetoothLinkDeviceName
                      : qsTr("请稍候，正在进行配对和服务发现")
                color: statusColor
                font.pixelSize: 12
                wrapMode: Text.Wrap
            }
        }

        Rectangle {
            id: bluetoothConnectedPanel
            visible: serialConfig.bluetoothLinkConnected && !serialConfig.bluetoothLinkConnecting
            x: 18
            y: 196
            width: parent.width - 36
            height: parent.height - 206
            radius: 10
            color: "#F7FBF7"
            border.color: "#B8D8C0"
            border.width: 1

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 46
                text: qsTr("已连接")
                color: "#2F8F46"
                font.pixelSize: 18
                font.bold: true
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 80
                width: parent.width - 40
                horizontalAlignment: Text.AlignHCenter
                text: serialConfig.bluetoothLinkDeviceName
                color: titleColor
                font.pixelSize: 14
                font.bold: true
                wrapMode: Text.Wrap
            }

            Button {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 118
                width: 96
                height: 30
                text: qsTr("断开连接")
                enabled: serialConfig.bluetoothLinkConnected
                onClicked: serialConfig.disconnectBluetoothDevice()
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 160
                width: parent.width - 40
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("现在可以直接使用右侧收发框和设备通信")
                color: statusColor
                font.pixelSize: 11
                wrapMode: Text.Wrap
            }
        }

        Rectangle {
            id: bluetoothListHeader
            x: 18
            y: 182
            width: parent.width - 36
            height: 28
            radius: 4
            color: "#EFEFEF"
            border.color: "#D0D0D0"
            border.width: 1
            visible: !serialConfig.bluetoothLinkConnecting && !serialConfig.bluetoothLinkConnected

            Text {
                x: 12
                y: 5
                width: parent.width - 24
                text: qsTr("附近设备") + qsTr(" (") + bluetoothListView.count + qsTr(")")
                color: statusColor
                font.pointSize: 10
                font.bold: true
            }
        }

        ListView {
            id: bluetoothListView
            x: 18
            anchors.top: bluetoothListHeader.bottom
            anchors.topMargin: 8
            width: parent.width - 36
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 10
            clip: true
            model: serialConfig.bluetoothDevicesModel
            spacing: 6
            visible: !serialConfig.bluetoothLinkConnecting && !serialConfig.bluetoothLinkConnected

            delegate: Rectangle {
                width: bluetoothListView.width
                height: 108
                radius: 10
                color: "#F6F6F6"
                border.color: hovered ? "#95B4D6" : "#E6E6E6"
                border.width: 1

                property bool hovered: false
                property string _name: (model && model.deviceName !== undefined) ? model.deviceName : ((modelData && modelData["name"]) ? modelData["name"] : qsTr("未知设备"))
                property string _id: (model && model.deviceId !== undefined) ? model.deviceId : ((modelData && modelData["device_id"]) ? modelData["device_id"] : qsTr("未知ID"))
                property string _uuid: (model && model.deviceUuid !== undefined) ? model.deviceUuid : ((modelData && modelData["uuid"]) ? modelData["uuid"] : "null")
                property string _rssiText: (model && model.rssiText !== undefined) ? model.rssiText : ((modelData && modelData["rssi_text"]) ? modelData["rssi_text"] : qsTr("未知"))
                property int _rssiValue: (model && model.rssiValue !== undefined) ? model.rssiValue : ((modelData && modelData["rssi"] !== undefined) ? modelData["rssi"] : 127)

                Rectangle {
                    x: 0
                    y: 0
                    width: 5
                    height: parent.height
                    radius: 10
                    color: _rssiValue === 127 ? "#B0B0B0" : (_rssiValue > -60 ? "#33A257" : _rssiValue > -80 ? "#F1A208" : "#D64A4A")
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                    onClicked: serialConfig.connectBluetoothDevice(_id, _name, _uuid)
                }

                Text {
                    x: 14
                    y: 10
                    width: parent.width - 120
                    text: _name
                    color: "#202020"
                    font.pointSize: 12
                    font.bold: true
                    verticalAlignment: Text.AlignTop
                    elide: Text.ElideRight
                }

                Text {
                    x: 14
                    y: 40
                    width: parent.width - 120
                    text: qsTr("DeviceId:  ") + _id
                    color: "#7B7B7B"
                    font.pointSize: 9
                    wrapMode: Text.WrapAnywhere
                }

                Text {
                    x: 14
                    y: 67
                    width: parent.width - 120
                    text: qsTr("UUID: ") + _uuid
                    color: "#7B7B7B"
                    font.pointSize: 9
                    wrapMode: Text.WrapAnywhere
                }

                Text {
                    anchors.right: parent.right
                    anchors.rightMargin: 14
                    y: 44
                    width: 88
                    horizontalAlignment: Text.AlignRight
                    text: qsTr("RSSI:  ") + _rssiText
                    color: "#262626"
                    font.pointSize: 11
                    font.bold: true
                    elide: Text.ElideRight
                }
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AlwaysOn
            }
        }

        Text {
            visible: !serialConfig.bluetoothLinkConnecting && !serialConfig.bluetoothLinkConnected && bluetoothListView.count === 0
            x: 18
            y: 238
            width: parent.width - 36
            text: serialConfig.bluetoothScanning
                  ? qsTr("正在搜索附近设备...")
                  : qsTr("暂无蓝牙设备结果，请点击“扫描”")
            color: statusColor
            font.pointSize: 10
            horizontalAlignment: Text.AlignHCenter
        }
    }

}
