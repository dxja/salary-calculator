import streamlit as st
import pandas as pd
import numpy as np

# 税率表（2025最新）
TAX_BRACKETS = [0, 3000, 12000, 25000, 35000, 55000, 80000]
TAX_RATES = [0.03, 0.1, 0.2, 0.25, 0.3, 0.35, 0.45]
TAX_DEDUCTIONS = [0, 210, 1410, 2660, 4410, 7160, 15160]

# 城市社保预设
CITY_PRESETS = {
    "上海": {"pension": 8.0, "medical": 2.0, "unemployment": 0.5, "injury": 0.2, "maternity": 0.0, "housing": 7.0},
    "北京": {"pension": 8.0, "medical": 2.0, "unemployment": 0.5, "injury": 0.2, "maternity": 0.0, "housing": 12.0},
    "广州": {"pension": 8.0, "medical": 2.0, "unemployment": 0.5, "injury": 0.2, "maternity": 0.0, "housing": 5.0},
    "深圳": {"pension": 8.0, "medical": 2.0, "unemployment": 0.3, "injury": 0.2, "maternity": 0.0, "housing": 5.0}
}

# 页面配置
st.set_page_config(page_title="外企薪酬计算器", layout="wide")
st.title("💰 外企薪酬计算器 (Python+Streamlit)")
st.caption("软件工程专业作品 | 自动计算五险一金及个税")

# 侧边栏输入
with st.sidebar:
    st.header("参数设置")
    base_salary = st.number_input("基本工资(元)", min_value=0, value=15000, step=1000)
    city = st.selectbox("工作城市", list(CITY_PRESETS.keys()), index=0)
    
    # 使用城市预设
    preset = CITY_PRESETS[city]
    st.subheader(f"{city}社保比例")
    col1, col2 = st.columns(2)
    with col1:
        pension_rate = st.slider("养老保险(%)", 0.0, 20.0, preset["pension"], 0.5)
        medical_rate = st.slider("医疗保险(%)", 0.0, 12.0, preset["medical"], 0.5)
        unemployment_rate = st.slider("失业保险(%)", 0.0, 2.0, preset["unemployment"], 0.1)
    with col2:
        housing_rate = st.slider("住房公积金(%)", 0.0, 12.0, preset["housing"], 0.5)
        injury_rate = st.slider("工伤保险(%)", 0.0, 2.0, preset["injury"], 0.1)
        maternity_rate = st.slider("生育保险(%)", 0.0, 1.0, preset["maternity"], 0.1)
    
    st.subheader("专项附加扣除")
    special_deduction = st.number_input("子女教育/房贷等(元)", min_value=0, value=1000)

# 计算五险一金
def calculate_insurance(base, rates):
    return {
        "养老保险": base * rates["pension"] / 100,
        "医疗保险": base * rates["medical"] / 100,
        "失业保险": base * rates["unemployment"] / 100,
        "工伤保险": base * rates["injury"] / 100,
        "生育保险": base * rates["maternity"] / 100,
        "住房公积金": base * rates["housing"] / 100
    }

# 计算个税
def calculate_tax(taxable_income):
    for i in range(1, len(TAX_BRACKETS)):
        if taxable_income <= TAX_BRACKETS[i]:
            return taxable_income * TAX_RATES[i-1] - TAX_DEDUCTIONS[i-1]
    return taxable_income * TAX_RATES[-1] - TAX_DEDUCTIONS[-1]

# 执行计算
insurance_rates = {
    "pension": pension_rate,
    "medical": medical_rate,
    "unemployment": unemployment_rate,
    "injury": injury_rate,
    "maternity": maternity_rate,
    "housing": housing_rate
}
insurance = calculate_insurance(base_salary, insurance_rates)
total_insurance = sum(insurance.values())

taxable_income = max(0, base_salary - total_insurance - 5000 - special_deduction)
income_tax = calculate_tax(taxable_income) if taxable_income > 0 else 0
net_salary = base_salary - total_insurance - income_tax

# 展示结果
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 五险一金明细")
    insurance_df = pd.DataFrame({
        "项目": list(insurance.keys()),
        "金额(元)": list(insurance.values())
    })
    st.dataframe(insurance_df.style.format({"金额(元)": "{:.2f}"}), hide_index=True)
    st.metric("五险一金总额", f"¥{total_insurance:,.2f}")

with col2:
    st.subheader("🧮 个税计算")
    # 确定税率和速算扣除数
    tax_rate = next((TAX_RATES[i-1] for i in range(1, len(TAX_BRACKETS)) 
                   if taxable_income <= TAX_BRACKETS[i]), TAX_RATES[-1])
    tax_deduction = next((TAX_DEDUCTIONS[i-1] for i in range(1, len(TAX_BRACKETS)) 
                        if taxable_income <= TAX_BRACKETS[i]), TAX_DEDUCTIONS[-1])
    
    tax_data = {
        "项目": ["应纳税所得额", "适用税率", "速算扣除数", "个人所得税"],
        "金额/比例": [
            f"¥{taxable_income:,.2f}", 
            f"{tax_rate*100:.1f}%",
            f"¥{tax_deduction}",
            f"¥{income_tax:,.2f}"
        ]
    }
    st.dataframe(pd.DataFrame(tax_data), hide_index=True)
    st.metric("税后工资", f"¥{net_salary:,.2f}", delta_color="inverse")

# ============== 修改后的工资构成分析 ==============
st.subheader("工资构成分析")
if base_salary > 0:
    # 使用进度条直观展示各项占比
    st.progress(min(1.0, net_salary/base_salary), text=f"税后工资: ¥{net_salary:,.2f} ({net_salary/base_salary*100:.1f}%)")
    st.progress(min(1.0, total_insurance/base_salary), text=f"五险一金: ¥{total_insurance:,.2f} ({total_insurance/base_salary*100:.1f}%)")
    st.progress(min(1.0, income_tax/base_salary), text=f"个人所得税: ¥{income_tax:,.2f} ({income_tax/base_salary*100:.1f}%)")
    
    # 添加数值说明
    st.caption(f"基本工资总额: ¥{base_salary:,.2f}")
else:
    st.warning("工资数据异常，无法生成分析")
# ============== 修改结束 ==============

# 专业说明和报告下载
with st.expander("💡 技术说明与应用场景"):
    st.write("""
    **技术亮点：**
    - 实时响应参数变化，计算结果即时更新
    - 内置2025年中国最新个税算法
    - 自动适配不同城市社保政策
    - 可视化展示工资构成
    
    **HR应用场景：**
    1. 新员工薪资方案快速测算
    2. 不同城市用工成本对比
    3. 年度调薪方案模拟
    """)
    
if st.button("📥 生成薪酬报告"):
    report = f"""
    【{city}】薪资测算报告
    ========================
    基本工资：¥{base_salary:,.2f}
    城市社保方案：{city}预设
    
    【五险一金明细】
    - 养老保险：¥{insurance['养老保险']:,.2f} ({pension_rate}%)
    - 医疗保险：¥{insurance['医疗保险']:,.2f} ({medical_rate}%)
    - 失业保险：¥{insurance['失业保险']:,.2f} ({unemployment_rate}%)
    - 工伤保险：¥{insurance['工伤保险']:,.2f} ({injury_rate}%)
    - 生育保险：¥{insurance['生育保险']:,.2f} ({maternity_rate}%)
    - 住房公积金：¥{insurance['住房公积金']:,.2f} ({housing_rate}%)
    
    【个税计算】
    - 应纳税所得额：¥{taxable_income:,.2f}
    - 适用税率：{tax_rate*100:.1f}%
    - 个人所得税：¥{income_tax:,.2f}
    
    【最终收入】
    💰 税后工资：¥{net_salary:,.2f}
    
    【工资构成比例】
    - 税后工资: {net_salary/base_salary*100:.1f}%
    - 五险一金: {total_insurance/base_salary*100:.1f}%
    - 个人所得税: {income_tax/base_salary*100:.1f}%
    """
    st.download_button("下载报告", report, file_name=f"{city}_薪资测算_{base_salary}元.txt")