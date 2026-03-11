# MCUTool - Python模块文档

## 项目概述

MCUTool是一个基于PySide6的串口工具，支持普通串口通信和Modbus RTU协议。通过模块化设计，使代码结构清晰、易于维护和扩展。

## 架构设计

### 模块化划分

原始的大型`SerialConfig`类已被重构为5个独立模块，每个模块负责特定的功能：

```
┌─────────────────────────────────────────────┐
│         main.py (SerialConfig)              │
│   主控制类 - 协调其他模块的工作               │
└──────────────────┬──────────────────────────┘
         │
    ┌────┴──────┬──────────┬─────────────┬──────────────────┐
    │            │          │             │                  │
    ▼            ▼          ▼             ▼                  ▼
┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────────────┐
│ serial_    │ │data_     │ │modbus_   │ │serial_port_  │ │serial_config_   │
│ port_      │ │handler   │ │protocol  │ │manager       │ │parser           │
│ manager    │ │          │ │          │ │              │ │                 │
└────────────┘ └──────────┘ └──────────┘ └──────────────┘ └─────────────────┘
```

---

## 模块详细说明

### 1. **serial_config_parser.py** - 配置解析模块
**职责：** 解析和验证串口配置参数

#### 主要类：`SerialConfigParser`

**功能：**
- `extract_port_name()` - 从显示文本中提取串口号
- `parse_baud_rate()` - 解析波特率
- `parse_parity()` - 解析校验位设置
- `parse_stop_bits()` - 解析停止位设置
- `parity_label()` / `stop_bits_label()` - 将枚举转换为显示文本

**配置常量：**
- `BAUD_RATES` - 支持的波特率列表
- `PARITY_OPTIONS` - 校验位选项
- `STOP_BITS_OPTIONS` - 停止位选项

**示例：**
```python
parser = SerialConfigParser()
baud = parser.parse_baud_rate("9600")  # 返回: 9600
port = parser.extract_port_name("COM1 (USB串口)")  # 返回: "COM1"
```

---

### 2. **data_handler.py** - 数据处理模块
**职责：** 数据编码/解码和格式转换

#### 主要类：`DataHandler`

**功能：**
- `decode_raw_data()` - 将原始字节解码为字符串（支持多种编码）
- `build_send_payload()` - 构建发送有效负载（支持HEX和文本模式）
- `format_received_data()` - 格式化接收数据显示
- `add_timestamp_to_lines()` - 为数据添加时间戳

**核心特性：**
- 支持UTF-8、GBK、GB2312、ASCII、Latin-1、UTF-16编码
- HEX模式支持多种输入格式：`"01 03 00 00"`、`"0x01,0x03"`等
- 增量解码器处理不完整的多字节字符

**示例：**
```python
handler = DataHandler("UTF-8")
payload = handler.build_send_payload("01 03 00 00 00 01", hex_mode=True)
text = handler.decode_raw_data(b'\x48\x65\x6c\x6c\x6f')  # "Hello"
```

---

### 3. **modbus_protocol.py** - Modbus协议模块
**职责：** Modbus RTU协议的帧构建、解析和验证

#### 主要类：`ModbusProtocol`

**功能：**
- `crc16()` - 计算CRC-16校验码（Modbus标准）
- `build_frame()` - 构建Modbus RTU帧
- `is_valid_frame()` - 验证帧CRC校验
- `expected_frame_length()` - 计算完整帧的预期长度
- `parse_response()` - 解析响应帧为可读文本
- `parse_hex_u16()` - 解析16位HEX数值

**支持的功能码：**
- `0x01` - 读取线圈
- `0x02` - 读取离散输入
- `0x03` - 读取保持寄存器
- `0x04` - 读取输入寄存器
- `0x05` - 写单个线圈
- `0x06` - 写单个寄存器
- `0x0F` - 写多个线圈
- `0x10` - 写多个寄存器

**示例：**
```python
modbus = ModbusProtocol()
# 构建读寄存器命令 (地址1, 功能码0x03, 起始地址0x0000, 读1个寄存器)
frame = modbus.build_frame(1, 0x03, 0x0000, 1)
# 返回: bytes with CRC appended

# 验证帧
is_valid = modbus.is_valid_frame(received_frame)

# 解析响应
result_text = modbus.parse_response(received_frame)
```

---

### 4. **serial_port_manager.py** - 串口管理模块
**职责：** 串口的底层操作（打开、关闭、读写）

#### 主要类：`SerialPortManager`

**功能：**
- `open()` - 打开串口
- `close()` - 关闭串口
- `is_open()` - 检查串口状态
- `write()` - 写入数据
- `read_all()` - 读取所有可用数据
- `wait_for_ready_read()` - 等待数据可读
- `get_error_string()` - 获取错误信息

**特点：**
- 封装QSerialPort的底层操作
- 提供简洁的接口
- 便于单元测试和模拟

**示例：**
```python
manager = SerialPortManager(serial_port_obj)
if manager.open("COM1", 9600, parity, stop_bits):
    manager.write(b'\x01\x03\x00\x00')
    manager.close()
```

---

### 5. **main.py** - 主控制模块
**职责：** 协调各个模块，实现高层业务逻辑

#### 主要类：`SerialConfig(QObject)`

**核心设计：**
- **初始化方法分离：**
  - `_initialize_properties()` - 初始化所有属性
  - `_initialize_modules()` - 创建功能模块实例
  - `_initialize_serial_port()` - 连接串口信号
  - `_initialize_timers()` - 配置定时器

- **功能分组：**
  - **串口操作** - 刷新、打开、关闭、切换
  - **数据传输** - 发送、接收、编码设置
  - **Modbus操作** - 发送命令、查询设备地址
  - **内部事件处理** - 错误处理、数据接收

#### QML接口（Property和Slot）

```javascript
// Properties
- serialOpen: bool - 串口打开状态
- serialStatus: string - 状态信息
- receivedText: string - 接收数据
- timestampEnabled: bool - 时间戳开关
- availablePorts: string[] - 可用串口列表
- baudRates: string[] - 波特率列表
- parityOptions: string[] - 校验位选项
- stopBitsOptions: string[] - 停止位选项
- encodingOptions: string[] - 编码选项

// Slots (方法)
- openSerial(port, baud, parity, stopBits): bool
- closeSerial()
- toggleSerial()
- sendData(text): bool
- sendModbusCommand(addr, fc, startAddr, regLen): string
- queryModbusDeviceAddresses(regAddr): string
- refreshPorts()
- clearReceivedText()
- setEncoding(encoding)
- setReceiveHexMode(enabled)
- setSendHexMode(enabled)
- setTimestampEnabled(enabled)
- setModbusMode(enabled)
```

---

## 数据流示例

### 发送普通数据流

```
QML界面
   ↓
sendData(text)
   ↓
DataHandler.build_send_payload()
   ↓ (HEX or Text encoding)
SerialPortManager.write()
   ↓
QSerialPort
   ↓
物理串口
```

### 接收并显示数据流

```
物理串口
   ↓
QSerialPort (readyRead signal)
   ↓
_on_ready_read()
   ↓ (split by mode)
┌─────────────────┑
│ Modbus Mode     │  │ Normal Mode
├─────────────────┤
│ModbusProtocol   │  │ DataHandler
│.parse_response()│  │ .decode_raw_data()
└─────────────────┘
   ↓
_received_text (更新)
   ↓
QML显示更新
```

### Modbus地址查询流程

```
queryModbusDeviceAddresses(regAddr)
   ↓
解析HEX地址
   ↓
循环发送[1..247]的查询命令
   ↓
│ ModbusProtocol.build_frame()
│ SerialPortManager.write()
│ _read_modbus_frame_blocking()
│ ModbusProtocol.is_valid_frame()
└─> 累计找到的地址
   ↓
返回结果并添加到__received_text
```

---

## 关键改进

| 方面 | 改进前 | 改进后 |
|------|------|------|
| **代码行数** | ~750+ | ~450（主类）+ 模块 |
| **职责清晰度** | 单类混合多职责 | 每个模块单一职责 |
| **可测试性** | 困难 | 简单（可独立测试模块） |
| **可维护性** | 低（需要理解全部代码） | 高（模块相对独立） |
| **扩展性** | 困难 | 容易（添加新模块） |
| **代码复用** | 困难 | 模块可复用 |

---

## 使用指南

### 基本操作

```python
from main import SerialConfig
from PySide6.QtCore import QCoreApplication

app = QCoreApplication([])
serial_config = SerialConfig()

# 刷新串口列表
serial_config.refreshPorts()

# 打开串口
serial_config.openSerial("COM1", "9600", "无校验 (None)", "1")

# 发送数据
serial_config.sendData("Hello")

# 发送HEX数据
serial_config.setSendHexMode(True)
serial_config.sendData("01 03 00 00 00 01")

# 关闭串口
serial_config.closeSerial()
```

### Modbus操作

```python
# 启用Modbus模式
serial_config.setModbusMode(True)

# 发送Modbus命令
# 参数: 设备地址, 功能码, 起始地址, 寄存器数量
serial_config.sendModbusCommand("01", "03", "0000", "1")

# 查询设备地址
found = serial_config.queryModbusDeviceAddresses("0000")
# 返回: "寄存器地址 0x0000 对应设备地址: 1, 2, 3"
```

---

## 文件结构

```
Python/
├── main.py                      # 主控制类 (~450行)
├── serial_config_parser.py      # 配置解析模块 (~100行)
├── data_handler.py              # 数据处理模块 (~120行)
├── modbus_protocol.py           # Modbus协议模块 (~230行)
├── serial_port_manager.py       # 串口管理模块 (~80行)
├── pyproject.toml               # 项目配置
└── autogen/
    └── settings.py
```

---

## 扩展建议

1. **添加日志记录**
   - 创建 `logger_config.py` 模块
   - 集中管理日志配置

2. **支持多个串口**
   - 将 `SerialConfig` 改为管理器，支持多个 `SerialPortManager` 实例

3. **单元测试**
   - 为每个模块编写测试
   - 模块化设计使测试变得容易

4. **配置持久化**
   - 创建 `config_manager.py` 模块
   - 保存用户配置（波特率、编码等）

5. **协议扩展**
   - 创建基类 `ProtocolBase`
   - 支持Modbus、Ymodem等多种协议

---

## 技术栈

- **Python**: 3.8+
- **PySide6**: Qt框架绑定
- **QSerialPort**: 串口通信库
- **编码**: UTF-8、GBK、GB2312等

---

## 许可证

[与原项目一致]

---

## 修订历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 2.0 | 2026-03 | 重构为模块化设计，提高代码可维护性 |
| 1.0 | 原始版本 | 单类设计 |

---

## 常见问题

### Q: 为什么要分解成多个模块？
A: 提高代码可维护性、可测试性和可复用性。单个类变得过大时，分解成工作职责单一的模块是最佳实践。

### Q: 模块之间如何通信？
A: 通过方法参数和返回值，没有紧耦合的全局状态。主类 `SerialConfig` 作为协调器。

### Q: 能否单独使用某个模块？
A: 可以。例如，`ModbusProtocol` 可以在其他项目中独立使用，无需依赖QT。

### Q: 如何添加新功能？
A: 
1. 如果是数据处理相关，扩展 `DataHandler`
2. 如果是串口操作相关，扩展 `SerialPortManager`
3. 如果是配置相关，扩展 `SerialConfigParser`
4. 在 `main.py` 的 `SerialConfig` 中调用新功能

---

**最后更新：** 2026-03-11
