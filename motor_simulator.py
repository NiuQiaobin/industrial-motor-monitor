import random
import csv
import json
from pathlib import Path
from alarm_utils import check_alarms


def generate_motor_data(mode="normal", count=20):
    # 检查模拟模式是否有效
    if mode not in ["normal", "overload", "overheat", "low_speed"]:
        raise ValueError("不支持的电机运行模式")

    if count <= 0:
        raise ValueError("生成数据数量必须大于 0")

    print(f"当前模拟模式：{mode}")
    print(f"本次生成数据数量：{count}")

    # 使用当前代码文件所在目录
    base_dir = Path(__file__).parent
    csv_path = base_dir / "motor_data.csv"
    run_id_path = base_dir / "run_id.json"

    # 检查 CSV 文件是否存在
    file_exists = csv_path.exists()

    # 读取并更新批次编号
    if run_id_path.exists():
        with open(run_id_path, "r", encoding="utf-8") as id_file:
            run_id = json.load(id_file) + 1
    else:
        run_id = 0

    with open(run_id_path, "w", encoding="utf-8") as id_file:
        json.dump(run_id, id_file)

    print(f"本次运行编号：{run_id}")

    # 初始化模拟参数
    temperature = 25.0

    # 打开 CSV 文件，追加本次模拟数据
    with open(
        csv_path,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # 如果是新文件，先写入表头
        if not file_exists:
            writer.writerow([
                "run_id",
                "elapsed_seconds",
                "current_a",
                "temperature_c",
                "speed_rpm",
                "load_percent",
                "status",
                "alarms"
            ])

        # 按照指定数量生成数据
        for i in range(count):

            # 模拟经过的时间，每条数据间隔 1 秒
            elapsed_show = i

            # 根据运行模式设置负载
            if mode == "normal":
                load = 40 if i < 10 else 85

            elif mode == "overload":
                load = 85

            elif mode == "overheat":
                load = 40

            elif mode == "low_speed":
                load = 40

            # 根据运行模式生成电流
            if mode == "overload":
                current = random.uniform(2.6, 3.0)
            else:
                current = random.uniform(1.0, 1.8)

            # 根据运行模式生成转速
            if mode == "low_speed":
                speed = random.uniform(1100, 1250)
            else:
                speed = random.uniform(1400, 1500)

            # 根据运行模式设置目标温度
            if mode == "overheat":
                target_temp = 50.0
            else:
                target_temp = 30.0

            # 温度逐渐接近目标值，并加入少量波动
            temperature += (target_temp - temperature) * 0.05
            temperature += random.uniform(-0.2, 0.2)

            # 检查报警
            alarms = check_alarms(
                current,
                temperature,
                speed
            )

            status = "ALARM" if alarms else "NORMAL"

            # 显示模拟数据
            print(
                f"Time: {elapsed_show:.1f}s | "
                f"Load: {load}% | "
                f"Current: {current:.2f} A | "
                f"Temperature: {temperature:.2f} C | "
                f"Speed: {speed:.0f} RPM | "
                f"Status: {status}"
            )

            if alarms:
                print("  Detected alarms:", alarms)

            # 写入 CSV
            writer.writerow([
                run_id,
                elapsed_show,
                current,
                temperature,
                speed,
                load,
                status,
                "|".join(alarms)
            ])

        # 将数据及时保存到磁盘
        file.flush()

    print(f"模拟完成！本次共生成 {count} 条数据。")

    return run_id
