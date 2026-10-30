from alarm_utils import check_alarms

# 测试数据
current = 2.8
temperature = 42.0
speed = 1200.0

# 调用报警函数
alarms = check_alarms(current, temperature, speed)

# 判断设备状态
if alarms:
    status = "ALARM"
else:
    status = "NORMAL"

print("报警列表:", alarms)
print("设备状态:", status)