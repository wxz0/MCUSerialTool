# MCUTool Python模块 - 快速参考

## 📦 模块概览

| 模块 | 职责 | 关键类/函数 | 行数 |
|------|------|----------|------|
| **main.py** | 主程序入口，协调各模块 | `SerialConfig` | ~450 |
| **serial_config_parser.py** | 串口配置参数解析 | `SerialConfigParser` | ~100 |
| **data_handler.py** | 数据编码/解码 | `DataHandler` | ~120 |
| **modbus_protocol.py** | Modbus RTU协议 | `ModbusProtocol` | ~230 |
| **serial_port_manager.py** | 串口底层操作 | `SerialPortManager` | ~80 |

---

## 🚀 快速开始

### 1. 初始化
```python
from main import SerialConfig

config = SerialConfig()
config.refreshPorts()  # 刷新可用串口
```

### 2. 打开串口
```python
success = config.openSerial(
    port_text="COM1",
    baud_text="9600",
    parity_text="无校验 (None)",
    stop_bits_text="1"
)
```

### 3. 发送数据
```python
# 文本模式
config.sendData("Hello World")

# HEX模式
config.setSendHexMode(True)
config.sendData("01 03 00 00 00 01")
```

### 4. 接收数据
```python
# 通过信号连接自动更新
# config.receivedTextChanged.emit()
received = config.receivedText  # 获取接收的数据
```

### 5. Modbus操作
```python
# 启用Modbus模式
config.setModbusMode(True)

# 发送Modbus读取命令
result = config.sendModbusCommand("01", "03", "0000", "1")

# 查询设备地址
found = config.queryModbusDeviceAddresses("0000")
```

### 6. 关闭串口
```python
config.closeSerial()
```

---

## 🔧 模块API详解

### SerialConfigParser
```python
from serial_config_parser import SerialConfigParser

parser = SerialConfigParser()

# 解析参数
port = parser.extract_port_name("COM1 (USB串口)")  # "COM1"
baud = parser.parse_baud_rate("9600")              # 9600
parity = parser.parse_parity("无校验 (None)")      # QSerialPort.NoParity
stop = parser.parse_stop_bits("1")                 # QSerialPort.OneStop

# 获取显示文本
parity_text = parser.parity_label(parity)          # "None"
stop_text = parser.stop_bits_label(stop)           # "1"

# 获取选项列表
print(parser.BAUD_RATES)        # 波特率列表
print(parser.PARITY_OPTIONS)    # 校验位选项
print(parser.STOP_BITS_OPTIONS) # 停止位选项
```

### DataHandler
```python
from data_handler import DataHandler

handler = DataHandler("UTF-8")

# 编码/解码
payload = handler.build_send_payload("Hello", hex_mode=False)
text = handler.decode_raw_data(b"Hello")

# HEX模式
payload = handler.build_send_payload("01 03 00 00", hex_mode=True)
payload = handler.build_send_payload("0x01,0x03", hex_mode=True)

# 编码转换
handler.set_encoding("GBK")

# 格式化显示
formatted = handler.format_received_data(b"\x01\x03", hex_mode=True, timestamp_enabled=True)
# "[HH:MM:SS.mmm] 01 03"

# 时间戳处理
timestamped = handler.add_timestamp_to_lines("Line1\nLine2", include_timestamp=True)
# "[HH:MM:SS.mmm] Line1\n[HH:MM:SS.mmm] Line2"
```

### ModbusProtocol
```python
from modbus_protocol import ModbusProtocol

modbus = ModbusProtocol()

# CRC计算
crc = modbus.crc16(b"\x01\x03\x00\x00\x00\x01")

# 帧构建
frame = modbus.build_frame(
    dev_addr=1,      # 设备地址
    fc=0x03,         # 功能码（读保持寄存器）
    start_addr=0x0000,
    reg_len=1
)

# 帧验证
is_valid = modbus.is_valid_frame(frame)

# 预期长度
length = modbus.expected_frame_length(b"\x01\x03\x02...")

# 响应解析
result = modbus.parse_response(received_frame)
# 返回格式化的文本说明

# 参数解析
addr = modbus.parse_hex_u16("0000")  # 0
```

### SerialPortManager
```python
from serial_port_manager import SerialPortManager
from PySide6.QtSerialPort import QSerialPort, QSerialPort.NoParity, QSerialPort.OneStop

manager = SerialPortManager(serial_port_obj)

# 打开与关闭
success = manager.open("COM1", 9600, QSerialPort.NoParity, QSerialPort.OneStop)
manager.close()

# 状态查询
is_open = manager.is_open()
port_name = manager.get_port_name()
error_msg = manager.get_error_string()

# 读写
bytes_written = manager.write(b"\x01\x03")
data = manager.read_all()

# 等待操作
manager.wait_for_bytes_written(100)
manager.wait_for_ready_read(1000)

# 清空缓冲
manager.clear_read_buffer()
```

### SerialConfig (主类)
```python
from main import SerialConfig

config = SerialConfig()

# ==================== 属性 ====================
config.serialOpen              # bool - 串口开关状态
config.serialStatus            # str - 状态消息
config.receivedText            # str - 接收数据
config.timestampEnabled        # bool - 时间戳开关
config.availablePorts          # list - 可用串口
config.hasAvailablePorts       # bool - 有可用串口
config.baudRates              # list - 波特率列表
config.parityOptions          # list - 校验位列表
config.stopBitsOptions        # list - 停止位列表
config.encodingOptions        # list - 编码列表

# ==================== 串口操作 ====================
config.refreshPorts()
config.openSerial(port, baud, parity, stop_bits)
config.closeSerial()
config.toggleSerial(port, baud, parity, stop_bits)

# ==================== 数据传输 ====================
config.sendData(text)
config.clearReceivedText()
config.setEncoding(encoding)
config.setReceiveHexMode(enabled)
config.setSendHexMode(enabled)
config.setTimestampEnabled(enabled)

# ==================== Modbus操作 ====================
config.setModbusMode(enabled)
config.setModbusQueryTimeout(timeout_ms)
config.sendModbusCommand(dev_addr, fc, start_addr, reg_len)
config.queryModbusDeviceAddresses(register_addr)

# ==================== 信号 ====================
# 当属性改变时发出信号
config.serialOpenChanged.connect(on_serial_open_changed)
config.serialStatusChanged.connect(on_status_changed)
config.receivedTextChanged.connect(on_text_received)
config.availablePortsChanged.connect(on_ports_changed)
```

---

## 📊 数据流图示

### 发送流程
```
用户输入 → sendData()
         ↓
    DataHandler.build_send_payload()
         ↓
    SerialPortManager.write()
         ↓
    物理串口
```

### 接收流程
```
物理串口 → QSerialPort.readyRead()
         ↓
    _on_ready_read()
         ↓
    [Modbus mode] ModbusProtocol.parse_response()
    [Normal mode] DataHandler.decode_raw_data()
         ↓
    receivedText 更新 → receivedTextChanged信号
         ↓
    QML显示更新
```

### Modbus查询流程
```
queryModbusDeviceAddresses()
    ↓
for addr in [1..247]:
    ModbusProtocol.build_frame()
    SerialPortManager.write()
    _read_modbus_frame_blocking()
    ModbusProtocol.is_valid_frame()
    检查响应 → 累计找到的地址
    ↓
返回结果列表
```

---

## ⚙️ 配置常量

### 波特率
```
300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 
38400, 57600, 115200, 230400, 460800, 921600
```

### 校验位
- `无校验 (None)` → `QSerialPort.NoParity`
- `奇校验 (Odd)` → `QSerialPort.OddParity`
- `偶校验 (Even)` → `QSerialPort.EvenParity`
- `Mark` → `QSerialPort.MarkParity`
- `Space` → `QSerialPort.SpaceParity`

### 停止位
- `1` → `QSerialPort.OneStop`
- `1.5` → `QSerialPort.OneAndHalfStop`
- `2` → `QSerialPort.TwoStop`

### 编码格式
```
UTF-8, GBK, GB2312, ASCII, Latin-1, UTF-16
```

### Modbus支持的功能码
| FC | 说明 |
|----|------|
| 0x01 | 读取线圈 |
| 0x02 | 读取离散输入 |
| 0x03 | 读取保持寄存器 |
| 0x04 | 读取输入寄存器 |
| 0x05 | 写单个线圈 |
| 0x06 | 写单个寄存器 |
| 0x0F | 写多个线圈 |
| 0x10 | 写多个寄存器 |

---

## 🛠️ 常见用例

### 用例1：连接设备并发送命令
```python
config = SerialConfig()
config.refreshPorts()

if config.hasAvailablePorts:
    port = config.availablePorts[0].split(" (")[0]
    if config.openSerial(port, "9600", "无校验 (None)", "1"):
        config.sendData("AT\r\n")  # 发送AT命令
        # 等待接收数据...
        config.closeSerial()
```

### 用例2：Modbus读取寄存器值
```python
config = SerialConfig()
config.setModbusMode(True)
config.openSerial("COM1", "9600", "无校验 (None)", "1")

# 读取设备1的寄存器0x0000
result = config.sendModbusCommand("01", "03", "0000", "1")

# 解析结果
if "[Modbus]" in config.receivedText:
    # Modbus通信成功
    pass
```

### 用例3：查找所有Modbus设备
```python
config = SerialConfig()
config.setModbusMode(True)
config.setModbusQueryTimeout(500)  # 设置500ms超时
config.openSerial("COM1", "9600", "无校验 (None)", "1")

devices = config.queryModbusDeviceAddresses("0000")
print(devices)
# 输出: "寄存器地址 0x0000 对应设备地址: 1, 2, 3, ..."
```

### 用例4：设置显示选项
```python
config = SerialConfig()

# 启用时间戳
config.setTimestampEnabled(True)

# 启用HEX模式接收
config.setReceiveHexMode(True)

# 切换编码
config.setEncoding("GBK")

# 启用HEX模式发送
config.setSendHexMode(True)
```

---

## ✅ 测试各模块

```python
# 测试SerialConfigParser
from serial_config_parser import SerialConfigParser
parser = SerialConfigParser()
assert parser.parse_baud_rate("9600") == 9600
assert parser.extract_port_name("COM1 (USB)") == "COM1"

# 测试DataHandler
from data_handler import DataHandler
handler = DataHandler()
payload = handler.build_send_payload("01 03", hex_mode=True)
assert payload == b"\x01\x03"

# 测试ModbusProtocol
from modbus_protocol import ModbusProtocol
modbus = ModbusProtocol()
frame = modbus.build_frame(1, 0x03, 0, 1)
assert frame is not None
assert modbus.is_valid_frame(frame)

print("✓ All modules working correctly!")
```

---

## 📚 相关文档

- [README.md](./README.md) - 完整项目文档
- [main.py](./main.py) - 主程序源代码
- [serial_config_parser.py](./serial_config_parser.py) - 配置解析
- [data_handler.py](./data_handler.py) - 数据处理
- [modbus_protocol.py](./modbus_protocol.py) - Modbus协议
- [serial_port_manager.py](./serial_port_manager.py) - 串口管理

---

## 🐛 调试技巧

### 查看串口状态
```python
print(f"Serial Open: {config.serialOpen}")
print(f"Status: {config.serialStatus}")
print(f"Available Ports: {config.availablePorts}")
```

### 查看接收数据
```python
print(f"Received Text:\n{config.receivedText}")
```

### 监听信号
```python
config.receivedTextChanged.connect(lambda: print(f"New data: {config.receivedText}"))
config.serialStatusChanged.connect(lambda: print(f"Status: {config.serialStatus}"))
```

### Modbus调试
```python
config.setModbusMode(True)
result = config.sendModbusCommand("01", "03", "0000", "1")
print(f"Modbus Response:\n{config.receivedText}")
```

---

**最后更新:** 2026-03-11
