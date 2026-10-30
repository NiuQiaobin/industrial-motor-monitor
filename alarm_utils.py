def check_alarms(current, temperature, speed):
    alarms = []

    if current > 2.5:
        alarms.append("HIGH_CURRENT")

    if temperature > 40:
        alarms.append("HIGH_TEMPERATURE")

    if speed < 1300:
        alarms.append("LOW_SPEED")

    return alarms