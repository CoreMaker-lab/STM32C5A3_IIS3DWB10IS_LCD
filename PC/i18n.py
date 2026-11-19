"""Lightweight Chinese/English UI localization for the PC vibration monitor."""
from __future__ import annotations

import weakref
from collections import deque
from PySide6 import QtWidgets

_LANGUAGE = "zh"
_WIDGETS = []
_ORIGINAL_GROUPBOX = QtWidgets.QGroupBox

# Phrase-level replacements also cover dynamic status strings containing numbers.
_PAIRS = [
    ("三轴振动监测", "3-Axis Vibration Monitor"),
    ("V2.5 · 20K · CH343高波特率", "V2.5 · 20K · CH343 High Baud Rate"),
    ("刷新串口", "Refresh Ports"),
    ("断开连接后选择；MCU串口必须设为相同波特率。选择此项不会自动修改MCU。", "Select while disconnected. The MCU UART must use the same baud rate; this setting does not change the MCU."),
    ("连接已结束，请断开后重连", "Connection ended. Disconnect and reconnect."),
    ("等待串口线程退出", "Waiting for the serial thread to stop"),
    ("串口指令未完整写出", "Serial command was not fully transmitted"),
    ("已打开串口：", "Serial port opened: "),
    ("，配置波特率 ", ", baud rate "),
    (" bps", " bps"),
    ("错误: ", "Error: "),
    ("连接已关闭", "Connection closed"),
    ("CSV 保存中", "CSV recording"),
    ("CSV 已关闭", "CSV closed"),
    ("保存完整原始采样", "Save Full Raw Samples"),
    ("结束保存", "Stop Saving"),
    ("保存 CSV", "Save CSV"),
    ("开始采集", "Start Acquisition"),
    ("停止采集", "Stop Acquisition"),
    ("连接", "Connect"),
    ("断开", "Disconnect"),
    ("传感器采样率", "Sensor Sample Rate"),
    ("等待 MCU 支持列表", "Waiting for MCU supported rates"),
    ("查询采样率", "Query Sample Rate"),
    ("应用采样率", "Apply Sample Rate"),
    ("等待 MCU 查询结果；切换后需重新学习", "Waiting for MCU response; relearn after changing the rate"),
    ("六位置校准", "Six-Position Calibration"),
    ("原始实际加速度", "Raw Acceleration"),
    ("校准后加速度", "Calibrated Acceleration"),
    ("约0.5秒均值", "Approx. 0.5 s average"),
    ("包含重力；不是振动RMS或瞬时峰值。", "Includes gravity; it is neither vibration RMS nor an instantaneous peak."),
    ("含重力；校准后值已应用设备参数。", "Includes gravity; device calibration parameters are applied to the calibrated values."),
    ("含重力；两行分别以原始/已校准报文为准。", "Includes gravity; raw and calibrated rows are based on their respective MCU messages."),
    ("等待原始数据", "Waiting for raw data"),
    ("尚未确认校准", "Calibration not confirmed"),
    ("MCU版本：等待核验", "MCU version: awaiting verification"),
    ("MCU 本地正常状态学习", "MCU Local Normal-State Learning"),
    ("学习正常状态（30秒）", "Learn Normal State (30 s)"),
    ("取消学习", "Cancel Learning"),
    ("等待设备结果", "Waiting for device data"),
    ("异常分数：", "Anomaly Score: "),
    ("模型：", "Model: "),
    ("未知（无最新结果）", "Unknown (no recent result)"),
    ("未知", "Unknown"),
    ("已建立（MCU）", "Created (MCU)"),
    ("未建立", "Not Created"),
    ("固定安装并确认设备正常后学习；约1秒预热＋30秒有效数据。支持配套固件保存模型；是否保存成功以 MCU 存储结果为准。", "Securely mount the device and confirm normal operation before learning. Allow about 1 s for warm-up plus 30 s of valid data. Model saving requires compatible firmware; the MCU storage status is authoritative."),
    ("MCU FFT · 1024点 / Hann窗 / 峰值幅度", "MCU FFT · 1024 Points / Hann Window / Peak Amplitude"),
    ("等待 MCU FFT 结果", "Waiting for MCU FFT results"),
    ("以下频谱曲线由 PC 计算；两端 FFT 点数不同，主峰可能略有差异。", "The spectrum below is calculated on the PC. Different FFT lengths may cause slight peak differences."),
    ("模型存储：等待 MCU 状态", "Model Storage: waiting for MCU status"),
    ("显示时长", "Display Duration"),
    ("去均值（观察微振动）", "Remove Mean (view micro-vibration)"),
    ("FFT 点数", "FFT Points"),
    ("跟随时间窗", "Follow Time Window"),
    ("Y轴自动量程", "Auto Y-Axis Scale"),
    ("恢复视图", "Reset View"),
    ("取消跟随后：滚轮缩放、左键拖动；频谱可独立缩放。", "When follow is disabled: use the mouse wheel to zoom and left-drag to pan. The spectrum can be zoomed independently."),
    ("等待数据；RMS/峰峰值基于所选显示窗口，去除均值。", "Waiting for data. RMS and peak-to-peak values use the selected display window after mean removal."),
    ("三轴加速度波形", "3-Axis Acceleration Waveform"),
    ("加速度", "Acceleration"),
    ("相对时间", "Relative Time"),
    ("频谱（Hann 窗，去直流）", "Spectrum (Hann Window, DC Removed)"),
    ("幅值", "Amplitude"),
    ("频率", "Frequency"),
    ("MCU 异常分数（偏差指标，非故障概率；虚线为判断阈值）", "MCU Anomaly Score (deviation metric, not failure probability; dashed line is the decision threshold)"),
    ("异常分数", "Anomaly Score"),
    ("MCU 运行状态：等待上报（约5秒一次）", "MCU Runtime: waiting for telemetry (about every 5 s)"),
    ("主循环忙碌率估计：扣除循环末尾HAL_Delay时间，包含SPI同步等待；不是精确CPU执行占用率。FFT/LCD为本统计周期的累计前台耗时，毫秒精度。队列峰值为本次启动累计值。", "Main-loop busy estimate excludes the final HAL_Delay and includes synchronous SPI waits; it is not an exact CPU utilization measurement. FFT/LCD values are accumulated foreground time for this reporting period (ms). Queue peak is accumulated since startup."),
    ("未连接", "Disconnected"),
    ("原始值 · 含零偏", "Raw · Includes Offset"),
    ("未收到 / 超时", "Not Received / Timed Out"),
    ("已应用设备校准", "Device Calibration Applied"),
    ("尚未校准", "Not Calibrated"),
    ("请先完成六位置校准并保存；此处不把原始值当作校准后值。", "Complete and save six-position calibration first. Raw values are not presented as calibrated values."),
    ("约0.5秒均值，含重力；校准后值仅采用MCU明确标记的结果。", "Approx. 0.5 s average including gravity. Calibrated values are shown only when explicitly marked by the MCU."),
    ("请先结束 CSV 保存、采样率切换或正常状态学习。", "Stop CSV recording, sample-rate switching, or normal-state learning first."),
    ("请先选择串口。", "Select a serial port first."),
    ("串口", "Serial Port"),
    ("校准会话或校准操作尚未结束，请先完成或取消校准。", "A calibration session or operation is still active. Complete or cancel calibration first."),
    ("正在切换采样率，请等待完成。", "Sample-rate change in progress. Please wait."),
    ("串口未连接，学习指令未发送。", "Serial port is not connected. The learning command was not sent."),
    ("结果超时", "Telemetry Timed Out"),
    ("学习中，请保持固定安装和正常运行。", "Learning in progress. Keep the device securely mounted and operating normally."),
    ("检测在 MCU 本地执行；超过阈值需连续5个窗口才报警，恢复也需连续正常窗口。", "Detection runs locally on the MCU. An alarm requires five consecutive windows above the threshold; recovery also requires consecutive normal windows."),
    (" 当前分数不是故障概率；报警与恢复均有连续窗口确认。", " The score is not a failure probability. Both alarms and recovery require consecutive-window confirmation."),
    ("正在查询 MCU 实际采样率及支持档位…", "Querying the actual MCU sample rate and supported settings…"),
    ("已请求 ", "Requested "),
    (" Hz，等待 MCU 确认；原学习模型需重新学习", " Hz. Waiting for MCU confirmation; the previous model must be relearned."),
    ("MCU 当前 ", "MCU current rate: "),
    (" Hz；切换成功后需重新学习。", " Hz; relearn after a successful change."),
    ("确认速率不匹配：请求 ", "Sample-rate confirmation mismatch: requested "),
    (" Hz，设备返回 ", " Hz, device returned "),
    (" Hz；请重新查询。", " Hz. Query again."),
    ("已确认切换为 ", "Confirmed sample rate: "),
    (" Hz；连续数据缓存已清空，请重新学习。", " Hz. Continuous-data buffers were cleared; please relearn."),
    ("MCU 采样率操作失败：", "MCU sample-rate operation failed: "),
    ("切换未收到确认，实际速率未知；请重新查询，界面未假定切换成功。", "No confirmation received. The actual rate is unknown. Query again; the UI has not assumed the change succeeded."),
    ("未收到采样率能力回复：当前固件可能尚不支持 RATE 指令。原有采集可继续。", "No sample-rate capability response. This firmware may not support RATE commands yet. Existing acquisition can continue."),
    ("MCU 运行状态：上报超时", "MCU Runtime: telemetry timed out"),
    ("MCU 忙碌≈", "MCU Busy ≈"),
    ("  |  FFT调度 ", "  |  FFT scheduling "),
    (" ms / ", " ms / "),
    ("s  |  LCD ", "s  |  LCD "),
    (" ms，最长 ", " ms, max "),
    ("，", ", "),
    (" FPS  |  TX队列 ", " FPS  |  TX queue "),
    ("，峰值 ", ", peak "),
    ("MCU FFT：结果超时", "MCU FFT: result timed out"),
    ("MCU FFT：等待设备结果", "MCU FFT: waiting for device data"),
    ("以下频谱由 PC 计算；暂无有效 MCU FFT 结果。", "The spectrum below is calculated on the PC; no valid MCU FFT result is available yet."),
    ("MCU FFT：等待完整连续数据窗口", "MCU FFT: waiting for a complete continuous-data window"),
    ("已完成 ", "Completed "),
    (" 组 · 跳过 ", " windows · skipped "),
    (" 个分析窗口", " analysis windows"),
    (" · 发布后样本时间 ", " · sample age at publication "),
    (" ms · 调度批次最大 ", " ms · maximum scheduling batch "),
    ("；幅值为峰值，非 RMS。", "; amplitude is peak, not RMS."),
    (" 【结果超过1秒未更新】", " [No update for over 1 s]"),
    ("模型存储：状态超时", "Model Storage: status timed out"),
    ("模型存储：初始化失败 ", "Model Storage: initialization failed "),
    ("本次启动已从 Flash 恢复模型", "Model restored from Flash during this startup"),
    ("本次启动未恢复模型", "No model restored during this startup"),
    ("启动加载失败 ", "Startup load failed "),
    ("本次启动已成功保存 ", "Successful saves this startup: "),
    (" 次", " times"),
    ("本次启动尚无成功保存", "No successful save during this startup"),
    ("；最近保存错误 ", "; most recent save error "),
    ("模型存储：", "Model Storage: "),
    ("；Flash 序号 ", "; Flash sequence "),
    ("。", "."),
    ("接收中", "Receiving"),
    ("已连接，等待采样数据", "Connected, waiting for samples"),
    ("串口 ", "Serial "),
    (" | 样本 ", " | Samples "),
    (" | CRC/格式错误 ", " | CRC/format errors "),
    (" | 不连续事件 ", " | Discontinuity events "),
    (" | 显示队列丢帧 ", " | Display queue drops "),
    (" | CSV ", " | CSV "),
    (" 点", " samples"),
    ("FFT 等待连续数据 ", "FFT waiting for continuous data "),
    ("PC 主峰: ", "PC peaks: "),
    (" · Δf=", " · Δf="),
    ("退出前请先取消校准；保存过程中请等待最终确认。", "Cancel calibration before exiting. If saving is in progress, wait for final confirmation."),
    # Six-position calibration dialog
    ("六位置校准 · MCU 参数保存", "Six-Position Calibration · Save Parameters to MCU"),
    ("停机后操作：依次让 X+、X−、Y+、Y−、Z+、Z− 朝上。每面放稳后采集 5 秒，收到完成结果再换面。\n校准由 MCU 计算和应用；本软件不会对收到的数据重复校正。", "Perform this procedure with the machine stopped. Orient X+, X−, Y+, Y−, Z+, and Z− upward in sequence. Stabilize each face and capture for 5 seconds; move to the next face only after completion is reported.\nCalibration is calculated and applied by the MCU. This software does not recalibrate the received data."),
    ("未校准三轴读数 · 约0.5秒均值", "Uncalibrated 3-Axis Readings · Approx. 0.5 s Average"),
    ("等待实时数据", "Waiting for live data"),
    ("这些数值包含重力和零偏；校准前不要求某轴恰好为±1000 mg、其余轴为0。请按传感器轴向标识摆放。", "These values include gravity and offset. Before calibration, an axis is not expected to be exactly ±1000 mg with the other axes at zero. Position the sensor according to its axis markings."),
    ("开始新校准", "Start New Calibration"),
    ("查询设备状态", "Query Device Status"),
    ("取消本次校准", "Cancel Calibration"),
    ("朝上方向", "Face Up"),
    ("原始 X (mg)", "Raw X (mg)"),
    ("原始 Y (mg)", "Raw Y (mg)"),
    ("原始 Z (mg)", "Raw Z (mg)"),
    ("校正残差 X / Y / Z (mg)", "Correction Residual X / Y / Z (mg)"),
    ("结果", "Result"),
    ("待采集", "Not Captured"),
    ("采集所选面（5秒）", "Capture Selected Face (5 s)"),
    ("本面原始均值：", "Current Face Raw Mean: "),
    ("计算并检查六面结果", "Calculate and Check Six-Face Results"),
    ("零偏/比例：待求解；综合一致性：待核验。旁轴残差为姿态提示。", "Offset/scale: pending calculation; overall consistency: pending verification. Cross-axis residuals are posture guidance."),
    ("写入设备并清除旧学习模型", "Write to Device and Clear Previous Learning Model"),
    ("保存后需在正常运行工况下重新学习。六面校准不替代高频振动幅值/频响校验。", "After saving, relearn under normal operating conditions. Six-face calibration does not replace high-frequency vibration amplitude/frequency-response verification."),
    ("静止（仍需保持到本面采集结束）", "Stable (keep still until this face capture is complete)"),
    ("检测到运动 / 振动，请放稳", "Motion / vibration detected. Stabilize the sensor."),
    ("  |  标准差 X/Y/Z：", "  |  Standard deviation X/Y/Z: "),
    ("实时数据未到达或已超时；需配套 MCU_Calibration_V1_4，且无需点击“开始采集”。", "Live data has not arrived or has timed out. MCU_Calibration_V1_4 firmware is required; do not click “Start Acquisition.”"),
    ("待求解核验", "Pending Calculation / Verification"),
    ("采集中…", "Capturing…"),
    ("一致性超限", "Consistency Limit Exceeded"),
    ("姿态提示", "Posture Warning"),
    ("已核验", "Verified"),
    ("已采集", "Captured"),
    ("明细待返回", "Details Pending"),
    ("重采所选面", "Recapture Selected Face"),
    ("采集所选面", "Capture Selected Face"),
    ("（5秒，其余面保留）", "(5 s; other faces are retained)"),
    ("本面采集 %p%", "Capturing This Face %p%"),
    ("已采集 ", "Captured "),
    ("/6 面", "/6 faces"),
    ("最近一面原始均值：", "Most Recent Face Raw Mean: "),
    ("零偏 ", "Offset "),
    (" mg；比例 ", " mg; scale "),
    ("当前设备参数：", "Current Device Parameters: "),
    ("（已校准）", "(calibrated)"),
    ("（默认值，尚未校准）", "(defaults; not calibrated)"),
    ("等待查询", "waiting for query"),
    ("本次候选参数：", "Candidate Parameters: "),
    ("零偏/比例：通过；综合一致性：", "Offset/scale: passed; overall consistency: "),
    ("通过", "Passed"),
    ("未通过", "Failed"),
    ("\n六面合量相对1g偏差 (mg)：", "\nSix-face vector-magnitude deviation from 1 g (mg): "),
    ("\nX/Y/Z 正反面对称性偏差 (mg)：", "\nX/Y/Z opposite-face symmetry deviation (mg): "),
    ("。旁轴残差>50 mg仅为黄色姿态提示。", ". Cross-axis residuals >50 mg are only a yellow posture warning."),
    ("零偏/比例及综合一致性：待完成六面求解。旁轴残差为姿态提示。", "Offset/scale and overall consistency: complete six-face calculation first. Cross-axis residuals are posture guidance."),
    ("校准尚未结束，请先点“取消本次校准”；保存过程中请等待最终确认。", "Calibration is not finished. Click “Cancel Calibration” first; if saving is in progress, wait for final confirmation."),
    # Detection / learning states
    ("未学习", "Not Learned"),
    ("学习中", "Learning"),
    ("滤波预热", "Filter Warm-up"),
    ("正常", "Normal"),
    ("疑似异常", "Suspected Anomaly"),
    ("异常报警", "Anomaly Alarm"),
    ("MCU已接收学习指令", "MCU accepted the learning command"),
    ("MCU已取消学习", "MCU canceled learning"),
    ("学习指令已排队，等待串口发送。", "Learning command queued; waiting for serial transmission."),
    ("取消指令已排队，等待发送。", "Cancel command queued; waiting for transmission."),
    ("学习指令已发送（第", "Learning command sent (attempt "),
    ("次），等待 MCU 确认。", "); waiting for MCU confirmation."),
    ("取消已发送，等待 MCU 确认。", "Cancel command sent; waiting for MCU confirmation."),
    ("MCU已确认取消学习。", "MCU confirmed learning cancellation."),
    ("MCU已接收学习指令，等待学习状态；请保持固定安装和正常工况。", "MCU accepted the learning command. Waiting for the learning state; keep the device securely mounted under normal operating conditions."),
    ("设备正忙（可能正在学习、保存或切换采样率）", "Device is busy (learning, saving, or changing sample rate may be in progress)"),
    ("传感器尚未就绪", "Sensor is not ready"),
    ("六位置校准会话尚未结束，请先取消或保存校准", "Six-position calibration session is still active. Cancel or save calibration first"),
    ("正在保存模型，请稍后再试", "Model is being saved. Try again later"),
    ("正在切换采样率，请稍后再试", "Sample rate is changing. Try again later"),
    ("MCU拒绝操作：", "MCU rejected the operation: "),
    ("。本次不视为学习成功。", ". This attempt is not considered successful learning."),
    ("MCU已进入正常状态学习，约1秒预热＋30秒有效数据。", "MCU entered normal-state learning: about 1 s warm-up plus 30 s of valid data."),
    ("MCU已退出学习状态。", "MCU exited the learning state."),
    ("串口已断开，操作结果未确认。", "Serial port disconnected; operation result was not confirmed."),
    ("尚未收到 MCU 确认，正在有限重试。", "No MCU confirmation received yet. Retrying with a limited number of attempts."),
    ("MCU已接收指令，但未确认持续学习状态；请检查采集错误或复位日志。", "MCU accepted the command but did not confirm sustained learning. Check acquisition errors or reset logs."),
    ("操作未收到完整确认，已停止重试，请查看串口日志。", "The operation did not receive complete confirmation. Retries stopped; check the serial log."),
]

_PAIRS.extend([('两行均为约0.5秒均值、含重力；校准后值已应用设备参数。', 'Both rows are approx. 0.5 s averages and include gravity; device calibration parameters are applied to the calibrated values.'), ('对应传感器 ', 'corresponds to sensor '), ('轴正方向朝上', 'axis positive direction up'), ('轴负方向朝上', 'axis negative direction up')])

_PAIRS.extend([('连接设备后查询校准状态。', 'Connect the device to query calibration status.'), ('正在核对 MCU 校准协议版本…', 'Checking the MCU calibration protocol version…'), ('串口已断开；未确认的采集或保存不视为成功。重连后查询设备状态。', 'Serial port disconnected. Unconfirmed capture or save operations are not considered successful. Reconnect and query the device status.'), ('校准协议', 'Calibration protocol'), ('不匹配，需V1.4', 'mismatch; V1.4 required'), ('匹配', 'matched'), ('MCU 启动标识 V', 'MCU boot identifier V'), ('；尚未收到V1.4能力确认', '; V1.4 capability confirmation not received'), ('MCU版本未确认：需烧录V1.4，确认 main.c 和 calibration.inc 均已替换并重新编译。', 'MCU version not verified: flash V1.4 and ensure both main.c and calibration.inc have been replaced and recompiled.'), ('设备拒绝求解，但六面诊断明细尚未返回；请查询设备状态并确认MCU版本。', 'The device rejected the calculation, but six-face diagnostic details have not been returned. Query device status and verify the MCU version.'), ('合量核验未通过：', 'Vector-magnitude check failed: '), (' 面校正后合量偏离1g ', ' face corrected magnitude deviates from 1 g by '), (' mg（允许±50 mg），请检查该面倾斜及对应正反面基准。', ' mg (allowed ±50 mg). Check the tilt of this face and the corresponding opposite-face reference.'), ('正反面对称性未通过：', 'Opposite-face symmetry check failed: '), (' 轴两面的校正中点偏差 ', ' axis corrected midpoint deviation between opposite faces is '), (' mg（允许50 mg）。请检查这两面及各轴零偏是否稳定。', ' mg (limit 50 mg). Check these two faces and verify that each axis offset is stable.'), ('六面核验未通过：最大残差在 ', 'Six-face verification failed: maximum residual is on '), (' 面的 ', ' face, axis '), (' 轴，', ', '), (' mg（门限50 mg）。先检查该面，并核对该轴正反面；最大残差不能唯一确定问题来源。选中一面重采会保留其余数据。', ' mg (limit 50 mg). Check this face first, then verify the corresponding opposite face. The maximum residual alone cannot uniquely identify the cause. Recapturing one face retains the other measurements.'), ('正反面差值或参数不合格。X/Y/Z 正反面差值：', 'Opposite-face differences or parameters are out of range. X/Y/Z opposite-face differences: '), (' mg；各轴应约为+2000 mg，请检查是否选错方向、重复同一面或正反面颠倒。', ' mg. Each axis should be about +2000 mg. Check for an incorrect orientation, duplicate face, or reversed opposite faces.'), ('六面数据尚未齐全，请补采缺失面。', 'Six-face data is incomplete. Capture the missing faces.'), ('零偏/比例及综合一致性检查通过。', 'Offset/scale and overall consistency checks passed.'), ('等待 MCU 开始校准确认…', 'Waiting for MCU confirmation to start calibration…'), ('保持静止，正在采集这一面…', 'Keep still. Capturing this face…'), ('等待 MCU 计算和检查六面结果…', 'Waiting for the MCU to calculate and verify the six-face results…'), ('正在写入设备，等待最终结果；请勿断电。', 'Writing to the device and waiting for the final result. Do not power off.'), ('等待 MCU 取消确认…', 'Waiting for MCU cancellation confirmation…'), ('已重新查询设备。上次操作结果未确认，请检查参数；不要将此提示当作保存成功。', 'Device queried again. The previous operation was not confirmed. Check the parameters; do not treat this message as a successful save.'), ('校准会话进行中，可继续采集或取消。', 'Calibration session is active. You can continue capturing or cancel.'), ('设备支持六位置校准。先停机，将板子静止放稳。', 'The device supports six-position calibration. Stop the machine and place the board on a stable surface.'), ('保存成功，已读回当前参数。请安装到正常工况，分别重新学习 2500 / 5000 / 10000 / 20000 Hz；掉电恢复需重启后另行验证。', 'Save successful; current parameters were read back. Install the device under normal operating conditions and relearn at 2500 / 5000 / 10000 / 20000 Hz respectively. Verify power-loss recovery separately after reboot.'), ('保存回复与读回参数不一致，请检查设备。', 'The save response does not match the parameters read back. Check the device.'), ('零偏/比例与综合一致性检查通过，可以保存。旁轴残差超过50 mg仅提示检查姿态；写入后须重新学习。', 'Offset/scale and overall consistency checks passed; the parameters can be saved. Cross-axis residuals above 50 mg are only a posture warning. Relearn after writing.'), ('按六个方向逐面放稳，再点击“采集所选面”。', 'Stabilize the device in each of the six orientations, then click “Capture Selected Face.”'), ('采集方向回复不匹配，请查询设备状态。', 'The capture-direction response does not match. Query the device status.'), ('本面静止检查通过，可以换下一面；方向和零偏将在六面求解时核验。', 'This face passed the stability check. You can move to the next face; orientation and offset will be verified during the six-face calculation.'), ('本面未通过：', 'This face failed: '), ('采集期间有振动，请放稳重试；方向会在六面求解时检查。', 'Vibration occurred during capture. Stabilize the device and try again; orientation will be checked during the six-face calculation.'), ('采集数据中断或超时，请重试。', 'Capture data was interrupted or timed out. Please try again.'), ('收到延迟的保存回复，请查询当前参数并检查设备。', 'A delayed save response was received. Query the current parameters and check the device.'), ('MCU 已确认保存，正在读回参数…', 'MCU confirmed the save. Reading back parameters…'), ('保存未完整确认：写入返回 ', 'Save was not fully confirmed: write returned '), ('，传感器恢复 ', ', sensor resume returned '), ('。请查询参数；可能已提交，需要重新学习。', '. Query the parameters. The save may have been committed; relearning is required.'), ('已取消未保存的校准；原有参数保持。', 'Uncommitted calibration was canceled; existing parameters are retained.'), (' [设备返回 ', ' [device returned '), ('MCU 拒绝操作：', 'MCU rejected the operation: '), ('固件不支持校准命令，请使用 MCU_Calibration_V1。', 'Firmware does not support calibration commands. Use MCU_Calibration_V1.'), ('MCU报告已采集，但六面明细未完整返回。请检查当前固件版本及串口日志；缺失值不会被当成0。', 'The MCU reports that capture is complete, but six-face details are incomplete. Check the firmware version and serial log; missing values are never treated as zero.'), ('未收到校准能力回复。请检查是否使用 MCU_Calibration_V1；原有采集功能仍可使用。', 'No calibration capability response was received. Check whether MCU_Calibration_V1 is in use; existing acquisition functions remain available.'), (' 未收到完整确认，结果未知；正在查询设备，请勿重复写入。', ' did not receive complete confirmation; the result is unknown. Querying the device. Do not repeat the write.')])

_PAIRS.extend([('校准协议匹配', 'Calibration protocol matched'), ('校准协议不匹配，需V1.4', 'Calibration protocol mismatch; V1.4 required')])

_PAIRS.extend([('：', ': '), ('、', ', ')])

_PAIRS = sorted(_PAIRS, key=lambda pair: len(pair[0]), reverse=True)

def get_language():
    return _LANGUAGE

def tr(value, language=None):
    text = str(value)
    language = language or _LANGUAGE
    if language == "zh":
        return text
    for source, target in _PAIRS:
        if source in text:
            text = text.replace(source, target)
    return text

def _register(obj):
    try:
        _WIDGETS.append(weakref.ref(obj))
    except TypeError:
        pass

class _TextMixin:
    def __init__(self, *args, **kwargs):
        initial_text = args[0] if args and isinstance(args[0], str) else None
        super().__init__(*args, **kwargs)
        self._i18n_text = None
        self._i18n_tooltip = None
        _register(self)
        # Qt constructors may set their initial caption in C++ without calling
        # the Python setText override, so capture it explicitly for relocalizing.
        if initial_text is not None:
            if isinstance(self, _ORIGINAL_GROUPBOX):
                self.setTitle(initial_text)
            elif hasattr(self, "setText"):
                self.setText(initial_text)

    def setText(self, value):
        self._i18n_text = str(value)
        super().setText(tr(self._i18n_text))

    def setToolTip(self, value):
        self._i18n_tooltip = str(value)
        super().setToolTip(tr(self._i18n_tooltip))

    def retranslate(self):
        if self._i18n_text is not None:
            super().setText(tr(self._i18n_text))
        if self._i18n_tooltip is not None:
            super().setToolTip(tr(self._i18n_tooltip))

class LocalizedLabel(_TextMixin, QtWidgets.QLabel):
    pass

class LocalizedButton(_TextMixin, QtWidgets.QPushButton):
    pass

class LocalizedCheckBox(_TextMixin, QtWidgets.QCheckBox):
    pass

class LocalizedGroupBox(_TextMixin, QtWidgets.QGroupBox):
    def setTitle(self, value):
        self._i18n_text = str(value)
        super().setTitle(tr(self._i18n_text))
    def retranslate(self):
        if self._i18n_text is not None:
            super().setTitle(tr(self._i18n_text))
        if self._i18n_tooltip is not None:
            super().setToolTip(tr(self._i18n_tooltip))

class LocalizedComboBox(_TextMixin, QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        self._i18n_items = []
        super().__init__(*args, **kwargs)

    def addItem(self, text, userData=None):
        self._i18n_items.append(str(text))
        super().addItem(tr(text), userData)

    def addItems(self, texts):
        for text in texts:
            self.addItem(text)

    def insertItem(self, index, text, userData=None):
        self._i18n_items.insert(index, str(text))
        super().insertItem(index, tr(text), userData)

    def setItemText(self, index, text):
        while len(self._i18n_items) <= index:
            self._i18n_items.append("")
        self._i18n_items[index] = str(text)
        super().setItemText(index, tr(text))

    def clear(self):
        self._i18n_items = []
        super().clear()

    def retranslate(self):
        for index, source in enumerate(self._i18n_items):
            if index < self.count():
                super().setItemText(index, tr(source))
        if self._i18n_tooltip is not None:
            super().setToolTip(tr(self._i18n_tooltip))

class LocalizedProgressBar(_TextMixin, QtWidgets.QProgressBar):
    def setFormat(self, value):
        self._i18n_text = str(value)
        super().setFormat(tr(self._i18n_text))
    def retranslate(self):
        if self._i18n_text is not None:
            super().setFormat(tr(self._i18n_text))
        if self._i18n_tooltip is not None:
            super().setToolTip(tr(self._i18n_tooltip))

class LocalizedPlainTextEdit(_TextMixin, QtWidgets.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        self._i18n_lines = deque(maxlen=150)
        super().__init__(*args, **kwargs)

    def appendPlainText(self, value):
        self._i18n_lines.append(str(value))
        super().appendPlainText(tr(value))

    def retranslate(self):
        super().setPlainText("\\n".join(tr(line) for line in self._i18n_lines))
        if self._i18n_tooltip is not None:
            super().setToolTip(tr(self._i18n_tooltip))

class LocalizedTableItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text=""):
        self._i18n_text = str(text)
        super().__init__(tr(self._i18n_text))
    def setText(self, value):
        self._i18n_text = str(value)
        super().setText(tr(self._i18n_text))
    def setToolTip(self, value):
        self._i18n_tooltip = str(value)
        super().setToolTip(tr(self._i18n_tooltip))
    def retranslate(self):
        super().setText(tr(self._i18n_text))
        if hasattr(self, "_i18n_tooltip"):
            super().setToolTip(tr(self._i18n_tooltip))

class LocalizedDialog(_TextMixin, QtWidgets.QDialog):
    def setWindowTitle(self, value):
        self._i18n_text = str(value)
        super().setWindowTitle(tr(self._i18n_text))
    def retranslate(self):
        if self._i18n_text is not None:
            super().setWindowTitle(tr(self._i18n_text))
        if self._i18n_tooltip is not None:
            super().setToolTip(tr(self._i18n_tooltip))

class LocalizedMainWindow(_TextMixin, QtWidgets.QMainWindow):
    def setWindowTitle(self, value):
        self._i18n_text = str(value)
        super().setWindowTitle(tr(self._i18n_text))
    def retranslate(self):
        if self._i18n_text is not None:
            super().setWindowTitle(tr(self._i18n_text))
        if self._i18n_tooltip is not None:
            super().setToolTip(tr(self._i18n_tooltip))

def set_language(language):
    global _LANGUAGE
    if language not in ("zh", "en"):
        return
    _LANGUAGE = language
    alive = []
    for reference in _WIDGETS:
        obj = reference()
        if obj is not None:
            alive.append(reference)
            try:
                obj.retranslate()
            except RuntimeError:
                pass
    _WIDGETS[:] = alive
