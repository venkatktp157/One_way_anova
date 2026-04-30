import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from groq import Groq
import os
from dotenv import load_dotenv

# Initialize environment and Groq
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Universal ANOVA Analyzer", layout="wide")

def get_llm_analysis(anova_res, posthoc_res, metric_name):
    """Generic prompt for any numerical comparison."""
    prompt = f"""
    Analyze the following One-Way ANOVA results for the metric: '{metric_name}'.
    
    ANOVA Data:
    {anova_res}
    
    Post-hoc Comparisons (Tukey HSD):
    {posthoc_res}
    
    Please provide:
    1. A clear statement on whether a statistically significant difference exists.
    2. Identify which specific groups are the outliers or differ the most.
    3. Provide a 'Technical Inference': What does this variance imply for the process being measured?
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {e}"

st.title("📊 Universal One-Way ANOVA Suite")
st.markdown("Compare 3+ groups for any metric (Speed, Power, Fuel, etc.) with AI-powered inferences.")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("1. Configuration")
metric_label = st.sidebar.text_input("Metric Name (e.g., Speed, Power, FOC)", "Value")
data_source = st.sidebar.radio("Data Source", ["Manual Entry", "File Upload (.csv, .xlsx)"])

df = pd.DataFrame()

# --- DATA INPUT LOGIC ---
if data_source == "Manual Entry":
    num_groups = st.sidebar.slider("Number of Groups/Columns", 3, 10, 3)
    cols = st.columns(num_groups)
    input_dict = {}
    for i, col in enumerate(cols):
        g_name = col.text_input(f"Group {i+1} Name", f"Group_{i+1}")
        raw_input = col.text_area(f"Data for {g_name}", "10, 11, 10.5", help="Comma-separated values", key=f"in_{i}")
        vals = [float(x.strip()) for x in raw_input.split(",") if x.strip()]
        input_dict[g_name] = vals
    
    # Normalize lengths with NaNs
    max_l = max(len(v) for v in input_dict.values()) if input_dict else 0
    for k in input_dict:
        input_dict[k] += [np.nan] * (max_l - len(input_dict[k]))
    df = pd.DataFrame(input_dict)

else:
    uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=['csv', 'xlsx'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

# --- ANALYSIS ENGINE ---
if not df.empty:
    df_clean = df.dropna(how='all', axis=1)
    df_melted = df_clean.melt(var_name='Group', value_name=metric_label).dropna()
    
    st.subheader(f"📊 {metric_label} Performance Analysis")
    
    # 1. VISUALS (Box plot with modern styling)
    fig = px.box(df_melted, x='Group', y=metric_label, color='Group', points="all", 
                 notched=True, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 2. STATISTICAL CALCULATIONS
    groups_list = [df_clean[c].dropna() for c in df_clean.columns]
    f_stat, p_val = stats.f_oneway(*groups_list)
    
    # Calculate F-Critical
    df_between = len(groups_list) - 1
    df_within = sum(len(g) for g in groups_list) - len(groups_list)
    f_critical = stats.f.ppf(q=1-0.05, dfn=df_between, dfd=df_within)
    
    # 3. KPIs (Including F-Critical)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("F-Calculated", f"{f_stat:.4f}")
    k2.metric("F-Critical (α=0.05)", f"{f_critical:.4f}")
    k3.metric("P-Value", f"{p_val:.4e}") # Using scientific notation for very small p-values
    k4.metric("Status", "Significant" if f_stat > f_critical else "Non-Sig")

    # 4. ANOVA TABLE
    formula = f'Q("{metric_label}") ~ C(Group)'
    model = ols(formula, data=df_melted).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    st.write("### Variance Components (SST = SSC + SSE)")
    st.dataframe(anova_table.style.highlight_max(axis=0, color='#2c3e50'), use_container_width=True)

    # 5. POST-HOC (Visual Appeal)
    if f_stat > f_critical:
        st.success(f"✅ The calculated F ({f_stat:.2f}) exceeds the Critical F ({f_critical:.2f}). Significant differences found.")
        
        # Convert Tukey to a clean DataFrame for display
        tukey = pairwise_tukeyhsd(endog=df_melted[metric_label], groups=df_melted['Group'], alpha=0.05)
        tukey_df = pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0])
        
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.write("### Pairwise Comparisons (Tukey HSD)")
            # Style the 'reject' column to make it pop
            def highlight_reject(val):
                color = '#27ae60' if val == True else '#c0392b'
                return f'background-color: {color}; color: white; font-weight: bold'
            
            st.dataframe(tukey_df.style.applymap(highlight_reject, subset=['reject']), use_container_width=True)
        
        with col_right:
            st.write("### AI Executive Inference")
            if st.button("🚀 Generate AI Interpretation"):
                with st.spinner("Consulting Groq..."):
                    ai_report = get_llm_analysis(anova_table.to_string(), tukey_df.to_string(), metric_label)
                    st.info(ai_report)