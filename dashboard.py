import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from pathlib import Path
from motor_simulator import generate_motor_data

st.set_page_config(
    page_title="Industrial Motor Monitoring",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    [data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 10px;
    }

    /* 报警表格整体样式 */
    .alarm-table {
        width: 100%;
        border-collapse: collapse;
        color: #E2E8F0;
        font-size: 14px;
    }

    /* 表头样式 */
    .alarm-table th {
        background-color: #1E293B;
        color: #94A3B8;
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #334155;
    }

    /* 表格内容样式 */
    .alarm-table td {
        background-color: #111827;
        padding: 12px;
        border-bottom: 1px solid #273449;
        white-space: nowrap;
    }
    /* 统一按钮风格 */
    .stDownloadButton > button,
    .stButton > button {
        background-color: #26313D !important;
        color: #E8E4DA !important;
        border: 1px solid #465363 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out;
    }

    /* 鼠标悬停 */
    .stDownloadButton > button:hover,
    .stButton > button:hover {
        background-color: #344252 !important;
        color: #FFF9ED !important;
        border: 1px solid #687789 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Industrial Motor Monitoring")
st.caption("工业电机实时监控与故障诊断系统")

# 定位项目文件
csv_path = Path(__file__).parent / "motor_data.csv"
run_id_path = Path(__file__).parent / "run_id.json"

# 模拟控制台
st.subheader("电机模拟控制台")

sim_col1, sim_col2, sim_col3 = st.columns([2, 1, 1])

with sim_col1:
    mode_options = {
        "正常运行": "normal",
        "过载": "overload",
        "过热": "overheat",
        "低转速": "low_speed"
    }

    selected_mode = st.selectbox(
        "选择模拟模式",
        list(mode_options.keys())
    )

with sim_col2:
    data_count = st.selectbox(
        "生成数据数量",
        [10, 20, 50, 100]
    )

with sim_col3:
    st.write("")
    st.write("")
    if st.button("▶️ 生成模拟数据", use_container_width=True):
        try:
            new_run_id = generate_motor_data(
                mode=mode_options[selected_mode],
                count=data_count
            )

            st.success(
                f"模拟完成！批次编号：{new_run_id}，"
                f"生成了 {data_count} 条数据。"
            )

            st.rerun()

        except Exception as e:
            st.error(f"生成数据失败：{e}")


# 两个按钮并排
button_col1, button_col2 = st.columns(2)

with button_col1:
    if st.button("刷新监控数据", use_container_width=True):
        st.rerun()

with button_col2:
    if st.button("重置测试数据", use_container_width=True):
        st.session_state["confirm_reset"] = True

# 二次确认
if st.session_state.get("confirm_reset", False):
    st.warning(
        "⚠️ 确定要重置吗？这将删除所有历史运行数据，并重置批次编号。此操作无法撤销！"
    )

    confirm_col1, confirm_col2 = st.columns(2)

    with confirm_col1:
        if st.button("确认重置", type="primary", use_container_width=True):
            # 删除历史 CSV 数据
            if csv_path.exists():
                csv_path.unlink()

            # 删除批次 ID 文件
            if run_id_path.exists():
                run_id_path.unlink()

            st.session_state["confirm_reset"] = False
            st.success("测试数据已清空！")
            st.rerun()

    with confirm_col2:
        if st.button("取消", use_container_width=True):
            st.session_state["confirm_reset"] = False
            st.rerun()

st.success("监控界面启动成功！")

st.subheader("电机运行数据")

if csv_path.exists():
    data = pd.read_csv(csv_path)

    # 负载模式筛选器
    st.subheader("负载模式筛选")

    load_mode = st.radio(
        "选择要查看的负载模式",
        ["全部", "低负载（40%）", "高负载（85%）"],
        horizontal=True
    )

    if load_mode == "低负载（40%）":
        filtered_data = data[data["load_percent"] == 40].copy()
    elif load_mode == "高负载（85%）":
        filtered_data = data[data["load_percent"] == 85].copy()
    else:
        filtered_data = data.copy()

    st.caption(f"当前筛选结果：{len(filtered_data)} 条记录")
    # 运行批次筛选器
    run_ids = sorted(filtered_data["run_id"].unique(), reverse=True)

    selected_run = st.selectbox(
        "选择运行批次",
        ["全部"] + run_ids
    )

    if selected_run != "全部":
        filtered_data = filtered_data[
            filtered_data["run_id"] == selected_run
        ].copy()

    st.caption(f"当前运行批次筛选后：{len(filtered_data)} 条记录")

    if not filtered_data.empty:
        latest = filtered_data.iloc[-1]

        col1, col2, col3,col4 = st.columns(4)

        col1.metric(
            "电流",
            f"{latest['current_a']:.2f} A"
        )

        col2.metric(
            "温度",
            f"{latest['temperature_c']:.2f} °C"
        )

        col3.metric(
            "转速",
            f"{latest['speed_rpm']:.0f} RPM"
        )

        status = str(latest["status"])

        if status == "ALARM":
            status_text = "报警"
        else:
            status_text = "运行正常"

        col4.metric(
            "运行状态",
            status_text
        )
        # 故障诊断建议
        st.subheader("故障诊断建议")
        if status == "ALARM":
            st.markdown(
                """
                <div style="
                    background-color: #472936;
                    color: #FDA4AF;
                    padding: 12px 16px;
                    border-radius: 8px;
                    border-left: 4px solid #FB7185;
                ">
                    <b>当前电机处于报警状态，请检查报警信息。</b>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="
                    background-color: #15352D;
                    color: #A7F3D0;
                    padding: 12px 16px;
                    border-radius: 8px;
                    border-left: 4px solid #34D399;
                ">
                    <b>当前电机运行正常。</b>
                </div>
                """,
                unsafe_allow_html=True
            )

        latest_alarms = str(latest["alarms"])

        diagnosis = []

        if "HIGH_CURRENT" in latest_alarms:
            diagnosis.append("电流过高：建议检查电机负载、线路及电流传感器。")

        if "HIGH_TEMPERATURE" in latest_alarms:
            diagnosis.append("温度过高：建议检查散热系统、通风情况及负载。")

        if "LOW_SPEED" in latest_alarms:
            diagnosis.append("转速过低：建议检查电机负载、驱动系统及转速传感器。")

        if diagnosis:
            for advice in diagnosis:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #26364A;
                        color: #BFDBFE;
                        padding: 10px 14px;
                        border-radius: 8px;
                        border-left: 4px solid #A78BFA;
                        margin-bottom: 8px;
                    ">
                        {advice}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style="
                    background-color: #15352D;
                    color: #A7F3D0;
                    padding: 10px 14px;
                    border-radius: 8px;
                    border-left: 4px solid #34D399;
                ">
                    当前没有检测到故障，无需显示诊断建议。
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("最新一条运行记录")
        st.dataframe(filtered_data.tail(5), width="stretch")


        # 报警信息面板
        st.subheader("报警信息")

        # 筛选所有报警记录
        alarm_data = filtered_data[
            filtered_data["status"] == "ALARM"
        ]

      
        if alarm_data.empty:
            st.markdown("""
                <div style="
                    background-color: #1B3832;
                    color: #6EE7B7;
                    border: 1px solid #315C50;
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: 500;
                ">
                    ● 当前数据中没有报警记录，电机运行正常。
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="
                    background-color: #472936;
                    color: #FDA4AF;
                    border: 1px solid #704052;
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: 500;
                ">
                    ● 共检测到 {len(alarm_data)} 条报警记录
                </div>
            """, unsafe_allow_html=True)


            # 只展示最近 10 条报警
            recent_alarms = alarm_data.tail(10).copy()

            # 把报警时间保留两位小数
            recent_alarms["elapsed_seconds"] = (
                recent_alarms["elapsed_seconds"].round(2)
            )
            

           
            # 把报警代码转换成中文说明
            def translate_alarm(alarm_text):
                alarm_names = {
                    "HIGH_CURRENT": "电流过高",
                    "HIGH_TEMPERATURE": "温度过高",
                    "LOW_SPEED": "转速过低"
                }
                if not isinstance(alarm_text, str) or not alarm_text:
                    return "无报警"
                
                codes = alarm_text.split("|")
                return "、".join(
                    alarm_names.get(code, code)
                    for code in codes
                )
            def get_alarm_level(alarm_text):
                if not isinstance(alarm_text, str) or not alarm_text.strip():
                    return "正常"

                alarms = [
                    alarm for alarm in alarm_text.split("|")
                    if alarm.strip()
                ]

                if len(alarms) >= 2:
                    return "高优先级"

                return "一般报警"


               

            # 转换报警代码
            recent_alarms["报警说明"] = (
                recent_alarms["alarms"].apply(translate_alarm)
            )
            recent_alarms["报警等级"] = (
               recent_alarms["alarms"].apply(get_alarm_level)
            )

            # 展示报警表格
            # 报警等级对应的胶囊标签
            def make_alarm_badge(level):
                badge_styles = {
                    "高优先级": (
                        "background:#3F1D2E;"
                        "color:#FDA4AF;"
                    ),
                    "一般报警": (
                        "background:#3B2B19;"
                        "color:#FCD34D;"
                    ),
                    "正常": (
                        "background:#15352D;"
                        "color:#6EE7B7;"
                    )
                }

                style = badge_styles.get(level, "")
                return (
                    f'<span style="display:inline-block;'
                    f'padding:4px 10px;'
                    f'border-radius:999px;'
                    f'font-size:12px;'
                    f'font-weight:600;'
                    f'{style}">'
                    f'● {level}</span>'
                )

            # 创建报警表格展示副本
            display_alarms = recent_alarms[
                [
                    "elapsed_seconds",
                    "current_a",
                    "temperature_c",
                    "speed_rpm",
                    "报警说明",
                    "报警等级"
                ]
            ].copy()

            # 将报警等级转换为 HTML 标签
            display_alarms["报警等级"] = (
                display_alarms["报警等级"]
                .apply(make_alarm_badge)
            )

            # 使用 HTML 表格展示胶囊标签
            st.markdown(
                display_alarms.to_html(
                    index=False,
                    escape=False,
                    classes="alarm-table"
                ),
                unsafe_allow_html=True
            )

        # 电机运行趋势
        st.subheader("📈 电机运行趋势")

        # 横轴使用运行时间
        chart_data = filtered_data.set_index("elapsed_seconds")
        # 电流趋势
        st.markdown("#### 电流趋势（A）")
        fig_current = go.Figure()
        # 蓝色实线：实际电流
        for run_id, group in filtered_data.groupby("run_id"):
            fig_current.add_trace(go.Scatter(
                x=group["elapsed_seconds"],
                y=group["current_a"],
                mode="lines",
                name=f"批次 {run_id}",
                line=dict(width=2)
            ))
        # 红色虚线：报警阈值
        fig_current.add_hline(
            y=2.5,
            line_dash="dash",
            line_color="#EF4444",
            line_width=2,
            annotation_text="报警阈值 2.5 A",
            annotation_position="top left"
        )
        fig_current.update_layout(
            xaxis_title="运行时间（秒）",
            yaxis_title="电流（A）",
            template="plotly_dark",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", y=1.12)
        )
        # 筛选电流超过报警阈值的数据
        current_alarm = chart_data[
            chart_data["alarms"].fillna("").str.contains(
                "HIGH_CURRENT",
                regex=False
            )
        ]

        # 在图表上添加红色报警点
        fig_current.add_trace(go.Scatter(
            x=current_alarm.index,
            y=current_alarm["current_a"],
            mode="markers",
            name="电流报警点",
            marker=dict(
                color="#EF4444",
                size=9,
                symbol="circle"
            )
        ))
        st.plotly_chart(fig_current, width="stretch")


        # 温度趋势
        st.markdown("#### 温度趋势（°C）")
        fig_temperature = go.Figure()
        # 蓝色实线：实际温度
        for run_id, group in filtered_data.groupby("run_id"):
            fig_temperature.add_trace(go.Scatter(
                x=group["elapsed_seconds"],
                y=group["temperature_c"],
                mode="lines",
                name=f"批次 {run_id}",
                line=dict(width=2)
            ))
        # 红色虚线：报警阈值
        fig_temperature.add_hline(
            y=40,
            line_dash="dash",
            line_color="#EF4444",
            line_width=2,
            annotation_text="报警阈值 40 °C",
            annotation_position="top left"
        )

        fig_temperature.update_layout(
            xaxis_title="运行时间（秒）",
            yaxis_title="温度（°C）",
            template="plotly_dark",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", y=1.12)
        )
        # 筛选温度超过报警阈值的数据
        temperature_alarm = chart_data[
            chart_data["alarms"].fillna("").str.contains(
                "HIGH_TEMPERATURE",
                regex=False
            )
        ]
        # 在图表上添加红色报警点
        fig_temperature.add_trace(go.Scatter(
            x=temperature_alarm.index,
            y=temperature_alarm["temperature_c"],
            mode="markers",
            name="温度报警点",
            marker=dict(
                color="#EF4444",
                size=9,
                symbol="circle"
            )
        ))
        st.plotly_chart(fig_temperature, width="stretch")

        # 转速趋势
        st.markdown("#### 转速趋势（RPM）")
        fig_speed = go.Figure()

        # 蓝色实线：实际转速
        for run_id, group in filtered_data.groupby("run_id"):
            fig_speed.add_trace(go.Scatter(
                x=group["elapsed_seconds"],
                y=group["speed_rpm"],
                mode="lines",
                name=f"批次 {run_id}",
                line=dict(width=2)
            ))

        # 红色虚线：最低转速报警阈值
        fig_speed.add_hline(
            y=1300,
            line_dash="dash",
            line_color="#EF4444",
            line_width=2,
            annotation_text="最低转速阈值 1300 RPM",
            annotation_position="top left"
        )

        fig_speed.update_layout(
            xaxis_title="运行时间（秒）",
            yaxis_title="转速（RPM）",
            template="plotly_dark",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", y=1.12)
        )
        # 筛选速度低于报警阈值的数据
        speed_alarm = chart_data[
            chart_data["alarms"].fillna("").str.contains(
                "LOW_SPEED",
                regex=False
            )
        ]

        # 添加红色报警点
        fig_speed.add_trace(go.Scatter(
            x=speed_alarm.index,
            y=speed_alarm["speed_rpm"],
            mode="markers",
            name="转速报警点",
            marker=dict(
                color="#EF4444",
                size=9,
                symbol="circle"
            )
        ))
        st.plotly_chart(fig_speed, width="stretch")


    else:
        st.warning("CSV 文件存在，但暂时没有数据。")
else:
    st.warning("尚未找到 motor_data.csv，请先运行电机模拟器。")



# 报警统计
st.subheader("报警统计")

if csv_path.exists() and not data.empty and not filtered_data.empty:

    alarm_data = filtered_data[
        filtered_data["status"] == "ALARM"
    ]

    total_records = len(filtered_data)
    total_alarm_records = len(alarm_data)

    alarm_rate = (
        total_alarm_records / total_records * 100
        if total_records > 0
        else 0
    )

    stat1, stat2, stat3 = st.columns(3)

    stat1.metric("总数据记录数", total_records)
    stat2.metric("报警记录数", total_alarm_records)
    stat3.metric("报警记录占比", f"{alarm_rate:.1f}%")

    # 各类报警次数统计

    alarm_text = filtered_data["alarms"].fillna("").astype(str)

    high_current_count = alarm_text.apply(
        lambda x: "HIGH_CURRENT" in x.split("|")
    ).sum()

    high_temperature_count = alarm_text.apply(
        lambda x: "HIGH_TEMPERATURE" in x.split("|")
    ).sum()

    low_speed_count = alarm_text.apply(
        lambda x: "LOW_SPEED" in x.split("|")
    ).sum()
    
    st.markdown("#### 报警类型分布")

    alarm_types = [
        ("高电流", int(high_current_count), "#F87171"),
        ("高温", int(high_temperature_count), "#FBBF24"),
        ("低转速", int(low_speed_count), "#60A5FA")
    ]

    max_count = max(count for _, count, _ in alarm_types)
    total_count = sum(count for _, count, _ in alarm_types)

    for name, count, color in alarm_types:
        label_col, bar_col, count_col = st.columns([1.2, 4, 0.9])

        with label_col:
            st.write(name)

        with bar_col:
            progress = count / total_count if total_count > 0 else 0
            percentage = progress * 100

            st.markdown(
                f"""
                <div style="
                    background-color: #263244;
                    border-radius: 6px;
                    height: 12px;
                    margin-top: 9px;
                    overflow: hidden;
                ">
                    <div style="
                        background-color: {color};
                        width: {progress * 100}%;
                        height: 12px;
                        border-radius: 6px;
                    "></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with count_col:
            st.markdown(
                f"<div style='text-align:right; padding-top:2px;'>"
                f"<b>{count}</b> 次 ({percentage:.1f}%)</div>",
                unsafe_allow_html=True
            )
    
    # 批次风险分析
    st.markdown("---")
    st.subheader("批次风险分析")

    # 统计每个批次的数据
    report_data = (
        filtered_data.groupby("run_id")
        .agg(
            数据记录数=("status", "size"),
            报警记录数=("status", lambda s: (s == "ALARM").sum())
        )
        .reset_index()
    )

    # 计算报警占比
    report_data["报警占比（%）"] = (
        report_data["报警记录数"]
        / report_data["数据记录数"]
        * 100
    ).round(1)

    # 判断风险等级
    def get_risk_level(rate):
        if rate >= 50:
            return "高风险"
        elif rate >= 20:
            return "中风险"
        else:
            return "低风险"

    report_data["风险等级"] = (
        report_data["报警占比（%）"].apply(get_risk_level)
    )

    # 统计每个批次的故障原因
    for run_id in report_data["run_id"]:
        batch_data = filtered_data[
            filtered_data["run_id"] == run_id
        ]

        alarms = batch_data["alarms"].fillna("").astype(str)

        report_data.loc[
            report_data["run_id"] == run_id, "高电流次数"
        ] = alarms.str.contains("HIGH_CURRENT", regex=False).sum()

        report_data.loc[
            report_data["run_id"] == run_id, "高温次数"
        ] = alarms.str.contains("HIGH_TEMPERATURE", regex=False).sum()

        report_data.loc[
            report_data["run_id"] == run_id, "低转速次数"
        ] = alarms.str.contains("LOW_SPEED", regex=False).sum()

    # 故障次数转换为整数
    fault_columns = ["高电流次数", "高温次数", "低转速次数"]
    report_data[fault_columns] = (
        report_data[fault_columns].fillna(0).astype(int)
    )

    # 按报警占比从高到低排名
    report_data = report_data.sort_values(
        "报警占比（%）",
        ascending=False
    )

    # 风险等级颜色
    def color_risk_level(value):
        if value == "高风险":
            return "background-color: #472936; color: #FDA4AF"
        elif value == "中风险":
            return "background-color: #3B2B19; color: #FCD34D"
        else:
            return "background-color: #15352D; color: #6EE7B7"

    # 表格样式
    styled_report = (
        report_data.style
        .map(color_risk_level, subset=["风险等级"])
        .bar(
            subset=["报警占比（%）"],
            color="#60A5FA",
            vmin=0,
            vmax=100,
            align="left"
        )
        .format({
            "报警占比（%）": "{:.1f}%"
        })
    )

    st.dataframe(
        styled_report,
        hide_index=True,
        width="stretch"
    )
    # 原始监测数据导出
    st.markdown("#### 原始监测数据导出")
    
    raw_csv = filtered_data.to_csv(
        index=False
    ).encode("utf-8-sig")
    
    st.download_button(
        label="下载原始监测数据 CSV",
        data=raw_csv,
        file_name="motor_raw_data.csv",
        mime="text/csv",
        use_container_width=True
    )
    # 准备报警记录导出数据
    csv_bytes = None

    if not alarm_data.empty:
        export_data = alarm_data.copy()

        # 将报警代码转换为中文
        alarm_name_map = {
            "HIGH_CURRENT": "高电流报警",
            "HIGH_TEMPERATURE": "高温报警",
            "LOW_SPEED": "低转速报警"
        }

        export_data["alarms"] = export_data["alarms"].apply(
            lambda value: "、".join(
                alarm_name_map.get(code, code)
                for code in str(value).split("|")
                if code
            )
        )

        csv_bytes = export_data.to_csv(
            index=False
        ).encode("utf-8-sig")
# 报告信息
    st.markdown("#### 报告信息")

    report_col1, report_col2, report_col3, report_col4 = st.columns(4)

    report_col1.metric(
        "分析批次数量",
        len(report_data)
    )

    report_col2.metric(
        "分析数据记录数",
        int(report_data["数据记录数"].sum())
    )

    report_col3.metric(
        "报警记录数",
        int(report_data["报警记录数"].sum())
    )

    report_col4.metric(
        "报告生成时间",
        pd.Timestamp.now().strftime("%H:%M:%S")
    )

        # 准备批次风险分析报告
    report_csv = report_data.to_csv(
        index=False
    ).encode("utf-8-sig")

    # 两个 CSV 下载按钮并排
    alarm_col, report_col = st.columns(2)

    with alarm_col:
        if csv_bytes is not None:
            st.download_button(
                label="下载报警记录 CSV",
                data=csv_bytes,
                file_name="motor_alarm_records.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button(
                "暂无报警记录",
                disabled=True,
                use_container_width=True
            )

    with report_col:
        st.download_button(
            label="下载批次风险分析报告",
            data=report_csv,
            file_name="motor_risk_analysis_report.csv",
            mime="text/csv",
            use_container_width=True
        )

elif not csv_path.exists():
    st.info("尚未找到 motor_data.csv，暂时无法统计报警数据。")

elif data.empty:
    st.info("CSV 文件存在，但没有数据，暂时无法统计报警。")

else:
    st.info("当前负载筛选没有匹配的记录，请切换负载模式。")