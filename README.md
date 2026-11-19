# STM32C5A3RGT6 + IIS3DWB10IS 三轴振动监测与边缘分析平台

**COREMAKER \| 3-Axis Vibration Monitoring & Edge Analytics**

基于 **STM32C5A3RGT6** 与 **ST IIS3DWB10IS**
的三轴振动采集与边缘智能分析项目。MCU 端完成传感器 FIFO
采集、振动特征计算、三轴 FFT、正常状态学习和异常状态判断；配套 Windows
PC 上位机通过 **USART1 + USB-UART（如 CH343）**
与设备通信，实现设备控制、实时波形/频谱显示、六位置校准、数据连续性监控及
CSV 导出。

> 本仓库包含 STM32C5A3RGT6 固件 CMake 工程和中英文双语 PC
> 上位机。当前固件支持 **2.5 / 5 / 10 / 20 kS/s** 四档采样率，最高 **20
> kS/s**。

------------------------------------------------------------------------

## 目录

- [项目功能](#项目功能)
- [硬件组成](#硬件组成)
- [系统架构](#系统架构)
- [采样率与数据处理](#采样率与数据处理)
- [六位置校准](#六位置校准)
- [PC 上位机使用](#pc-上位机使用)
- [STM32 固件编译](#stm32-固件编译)
- [串口命令](#串口命令)
- [数据协议与 CSV](#数据协议与-csv)
- [关键注意事项](#关键注意事项)
- [工程目录](#工程目录)
- [验证脚本](#验证脚本)
- [License](#license)
- [English](#english)

------------------------------------------------------------------------

## 项目功能

### MCU 固件

- 基于 **STM32C5A3RGT6（Cortex-M33，144 MHz）**。
- ST IIS3DWB10IS 三轴加速度数据采集，量程配置为 **±50 g**。
- SPI1 + DMA 读取传感器 FIFO，配合 INT1 / INT2 事件及 FIFO 状态检查。
- 支持 2.5 kHz、5 kHz、10 kHz、20 kHz 四档采样率。
- 三轴振动信号采用 **5 Hz 高通处理**，按约 **200 ms** 数据块计算特征。
- 每轴计算 RMS、峰峰值（P-P）和峰值因子（Crest Factor），共 9 项特征。
- MCU 端独立执行 **1024 点 Hann 窗三轴 FFT**，输出 X/Y/Z
  轴主峰频率及峰值幅度。
- 基于正常工况样本建立统计基线，在 MCU
  本地执行异常评分、状态判断与报警。
- ST7796 LCD 实时显示三轴振动数值、波形、采样率和学习/异常状态。
- USART1 DMA 接收与发送；通过 USB-UART 转换器向 PC
  传输原始三轴数据及诊断信息。
- 支持模型和六位置校准参数写入 MCU Flash EDATA，并在启动时读取有效记录。

### Windows PC 上位机

- **简体中文 / English** 双语界面，主窗口与六位置校准窗口支持实时切换。
- COM 端口刷新、连接和断开；串口波特率可选，默认 **6,000,000 bps**。
- 查询 MCU 当前采样率，并在固件支持范围内切换采样率。
- 开始/停止三轴数据上传。
- 启动或取消 MCU
  正常状态学习，查看学习进度、模型状态、异常分数和报警状态。
- 实时显示 X/Y/Z 三轴波形及显示窗口 RMS / P-P。
- PC 端独立 FFT 分析，支持 1024 / 2048 / 4096 / 8192 点。
- 显示 MCU FFT 结果、MCU 运行状态、LCD 刷新与串口发送队列遥测信息。
- 六位置加速度校准：六面采集、数据检查、参数求解、质量诊断及写入后读回确认。
- 显示原始实际加速度与校准后加速度。
- 检查 CRC、帧序号、样本索引、数据连续性及接收队列丢帧。
- CSV 原始数据记录，配套串口日志和诊断信息，便于问题定位。

------------------------------------------------------------------------

## 硬件组成

| 模块             | 器件 / 接口    | 说明                                      |
|:-----------------|:---------------|:------------------------------------------|
| MCU              | STM32C5A3RGT6  | Cortex-M33，144 MHz，主控制器             |
| 三轴加速度传感器 | ST IIS3DWB10IS | ±50 g 配置，SPI 接口                      |
| LCD              | ST7796         | 480 × 320，SPI 接口                       |
| 传感器通信       | SPI1 + DMA     | 传感器寄存器及 FIFO 读取                  |
| LCD 通信         | SPI2           | LCD 显示数据传输                          |
| PC 通信          | USART1         | 外接 USB-UART 转换器，当前固件默认 6 Mbps |
| 传感器中断       | INT1 / INT2    | FIFO 事件及状态辅助处理                   |

### 当前工程引脚

| 功能                          | MCU 引脚              |
|:------------------------------|:----------------------|
| Sensor SPI1 SCK / MISO / MOSI | PA5 / PA6 / PA7       |
| Sensor CS                     | PB0                   |
| Sensor INT1 / INT2            | PB1 / PB2             |
| LCD SPI2 MOSI / SCK / MISO    | PC3 / PB10 / PB14     |
| LCD CS / DC / RESET / BL      | PC1 / PC2 / PC4 / PC5 |
| USART1 TX / RX                | PA9 / PA10            |
| 用户按键 K2 / K3 / K4         | PC13 / PA15 / PE2     |

> 引脚信息来自当前 CMake 工程中的外设配置。实际 PCB
> 连接请以对应硬件原理图和板卡版本为准。LCD 是否使用 SPI2
> MISO，以具体屏幕模块连接为准。

------------------------------------------------------------------------

## 系统架构

``` text
ST IIS3DWB10IS
      │
      │ SPI1 + DMA / FIFO + INT1
      ▼
STM32C5A3RGT6
      ├── 三轴原始数据采集
      ├── 传感器校准与数据换算
      ├── 5 Hz 高通与 200 ms 特征窗口
      ├── 三轴振动特征计算（RMS / P-P / Crest Factor）
      ├── MCU FFT（1024-point Hann window）
      ├── 正常状态学习与异常判断
      ├── ST7796 LCD 实时显示
      ├── Flash EDATA 模型 / 校准参数存储
      └── USART1：命令、遥测与原始数据帧
                    │
                    │ USB-UART Adapter
                    ▼
             Windows PC Monitor
                 ├── 中文 / English UI
                 ├── 实时三轴波形
                 ├── PC 独立 FFT
                 ├── MCU 状态与异常分数
                 ├── 六位置校准
                 ├── 数据连续性 / CRC 监控
                 └── CSV / Diagnostics
```

MCU 是实时采集、特征计算和异常判断的执行端；PC
主要负责设备控制、可视化、独立复核和数据记录。PC 端 FFT 与 MCU 端 FFT
独立计算，FFT 点数和数据窗口可能不同，因此频谱主峰结果允许存在小幅差异。

------------------------------------------------------------------------

## 采样率与数据处理

### 支持的传感器采样率

|       ODR | 说明                      |
|----------:|:--------------------------|
|  2,500 Hz | 2.5 kS/s，默认启动档位    |
|  5,000 Hz | 5 kS/s                    |
| 10,000 Hz | 10 kS/s                   |
| 20,000 Hz | 20 kS/s，当前工程最高档位 |

采样率可通过 PC 上位机查询和切换。切换时 MCU
会暂停数据流、重新配置传感器 FIFO，并清理滤波、特征和 FFT
历史数据；切换完成后 PC 会等待新的连续数据。

### 振动特征计算

- 高通截止频率：约 **5 Hz**。
- 特征窗口：每个数据块约 **200 ms**，即当前采样率的 1/5。
- 每个数据块计算 X/Y/Z 三轴的 RMS、P-P 和 Crest Factor，共 9 项特征。
- MCU LCD 显示三轴 RMS、P-P 与波形包络。
- PC 上位机可根据显示窗口独立计算 RMS、P-P 和 FFT。

### MCU FFT 与 PC FFT

- MCU：1024 点 Hann 窗三轴
  FFT，采用分段处理调度，输出各轴主峰频率和峰值幅度。
- PC：独立 FFT，支持 1024 / 2048 / 4096 / 8192 点，可按分析需要调整。
- MCU 输出的 FFT 峰值幅度不是 RMS 值；查看结果时请注意幅值口径。
- 两端 FFT 点数、窗口长度和更新时间不同，结果不要求逐点完全一致。

### 正常状态学习与异常判断

1.  将传感器/设备稳定安装在被测对象上，确认设备处于具有代表性的正常工况。
2.  选择实际工作采样率，并确认安装方向、负载和运行状态稳定。
3.  MCU 先进行约 **1 秒预热**，随后采集 **150 个有效特征块**
    建立正常基线；有效学习数据约 30 秒。
4.  每个特征块包含 X/Y/Z 三轴 RMS、P-P 和 Crest Factor，共 9 项特征。
5.  监测阶段，MCU 计算当前特征相对正常基线的偏离分数，并结合连续窗口判断
    WARNING / ALARM 状态。
6.  学习完成后，配套固件会尝试保存模型；是否保存成功以 MCU 返回的 NVM
    状态为准。

**异常分数是相对正常基线的偏离指标，不是故障概率，也不能单独作为设备故障诊断结论。**
实际应用应结合原始波形、频谱、工况和现场检查综合判断。

### 模型存储说明

- 当前固件的 Flash EDATA 模型记录支持保存 2.5 / 5 / 10 / 20 kS/s
  四种采样率对应的正常基线。
- 模型加载时按当前采样率匹配，不应将某一采样率下的模型直接用于另一采样率。
- 切换采样率后，固件会尝试加载该采样率对应的有效模型；若没有匹配记录，则需要重新执行正常状态学习。
- 六位置校准参数与各采样率模型共同存储。保存新的校准参数后，旧的正常基线会被清除，需在校准完成后重新学习。

------------------------------------------------------------------------

## 六位置校准

PC 上位机提供六位置静态加速度校准流程，MCU
负责采集、求解、检查和保存校准参数。

### 校准流程

1.  断开设备与被测对象的动态连接，将传感器放置在稳定、静止的平台上。
2.  在 PC 上位机打开”六位置校准”窗口，查询 MCU 校准状态。
3.  依次完成 X+、X-、Y+、Y-、Z+、Z- 六个方向的采集。
4.  每个方向按固件配置采集约 **5 秒** 数据；采集期间保持设备静止。
5.  六面数据齐全后执行参数求解，查看六面残差、正反面对称性及综合质量检查结果。
6.  检查通过后执行保存；等待 MCU 返回保存结果，并由 PC
    重新读取参数确认。
7.  校准完成后，将设备安装回正常工况，并重新进行正常状态学习。

### 校准范围与限制

- 当前实现为三轴加速度计的六位置静态校准，主要估计各轴零偏和比例系数。
- 当前算法不包含交叉轴耦合补偿、温度补偿或频率响应补偿。
- 校准精度受平台水平度、六面姿态、静止程度、安装应力和传感器本身影响。
- 校准结果应结合现场标定条件和目标精度要求进行验证，不能仅凭”校准通过”推断整机达到某个角度精度指标。

------------------------------------------------------------------------

## PC 上位机使用

### 环境要求

- Windows 10 / 11
- 64-bit Python（建议 Python 3.10 或更新版本）
- USB-UART 转换器及对应驱动（例如 CH343）
- 连接至 MCU USART1 的 TX / RX / GND

PC 依赖位于 `PC/requirements.txt`：

- PySide6
- pyqtgraph
- numpy
- pyserial

### 启动步骤

1.  下载或克隆本仓库，并完整保留目录结构。

2.  安装 64-bit Python。

3.  连接 USB-UART 转换器，确认 TX、RX、GND 接线正确。

4.  进入 `PC/` 文件夹。

5.  首次运行前安装依赖：

    ``` bash
    python -m pip install -r requirements.txt
    ```

6.  双击 `start.bat`，或在命令行运行：

    ``` bash
    python app.py
    ```

7.  软件启动后，在界面顶部选择 `简体中文` 或 `English`。

8.  点击刷新串口，选择连接 MCU USART1 的 COM 端口。

9.  当前固件默认串口波特率为 **6,000,000 bps**，PC 端默认也选择
    6,000,000 bps。

10. 点击连接，查询 MCU 当前采样率；按需选择采样率并应用。

11. 点击开始采集查看实时波形和频谱；需要记录数据时点击”保存 CSV”。

12. 需要正常状态监测时，先固定安装设备并确认工况正常，再启动”学习正常状态”。

> **重要：当前固件 USART1 默认配置为 6 Mbps。** PC
> 界面的波特率选项只设置 PC 串口，不会自动修改
> MCU。两端波特率必须一致；如果修改 MCU UART 配置，也必须同步修改 PC
> 设置。请勿将 USB-UART 转换器的 COM 口与 ST-Link 的调试串口混淆。

### 六位置校准操作

1.  连接设备并确认 MCU 固件版本与校准协议匹配。
2.  停止动态采集，确保传感器静止。
3.  点击”六位置校准”，开始新校准会话。
4.  按界面提示逐面摆放并采集六个方向。
5.  六面采集完成后执行求解，检查质量诊断结果。
6.  确认结果通过后保存，并等待参数读回确认。
7.  校准保存后，重新进行正常状态学习。

校准过程中请勿断开串口或关闭程序。保存操作进行时请等待 MCU
返回最终结果。

### CSV 数据字段

| 字段                    | 含义                                 |
|:------------------------|:-------------------------------------|
| `seq`                   | 数据包序号                           |
| `sample_index`          | 样本索引                             |
| `fs_Hz`                 | 采样率（Hz）                         |
| `flags`                 | 数据包标志，包含连续性/间断提示      |
| `raw_x / raw_y / raw_z` | 三轴原始传感器数据                   |
| `x_mg / y_mg / z_mg`    | 按传感器灵敏度换算的三轴加速度（mg） |

PC 端 CSV
保存的是原始采样数据及其基础单位换算值。校准后加速度显示属于上位机/MCU
的校准显示数据，不应将 CSV 中的 `x_mg / y_mg / z_mg`
字段误认为已经完成六位置校准的结果。

------------------------------------------------------------------------

## STM32 固件编译

本仓库提供基于 CMake 的 STM32C5A3RGT6 工程，目标配置为
`debug_GCC_STM32C5A3RGT6`。

### 编译环境

- CMake 3.30 或更新版本
- Ninja
- 与工程工具链文件匹配的 GNU Arm Embedded Toolchain（工程配置为 GCC
  14.3.1）
- STM32C5 系列 CMSIS / HAL 相关工程文件

### 编译步骤

1.  安装 CMake、Ninja 和对应 ARM GCC 工具链，并配置好系统 PATH。

2.  进入固件工程目录：

    ``` bash
    cd STM32C5A3_IIS3DWB10IS_cmake
    ```

3.  配置工程：

    ``` bash
    cmake --preset debug_GCC_STM32C5A3RGT6
    ```

4.  编译工程：

    ``` bash
    cmake --build --preset debug_GCC_STM32C5A3RGT6
    ```

5.  编译完成后，在对应 `build/` 配置目录中检查生成的 ELF / HEX / BIN
    文件。

6.  使用 ST-Link 或对应下载工具烧录到 STM32C5A3RGT6 硬件。

> 工程使用 CMake Presets 和 Ninja
> 构建。不同电脑的工具链安装路径、调试器配置和下载设置可能不同；首次编译请检查本机
> GCC、CMake 与 Ninja 环境。实际硬件烧录及外设连接仍需在目标板上验证。

------------------------------------------------------------------------

## 串口命令

PC 上位机通常会自动查询采样率和设备状态。开发调试时，也可通过 USART1
发送以下 ASCII 文本命令（命令以换行结束）。

### 基础控制

| 命令                          | 功能                              |
|:------------------------------|:----------------------------------|
| `PING`                        | 通信测试，设备返回 `PONG`         |
| `START`                       | 开始向 PC 上传三轴原始采样数据    |
| `STOP`                        | 停止向 PC 上传采样数据            |
| `STATUS`                      | 查询设备通信、发送队列及 LCD 状态 |
| `RATE?`                       | 查询当前采样率及支持档位          |
| `RATE 2500`                   | 设置为 2500 Hz                    |
| `RATE 5000`                   | 设置为 5000 Hz                    |
| `RATE 10000`                  | 设置为 10000 Hz                   |
| `RATE 20000`                  | 设置为 20000 Hz                   |
| `LEARN`                       | 启动 MCU 正常状态学习             |
| `CANCEL`                      | 取消当前正常状态学习              |
| `RESET`                       | 重置 MCU 振动处理与 FFT 状态      |
| `UP` / `DOWN` / `OK` / `BACK` | 模拟 LCD 按键操作                 |

### 六位置校准

| 命令            | 功能                                      |
|:----------------|:------------------------------------------|
| `CAL INFO`      | 查询校准协议与固件能力信息                |
| `CAL STATUS`    | 查询校准会话、采集进度及当前参数          |
| `CAL DATA`      | 查询六面数据及质量诊断信息                |
| `CAL MONITOR 1` | 开启实时静态加速度监视                    |
| `CAL MONITOR 0` | 关闭实时静态加速度监视                    |
| `CAL BEGIN`     | 开始新的六位置校准会话                    |
| `CAL FACE X+`   | 采集 X+ 面；其他方向为 X-、Y+、Y-、Z+、Z- |
| `CAL SOLVE`     | 根据六面数据求解并检查校准参数            |
| `CAL SAVE`      | 保存已求解的校准参数                      |
| `CAL CANCEL`    | 取消当前校准会话                          |

> 采样率切换、正常学习和六位置校准之间存在互斥条件。若 MCU 返回 BUSY
> 或校准会话状态错误，请先查询 `STATUS` /
> `CAL STATUS`，按当前操作状态完成或取消流程，不要连续发送重复命令。

------------------------------------------------------------------------

## 数据协议与 CSV

MCU 通过 USART1 发送 ASCII 状态/诊断文本和二进制采样帧。PC
上位机使用协议解析器区分两类数据。

### 二进制采样帧

- 帧头：`A5 5A C3 3C`
- 协议版本：V1
- 每帧样本数：32 组三轴样本
- 每组三轴数据：X / Y / Z 三个 `int32`
- 帧内包含序号、采样率、首样本索引和数据标志
- 帧尾：CRC32 校验值

PC
端会检查帧头、协议字段、CRC、帧序号和样本索引。检测到间断或错误时，会清理受影响的连续分析窗口并记录诊断状态，避免将不连续数据当作完整连续波形使用。

### 测试脚本

`PC/` 目录中的 `test_10k.py`、`test_20k.py`
等脚本包含协议解析、采样率字段和数据帧处理测试。它们可用于开发阶段的主机侧验证和联调，不等同于所有采样率下的长期实机稳定性测试。

------------------------------------------------------------------------

## 关键注意事项

- **串口波特率必须匹配。** 当前 MCU USART1 固件配置为 6 Mbps，PC
  端默认也为 6 Mbps；修改任意一端后必须同步另一端。
- **使用正确的 COM 口。** PC 通信使用 USB-UART 转换器连接
  USART1，不是原生 USB FS CDC。
- **先固定安装，再学习。**
  学习过程中不要移动设备、改变安装方向或改变被测设备工况。
- **先确定采样率，再开始学习。** 切换采样率后应确认 MCU
  实际速率和模型状态；无匹配模型时重新学习。
- **校准时必须静止。**
  六位置校准每一面需要稳定采集，运动、倾斜或振动可能导致采集失败或质量检查不通过。
- **校准保存后重新学习。**
  新校准参数保存会清除原有正常基线模型，需在目标采样率和正常工况下重新建立基线。
- **异常分数不是故障概率。**
  本项目使用统计特征正常基线模型，并非神经网络，也不替代专业设备诊断或安全保护系统。
- 如果发生 FIFO overrun、UART 发送队列溢出、CRC 错误或样本间断，请保留
  CSV、串口日志和界面截图，并降低采样率进行对照测试。
- 高采样率运行效果与 USB-UART 转换器、线缆、接地、PC
  串口驱动和目标板硬件实现有关，建议在实际系统中完成持续运行测试。

------------------------------------------------------------------------

## 工程目录

``` text
.
├── PC/
│   ├── app.py
│   ├── i18n.py
│   ├── calibration.py
│   ├── calibration_ui.py
│   ├── detection.py
│   ├── learning_control.py
│   ├── protocol.py
│   ├── telemetry.py
│   ├── requirements.txt
│   ├── start.bat
│   ├── test_10k.py
│   ├── test_20k.py
│   ├── test_calibration.py
│   ├── test_compact_xyz.py
│   ├── test_firmware_link.py
│   ├── test_learning_control.py
│   ├── test_monitor.py
│   └── test_bilingual_ui.py
│
├── STM32C5A3_IIS3DWB10IS.ioc2
│
└── STM32C5A3_IIS3DWB10IS_cmake/
    ├── main.c / main.h
    ├── sensor_app.c / sensor_app.h
    ├── iis3dwb10is_reg.c / iis3dwb10is_reg.h
    ├── vibration.c / vibration.h
    ├── mcu_fft.c / mcu_fft.h
    ├── st7796.c / st7796.h
    ├── lcd_ui.c / lcd_ui.h
    ├── calibration.inc
    ├── model_store.inc
    ├── fft_tables.inc
    ├── CMakeLists.txt
    ├── CMakePresets.json
    ├── cmake/
    ├── generated/
    ├── arch/
    ├── stm32c5xx_drivers/
    └── stm32c5xx_dfp/
```

------------------------------------------------------------------------

## 验证脚本

`PC/` 目录包含开发验证脚本，例如：

- `test_10k.py`：10 kS/s 相关协议解析与数据帧测试。
- `test_20k.py`：20 kS/s 相关协议解析与数据帧测试。
- `test_calibration.py`：六位置校准解析、状态与流程测试。
- `test_compact_xyz.py`：三轴数据帧处理测试。
- `test_firmware_link.py`：固件通信文本与协议解析测试。
- `test_learning_control.py`：正常学习和取消学习控制逻辑测试。
- `test_monitor.py`：监测状态处理测试。
- `test_bilingual_ui.py`：主界面及校准窗口中英文切换测试。

运行硬件相关联调前，请连接对应设备，并确认 MCU
固件版本、串口端口、波特率和采样率正确。

------------------------------------------------------------------------

## License

当前仓库中的 STM32 HAL、CMSIS、Device Family Pack
及其他第三方组件保留各自原有许可文件。若仓库未提供独立的项目级 `LICENSE`
文件，请勿将其理解为第三方组件或本项目代码可不受限制地复制、修改或商业使用。用于二次开发或商业项目之前，请核实各组件许可，并为本项目补充明确的项目级
License。

------------------------------------------------------------------------

# English

## Overview

A 3-axis vibration acquisition and edge analytics platform based on
**STM32C5A3RGT6** and **ST IIS3DWB10IS**.

The MCU handles sensor FIFO acquisition, vibration feature extraction,
3-axis FFT, normal-state learning, anomaly evaluation, LCD display, and
Flash storage. A bilingual Windows PC application communicates with the
board through **USART1 and a USB-to-UART adapter** for device control,
waveform and spectrum visualization, six-position calibration, data
continuity monitoring, and CSV recording.

The current firmware supports **2.5 / 5 / 10 / 20 kS/s**, with a maximum
configured sampling rate of **20 kS/s**.

### Key Features

- STM32C5A3RGT6 Cortex-M33 MCU running at 144 MHz.
- IIS3DWB10IS 3-axis acceleration acquisition, configured for ±50 g.
- SPI1 + DMA sensor communication with FIFO and INT1 / INT2 event
  handling.
- Selectable ODR: 2.5 / 5 / 10 / 20 kHz.
- 5 Hz high-pass processing and approximately 200 ms feature windows.
- RMS, peak-to-peak, and crest-factor features for each axis.
- 1024-point Hann-window FFT on the MCU, reporting dominant frequency
  and peak amplitude for X/Y/Z.
- On-device normal-baseline learning and anomaly scoring.
- ST7796 480 × 320 SPI display.
- USART1 DMA communication with a USB-UART adapter.
- Chinese / English Windows PC application with live language switching.
- PC waveform plots, independent FFT, six-position calibration, CSV
  recording, and diagnostics.
- Flash EDATA storage for calibration parameters and
  sampling-rate-specific normal models.

### Hardware Interface

| Function                 | MCU Interface / Pins  |
|:-------------------------|:----------------------|
| Sensor SPI1              | PA5 / PA6 / PA7       |
| Sensor CS                | PB0                   |
| Sensor INT1 / INT2       | PB1 / PB2             |
| LCD SPI2                 | PC3 / PB10 / PB14     |
| LCD CS / DC / RESET / BL | PC1 / PC2 / PC4 / PC5 |
| USART1 TX / RX           | PA9 / PA10            |
| PC connection            | USB-UART adapter      |

### PC Quick Start

1.  Install 64-bit Python and the required dependencies.

2.  Connect the USB-UART adapter to MCU USART1 (TX, RX, and GND).

3.  Open the `PC/` directory.

4.  Install dependencies:

    ``` bash
    python -m pip install -r requirements.txt
    ```

5.  Run `start.bat`, or execute:

    ``` bash
    python app.py
    ```

6.  Select **简体中文** or **English** from the language selector.

7.  Refresh COM ports and select the adapter connected to USART1.

8.  Use the default baud rate of **6,000,000 bps**, matching the current
    firmware configuration.

9.  Connect, query the sampling rate, and apply the required ODR.

10. Start acquisition for live waveforms and spectrum analysis. Use
    **Save CSV** to record raw samples.

11. For anomaly monitoring, secure the sensor in a representative normal
    operating condition and start **Learn Normal State**.

### Six-Position Calibration

The PC application provides a six-position static accelerometer
calibration workflow:

1.  Keep the sensor stationary on a stable surface.
2.  Start a new calibration session.
3.  Capture X+, X-, Y+, Y-, Z+, and Z- orientations.
4.  Each face is captured for approximately 5 seconds.
5.  Solve the calibration parameters and review residual and quality
    checks.
6.  Save the parameters and wait for MCU confirmation and read-back.
7.  Relearn the normal baseline after calibration.

The current implementation estimates per-axis offset and scale. It does
not implement cross-axis, temperature, or frequency-response
compensation.

### Sampling and Anomaly Detection

- Supported rates: 2.5 / 5 / 10 / 20 kS/s.
- High-pass cutoff: approximately 5 Hz.
- Feature window: approximately 200 ms.
- Nine features: X/Y/Z RMS, peak-to-peak, and crest factor.
- Learning: approximately 1 second of warm-up followed by 150 valid
  feature blocks (approximately 30 seconds).
- The anomaly score represents deviation from the learned normal
  baseline. It is not a failure probability or a standalone fault
  diagnosis.

The firmware stores rate-specific baseline models in Flash EDATA when
storage is available. After changing the ODR, the firmware attempts to
load a matching model; if none is available, run normal-state learning
again. Saving new six-position calibration parameters clears the
previous normal models, so relearning is required.

### Firmware Build

The firmware uses CMake Presets and Ninja.

Requirements:

- CMake 3.30 or later
- Ninja
- GNU Arm Embedded Toolchain matching the project configuration (GCC
  14.3.1)

Build commands:

``` bash
cd STM32C5A3_IIS3DWB10IS_cmake
cmake --preset debug_GCC_STM32C5A3RGT6
cmake --build --preset debug_GCC_STM32C5A3RGT6
```

Check the generated files in the corresponding `build/` directory and
flash the target board using ST-Link or the appropriate programming
tool.

### Serial Commands

Commands are ASCII text lines terminated by a newline.

| Command                                  | Function                                   |
|:-----------------------------------------|:-------------------------------------------|
| `PING`                                   | Communication test                         |
| `START` / `STOP`                         | Start / stop raw sample streaming          |
| `STATUS`                                 | Query device communication and LCD status  |
| `RATE?`                                  | Query current and supported sampling rates |
| `RATE 2500` / `5000` / `10000` / `20000` | Set the sensor ODR                         |
| `LEARN`                                  | Start normal-state learning                |
| `CANCEL`                                 | Cancel normal-state learning               |
| `RESET`                                  | Reset vibration processing and FFT state   |
| `UP` / `DOWN` / `OK` / `BACK`            | Simulate LCD key operations                |
| `CAL INFO`                               | Query calibration protocol information     |
| `CAL STATUS` / `CAL DATA`                | Query calibration status and captured data |
| `CAL BEGIN`                              | Start a six-position calibration session   |
| `CAL FACE X+` etc.                       | Capture one of the six orientations        |
| `CAL SOLVE`                              | Solve and validate calibration parameters  |
| `CAL SAVE`                               | Save the calibration parameters            |
| `CAL CANCEL`                             | Cancel the calibration session             |

### Data Protocol and CSV

The MCU sends ASCII diagnostic messages and binary sample frames over
USART1. Each binary frame contains:

- Header: `A5 5A C3 3C`
- Protocol version and frame type
- Sequence number and sensor sampling rate
- First sample index and frame flags
- 32 samples of raw X/Y/Z `int32` data
- CRC32 checksum

The PC parser checks frame structure, CRC, sequence numbers, sample
indices, and continuity. CSV files include sequence number, sample
index, sampling rate, flags, raw XYZ values, and basic acceleration
conversion in mg.

### Important Notes

- The current firmware USART1 baud rate is **6 Mbps**. The PC serial
  setting must match it; changing the PC setting alone does not change
  the MCU UART.
- The PC connection is USART1 through a USB-UART adapter, not native USB
  FS CDC.
- Secure the sensor before normal-state learning. Do not move or
  reorient it during learning.
- Confirm the actual ODR and model state after changing the sampling
  rate.
- Keep the sensor stationary during six-position calibration.
- Relearn normal baselines after saving new calibration parameters.
- The anomaly score is a statistical deviation metric, not a failure
  probability.
- High-rate performance depends on the USB-UART adapter, wiring,
  grounding, host driver, and target hardware. Perform sustained tests
  on the actual system before deployment.

**COREMAKER — Shenzhen Xintu Chuangke Electronic Technology Co., Ltd.**
