import pandas as pd ##表格的数据读取、清洗、统计、筛选
import matplotlib.pyplot as plt ##数据可视化，画曲线图
# 读取电机运行记录
data = pd.read_csv("motor_data.csv")

print("=== 数据预览 ===")
print(data.head())##如果这里不填写默认输出前五行数据

print("\n=== 统计结果 ===")
print("数据记录数:", len(data))
print("最大电流:", data["current_a"].max(), "A")
print("最高温度:", data["temperature_c"].max(), "°C")
print("最低转速:", data["speed_rpm"].min(), "RPM")
print("平均电流:", round(data["current_a"].mean(), 2), "A")
print("平均温度:", round(data["temperature_c"].mean(), 2), "°C")
print("平均转速:", round(data["speed_rpm"].mean(), 2), "RPM")


# 按负载分组，比较电机运行数据
print("\n=== 不同负载下的运行数据对比 ===")
load_groups = data.groupby("load_percent")
print(
    load_groups[
        ["current_a", "temperature_c", "speed_rpm"]
    ].mean().round(2)
)
print("\n=== 不同负载下的报警记录数量 ===")
alarm_counts = (
    data[data["status"] == "ALARM"]
    .groupby("load_percent")
    .size()
)

alarm_counts = alarm_counts.reindex(
    sorted(data["load_percent"].unique()),
    fill_value=0
)

print(alarm_counts)

# 筛选出所有报警记录
alarm_data = data[data["status"] == "ALARM"]

# 只筛选高电流异常记录
current_alarm_data = data[
    data["alarms"].fillna("").str.contains("HIGH_CURRENT")
]
# 只筛选高温度异常记录
temperature_alarm_data = data[
    data["alarms"].fillna("").str.contains("HIGH_TEMPERATURE")
]
# 只筛选低转速异常记录
speed_alarm_data = data[
    data["alarms"].fillna("").str.contains("LOW_SPEED")
]

print("\n=== 报警记录 ===")
print(alarm_data)

print("报警记录数量:", len(alarm_data))

# 统计各类报警次数
print("\n=== 报警类型统计 ===")

print(
    "高电流报警次数:",
    data["alarms"].fillna("").str.contains("HIGH_CURRENT").sum()
)

print(
    "高温度报警次数:",
    data["alarms"].fillna("").str.contains("HIGH_TEMPERATURE").sum()
)

print(
    "低转速报警次数:",
    data["alarms"].fillna("").str.contains("LOW_SPEED").sum()
)

# 创建一个窗口，里面放三张子图
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# 第一张：电流
axes[0].plot(data["elapsed_seconds"], data["current_a"], label="Current (A)")
axes[0].set_title("Motor Current")
axes[0].set_ylabel("Current (A)")
axes[0].legend()
axes[0].grid(True)

axes[0].axhline(
    y=2.5,
    color="red",
    linestyle="--",
    label="Current Threshold (2.5 A)"
)

#标记温度异常点
axes[0].scatter(
    current_alarm_data["elapsed_seconds"],
    current_alarm_data["current_a"],
    color="red",
    label="High Current Alarm",
    zorder=3
)

# 第二张：温度
axes[1].plot(data["elapsed_seconds"], data["temperature_c"], label="Temperature (C)")
axes[1].set_title("Motor Temperature")
axes[1].set_ylabel("Temperature (C)")
axes[1].legend()
axes[1].grid(True)

axes[1].axhline(
    y=40,
    color="red",
    linestyle="--",
    label="Temperature Threshold (40 °C)"
)

axes[1].scatter(
    temperature_alarm_data["elapsed_seconds"],
    temperature_alarm_data["temperature_c"],
    color="red",
    label="High Temperature Alarm",
    zorder=3
)

# 第三张：转速
axes[2].plot(data["elapsed_seconds"], data["speed_rpm"], label="Speed (RPM)")
axes[2].set_title("Motor Speed")
axes[2].set_ylabel("Speed (RPM)")
axes[2].set_xlabel("Time (seconds)")
axes[2].legend()
axes[2].grid(True)

axes[2].axhline(
    y=1300,
    color="red",
    linestyle="--",
    label="Speed Threshold (1300 RPM)"
)

axes[2].scatter(
    speed_alarm_data["elapsed_seconds"],
    speed_alarm_data["speed_rpm"],
    color="red",
    label="Low Speed Alarm",
    zorder=3
)

# 自动调整布局
plt.tight_layout()

# 一次性显示整个窗口
plt.show()