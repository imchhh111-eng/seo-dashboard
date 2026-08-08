
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import os

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="SEO Health Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 设计系统（SaaS 风格）
# ============================================================
C = {
    'blue': '#2563EB',
    'blue_light': '#EFF6FF',
    'blue_dark': '#1D4ED8',
    'green': '#10B981',
    'green_bg': '#ECFDF5',
    'amber': '#F59E0B',
    'amber_bg': '#FFFBEB',
    'red': '#EF4444',
    'red_bg': '#FEF2F2',
    'gray_900': '#111827',
    'gray_700': '#374151',
    'gray_500': '#6B7280',
    'gray_400': '#9CA3AF',
    'gray_200': '#E5E7EB',
    'gray_100': '#F3F4F6',
    'gray_50': '#F9FAFB',
    'white': '#FFFFFF',
    'chart': ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'],
}

# ============================================================
# 全局 CSS（SaaS 风格，无渐变）
# ============================================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {C['gray_50']}; }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    .card {{
        background: {C['white']};
        border: 1px solid {C['gray_200']};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }}
    .card-sm {{
        background: {C['white']};
        border: 1px solid {C['gray_200']};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }}
    .card-title {{
        font-size: 11px; font-weight: 700; color: {C['gray_400']};
        text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;
    }}
    .kpi-box {{
        background: {C['white']};
        border: 1px solid {C['gray_200']};
        border-radius: 12px;
        padding: 16px 12px; text-align: center;
    }}
    .kpi-label {{ font-size: 11px; font-weight: 500; color: {C['gray_500']}; }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: {C['gray_900']}; margin-top: 2px; }}

    .score-ring {{
        width: 100px; height: 100px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 32px; font-weight: 800;
        border: 4px solid;
    }}
    .score-A {{ border-color: {C['green']}; color: {C['green']}; background: {C['green_bg']}; }}
    .score-B {{ border-color: {C['blue']}; color: {C['blue']}; background: {C['blue_light']}; }}
    .score-C {{ border-color: {C['amber']}; color: {C['amber']}; background: {C['amber_bg']}; }}
    .score-D {{ border-color: {C['red']}; color: {C['red']}; background: {C['red_bg']}; }}

    .insight-box {{
        background: {C['blue_light']};
        border-left: 3px solid {C['blue']};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 12px 0;
    }}
    .insight-box .insight-title {{
        font-size: 11px; font-weight: 700; color: {C['blue']};
        text-transform: uppercase; margin-bottom: 4px;
    }}
    .insight-box .insight-text {{
        font-size: 13px; color: {C['gray_700']}; line-height: 1.5;
    }}

    .warn-box {{
        background: {C['amber_bg']};
        border-left: 3px solid {C['amber']};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px; margin: 12px 0;
    }}
    .warn-box .warn-title {{
        font-size: 11px; font-weight: 700; color: {C['amber']};
        text-transform: uppercase; margin-bottom: 4px;
    }}
    .warn-box .warn-text {{ font-size: 13px; color: {C['gray_700']}; }}

    .priority-P0 {{ background: {C['red_bg']}; color: {C['red']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}
    .priority-P1 {{ background: {C['amber_bg']}; color: {C['amber']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}
    .priority-P2 {{ background: {C['blue_light']}; color: {C['blue']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}

    .empty-state {{
        text-align: center; padding: 48px 24px;
        border: 2px dashed {C['gray_200']}; border-radius: 16px; margin: 24px 0;
    }}
    .empty-state .icon {{ font-size: 48px; margin-bottom: 12px; }}
    .empty-state .msg {{ font-size: 13px; color: {C['gray_500']}; }}

    .nav-group {{
        font-size: 10px; font-weight: 700; color: {C['gray_400']};
        text-transform: uppercase; letter-spacing: 1px;
        margin: 16px 0 6px 0;
    }}

    .dim-bar {{
        height: 8px; border-radius: 4px; background: {C['gray_100']};
        overflow: hidden; margin-top: 4px;
    }}
    .dim-bar-fill {{ height: 100%; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Plotly 模板
# ============================================================
tpl = go.layout.Template()
tpl.layout = go.Layout(
    font=dict(family="-apple-system, BlinkMacSystemFont, sans-serif", size=12, color=C['gray_700']),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=8, r=8, t=32, b=8),
    colorway=C['chart'],
    xaxis=dict(gridcolor=C['gray_200'], zeroline=False),
    yaxis=dict(gridcolor=C['gray_200'], zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
)
pio.templates['saas'] = tpl
pio.templates.default = 'saas'

# ============================================================
# 多语言
# ============================================================
T = {
    "中文": {
        "brand": "SEO 健康智能分析平台",
        "brand_sub": "将搜索数据转化为可执行的 SEO 洞察 · Powered by GSC",
        "nav_exec": "🏠 Executive Overview",
        "nav_health": "🎯 SEO Health Score",
        "nav_trend": "📈 搜索趋势",
        "nav_keyword": "🔍 关键词洞察",
        "nav_page": "📄 页面效果",
        "nav_country": "🌍 国家/地区",
        "nav_device": "📱 设备分布",
        "nav_anomaly": "🚨 异常监控",
        "nav_recommend": "💡 优化建议",
        "group_overview": "概览", "group_intelligence": "搜索智能",
        "group_content": "内容智能", "group_market": "市场智能",
        "group_monitor": "监控", "group_action": "行动",
        "total_clicks": "总点击", "total_impressions": "总展示",
        "avg_ctr": "平均CTR", "avg_position": "平均排名",
        "health_score": "健康度评分", "grade": "等级", "score": "分数",
        "search_perf": "搜索表现", "content_eff": "内容效果", "tech_exp": "技术体验",
        "start_date": "开始日期", "end_date": "结束日期",
        "clicks": "点击", "impressions": "展示", "ctr": "CTR", "position": "排名",
        "country": "国家/地区", "device": "设备",
        "export_csv": "📥 导出", "no_data": "暂无数据",
        "no_data_desc": "请检查 data/ 文件夹中是否包含对应的 CSV 文件",
        "sensitivity": "灵敏度", "select_metric": "检测指标",
        "days_analyzed": "检测天数", "anomalies_found": "异常点", "anomaly_rate": "异常率",
        "normal": "正常", "anomaly": "异常", "rolling_mean": "7日均值",
        "anomaly_events": "异常事件", "actual": "实际值", "expected": "期望值",
        "total_keywords": "关键词总数", "kw_with_clicks": "有点击词",
        "position_dist": "排名分布", "opportunity_kw": "机会关键词",
        "opportunity_kw_desc": "高展示 + 低CTR + 排名11-30，优化后可快速提升",
        "top_keywords": "Top 关键词",
        "total_pages": "总页面", "pages_with_clicks": "有点击页面", "active_rate": "活跃率",
        "page_matrix": "页面机会矩阵",
        "opportunity_pages": "高展示低CTR页面",
        "opportunity_pages_desc": "展示高但CTR低，优化标题/描述可快速提升",
        "top_pages": "Top 页面",
        "countries_covered": "覆盖国家", "top_countries": "Top 国家",
        "geo_map": "全球流量分布", "detail_data": "详细数据",
        "imp_share": "展示占比", "click_share": "点击占比",
        "device_compare": "设备对比", "device_trend": "月度趋势",
        "monthly_summary": "月度汇总",
        "scoring_method": "评分方法",
        "backlink_reserved": "外链权威（待接入）",
        "backlink_desc": "外链权威维度已预留，待接入 Ahrefs/Moz API 后启用。届时权重：搜索35% + 内容30% + 技术20% + 外链15%",
        "data_missing_warn": "⚠️ 部分数据源缺失",
        "rec_title": "优化建议",
        "key_finding": "关键发现", "recommendation": "建议行动",
        "main_opportunity": "核心机会", "strength": "优势", "weakness": "短板",
        "exec_summary": "AI 诊断摘要",
        "score_path": "评分提升路径",
        "model_arch": "模型架构",
    },
    "English": {
        "brand": "SEO Health Intelligence Platform",
        "brand_sub": "Transform Search Data into Actionable SEO Insights · Powered by GSC",
        "nav_exec": "🏠 Executive Overview",
        "nav_health": "🎯 SEO Health Score",
        "nav_trend": "📈 Search Trends",
        "nav_keyword": "🔍 Keyword Insights",
        "nav_page": "📄 Page Performance",
        "nav_country": "🌍 Country/Region",
        "nav_device": "📱 Device Distribution",
        "nav_anomaly": "🚨 Anomaly Monitor",
        "nav_recommend": "💡 Recommendations",
        "group_overview": "Overview", "group_intelligence": "Search Intelligence",
        "group_content": "Content Intelligence", "group_market": "Market Intelligence",
        "group_monitor": "Monitoring", "group_action": "Action",
        "total_clicks": "Total Clicks", "total_impressions": "Total Impressions",
        "avg_ctr": "Avg CTR", "avg_position": "Avg Position",
        "health_score": "Health Score", "grade": "Grade", "score": "Score",
        "search_perf": "Search Performance", "content_eff": "Content Effectiveness", "tech_exp": "Technical Experience",
        "start_date": "Start Date", "end_date": "End Date",
        "clicks": "Clicks", "impressions": "Impressions", "ctr": "CTR", "position": "Position",
        "country": "Country/Region", "device": "Device",
        "export_csv": "📥 Export", "no_data": "No Data",
        "no_data_desc": "Please check if CSV files exist in data/ folder",
        "sensitivity": "Sensitivity", "select_metric": "Metric",
        "days_analyzed": "Days", "anomalies_found": "Anomalies", "anomaly_rate": "Rate",
        "normal": "Normal", "anomaly": "Anomaly", "rolling_mean": "7-day Mean",
        "anomaly_events": "Anomaly Events", "actual": "Actual", "expected": "Expected",
        "total_keywords": "Keywords", "kw_with_clicks": "With Clicks",
        "position_dist": "Position Distribution", "opportunity_kw": "Opportunity Keywords",
        "opportunity_kw_desc": "High impressions + Low CTR + Position 11-30, quick wins",
        "top_keywords": "Top Keywords",
        "total_pages": "Pages", "pages_with_clicks": "With Clicks", "active_rate": "Active Rate",
        "page_matrix": "Page Opportunity Matrix",
        "opportunity_pages": "High Impression Low CTR Pages",
        "opportunity_pages_desc": "High impressions but low CTR, optimize title/description",
        "top_pages": "Top Pages",
        "countries_covered": "Countries", "top_countries": "Top Countries",
        "geo_map": "Global Traffic Map", "detail_data": "Details",
        "imp_share": "Impression Share", "click_share": "Click Share",
        "device_compare": "Device Comparison", "device_trend": "Monthly Trend",
        "monthly_summary": "Monthly Summary",
        "scoring_method": "Methodology",
        "backlink_reserved": "Backlink Authority (Coming Soon)",
        "backlink_desc": "Backlink authority reserved. Once Ahrefs/Moz integrated: Search 35% + Content 30% + Technical 20% + Backlinks 15%",
        "data_missing_warn": "⚠️ Some data sources missing",
        "rec_title": "Recommendations",
        "key_finding": "Key Finding", "recommendation": "Recommendation",
        "main_opportunity": "Main Opportunity", "strength": "Strength", "weakness": "Weakness",
        "exec_summary": "AI Diagnostic Summary",
        "score_path": "Score Improvement Path",
        "model_arch": "Model Architecture",
    }
}

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
    base_path = "data/"
    data = {}
    file_mapping = {
        'by_date': 'cleaned_by_date.csv',
        'by_country': 'cleaned_by_country.csv',
        'by_device': 'cleaned_by_device.csv',
        'daily_summary': 'cleaned_daily_summary.csv',
        'by_query': 'cleaned_by_query.csv',
        'by_page': 'cleaned_by_page.csv',
    }
    for key, filename in file_mapping.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if 'data_date' in df.columns:
                df['data_date'] = pd.to_datetime(df['data_date'])
            data[key] = df
        else:
            data[key] = None
    return data

data = load_data()

# ============================================================
# SEO 健康度评分 V2.0
# ============================================================
def calculate_health_score(data):
    scores = {}
    missing = []

    # 搜索表现 (40%)
    s_scores = []
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        avg_ctr = df['ctr'].mean()
        ctr_score = min(100, (avg_ctr / 0.03) * 100)
        s_scores.append(ctr_score)
        avg_pos = df['position'].mean()
        if avg_pos <= 10:
            pos_score = 100
        elif avg_pos <= 20:
            pos_score = 80 - (avg_pos - 10) * 2
        elif avg_pos <= 50:
            pos_score = 60 - (avg_pos - 20)
        else:
            pos_score = max(10, 30 - (avg_pos - 50) * 0.5)
        s_scores.append(pos_score)
        df_s = df.sort_values('data_date')
        if len(df_s) >= 6:
            recent = df_s.tail(len(df_s) // 3)['clicks'].mean()
            earlier = df_s.head(len(df_s) // 3)['clicks'].mean()
            ratio = recent / earlier if earlier > 0 else 1
            if ratio >= 1.2:
                trend_score = 90
            elif ratio >= 0.8:
                trend_score = 70
            elif ratio >= 0.5:
                trend_score = 50
            else:
                trend_score = 30
        else:
            trend_score = 50
        s_scores.append(trend_score)
    else:
        missing.append('daily_summary')
    scores['search'] = round(np.mean(s_scores), 1) if s_scores else 0

    # 内容效果 (35%)
    c_scores = []
    if data.get('by_query') is not None:
        uq = data['by_query']['query'].nunique()
        if uq >= 500:
            c_scores.append(90)
        elif uq >= 200:
            c_scores.append(70 + (uq - 200) / 300 * 20)
        elif uq >= 50:
            c_scores.append(50 + (uq - 50) / 150 * 20)
        else:
            c_scores.append(max(20, uq))
    else:
        missing.append('by_query')
    if data.get('by_page') is not None:
        dp = data['by_page']
        tp = dp['page'].nunique()
        ap = dp[dp['clicks'] > 0]['page'].nunique()
        c_scores.append(min(100, (ap / tp * 100 * 2)) if tp > 0 else 0)
    else:
        missing.append('by_page')
    if data.get('by_country') is not None:
        uc = data['by_country']['country'].nunique()
        c_scores.append(min(100, (uc / 50) * 100))
    else:
        missing.append('by_country')
    scores['content'] = round(np.mean(c_scores), 1) if c_scores else 0

    # 技术体验 (25%)
    t_scores = []
    if data.get('by_device') is not None:
        dd = data['by_device']
        t_scores.append(min(100, (dd['device'].nunique() / 3) * 100))
        ti = dd['impressions'].sum()
        if ti > 0:
            mr = dd[dd['device'] == 'MOBILE']['impressions'].sum() / ti
            if 0.15 <= mr <= 0.35:
                t_scores.append(90)
            elif 0.10 <= mr <= 0.45:
                t_scores.append(70)
            else:
                t_scores.append(50)
        else:
            t_scores.append(50)
    else:
        missing.append('by_device')
    if data.get('by_date') is not None:
        dfd = data['by_date']
        td = (dfd['data_date'].max() - dfd['data_date'].min()).days
        ad = dfd['data_date'].nunique()
        t_scores.append(min(100, (ad / td * 100)) if td > 0 else 50)
    else:
        missing.append('by_date')
    scores['tech'] = round(np.mean(t_scores), 1) if t_scores else 0

    total = scores['search'] * 0.40 + scores['content'] * 0.35 + scores['tech'] * 0.25
    scores['total'] = round(total, 1)
    scores['grade'] = 'A' if total >= 90 else 'B' if total >= 70 else 'C' if total >= 50 else 'D'
    scores['grade_label'] = {'A': 'Excellent', 'B': 'Good', 'C': 'Moderate', 'D': 'Needs Work'}[scores['grade']]
    scores['grade_cn'] = {'A': '优秀', 'B': '良好', 'C': '一般', 'D': '较差'}[scores['grade']]
    scores['missing'] = missing
    return scores

health = calculate_health_score(data)

# ============================================================
# 侧边栏（分组导航）
# ============================================================
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:12px 0 16px;'>"
                f"<div style='font-size:24px;'>🎯</div>"
                f"<div style='font-size:14px; font-weight:700; color:{C['gray_900']}; margin-top:4px;'>SEO Health</div>"
                f"<div style='font-size:10px; color:{C['gray_500']}; margin-top:2px;'>Intelligence Platform v2.0</div>"
                f"</div>", unsafe_allow_html=True)
    st.markdown("---")

    lang = st.selectbox("🌐", list(T.keys()), label_visibility="collapsed")
    t = T[lang]

    # 分组导航
    st.markdown(f"<div class='nav-group'>{t['group_overview']}</div>", unsafe_allow_html=True)
    nav_list = [t['nav_exec'], t['nav_health']]

    st.markdown(f"<div class='nav-group'>{t['group_intelligence']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_trend'], t['nav_keyword']]

    st.markdown(f"<div class='nav-group'>{t['group_content']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_page']]

    st.markdown(f"<div class='nav-group'>{t['group_market']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_country'], t['nav_device']]

    st.markdown(f"<div class='nav-group'>{t['group_monitor']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_anomaly']]

    st.markdown(f"<div class='nav-group'>{t['group_action']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_recommend']]

    page = st.radio("nav", nav_list, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"<p style='font-size:10px; font-weight:700; color:{C['gray_400']}; letter-spacing:1px;'>📅 DATA FILTER</p>", unsafe_allow_html=True)
    if data.get('by_date') is not None:
        min_d = data['by_date']['data_date'].min().date()
        max_d = data['by_date']['data_date'].max().date()
        g_start = st.date_input(t['start_date'], value=min_d, min_value=min_d, max_value=max_d)
        g_end = st.date_input(t['end_date'], value=max_d, min_value=min_d, max_value=max_d)
    else:
        g_start, g_end = None, None

    st.markdown("---")
    st.caption(t['brand_sub'])

# ============================================================
# 辅助函数
# ============================================================
def empty_state(icon, msg=""):
    st.markdown(f"<div class='empty-state'><div class='icon'>{icon}</div>"
                f"<div class='msg'>{msg or t['no_data_desc']}</div></div>", unsafe_allow_html=True)

def date_filter(df, s, e):
    if s and e and 'data_date' in df.columns:
        return df[(df['data_date'].dt.date >= s) & (df['data_date'].dt.date <= e)]
    return df

def csv_export(df, name):
    st.download_button(t['export_csv'], df.to_csv(index=False).encode('utf-8-sig'), name, 'text/csv')

def kpi(label, value):
    return f"<div class='kpi-box'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>"

def insight_box(text):
    title = t['key_finding']
    st.markdown(f"<div class='insight-box'><div class='insight-title'>💡 {title}</div>"
                f"<div class='insight-text'>{text}</div></div>", unsafe_allow_html=True)

def warn_box(text):
    title = t['recommendation']
    st.markdown(f"<div class='warn-box'><div class='warn-title'>🎯 {title}</div>"
                f"<div class='warn-text'>{text}</div></div>", unsafe_allow_html=True)

def dim_bar(label, score, weight):
    color = C['green'] if score >= 70 else C['amber'] if score >= 50 else C['red']
    return f"""<div style='margin-bottom:12px;'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <span style='font-size:13px; font-weight:500; color:{C["gray_700"]};'>{label}</span>
            <span style='font-size:13px; font-weight:700; color:{C["gray_900"]};'>{score}</span>
        </div>
        <div style='font-size:10px; color:{C["gray_400"]}; margin-bottom:4px;'>Weight: {weight}%</div>
        <div class='dim-bar'><div class='dim-bar-fill' style='width:{score}%; background:{color};'></div></div>
    </div>"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import os

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="SEO Health Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 设计系统（SaaS 风格）
# ============================================================
C = {
    'blue': '#2563EB',
    'blue_light': '#EFF6FF',
    'blue_dark': '#1D4ED8',
    'green': '#10B981',
    'green_bg': '#ECFDF5',
    'amber': '#F59E0B',
    'amber_bg': '#FFFBEB',
    'red': '#EF4444',
    'red_bg': '#FEF2F2',
    'gray_900': '#111827',
    'gray_700': '#374151',
    'gray_500': '#6B7280',
    'gray_400': '#9CA3AF',
    'gray_200': '#E5E7EB',
    'gray_100': '#F3F4F6',
    'gray_50': '#F9FAFB',
    'white': '#FFFFFF',
    'chart': ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'],
}

# ============================================================
# 全局 CSS（SaaS 风格，无渐变）
# ============================================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {C['gray_50']}; }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    .card {{
        background: {C['white']};
        border: 1px solid {C['gray_200']};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }}
    .card-sm {{
        background: {C['white']};
        border: 1px solid {C['gray_200']};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }}
    .card-title {{
        font-size: 11px; font-weight: 700; color: {C['gray_400']};
        text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;
    }}
    .kpi-box {{
        background: {C['white']};
        border: 1px solid {C['gray_200']};
        border-radius: 12px;
        padding: 16px 12px; text-align: center;
    }}
    .kpi-label {{ font-size: 11px; font-weight: 500; color: {C['gray_500']}; }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: {C['gray_900']}; margin-top: 2px; }}

    .score-ring {{
        width: 100px; height: 100px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 32px; font-weight: 800;
        border: 4px solid;
    }}
    .score-A {{ border-color: {C['green']}; color: {C['green']}; background: {C['green_bg']}; }}
    .score-B {{ border-color: {C['blue']}; color: {C['blue']}; background: {C['blue_light']}; }}
    .score-C {{ border-color: {C['amber']}; color: {C['amber']}; background: {C['amber_bg']}; }}
    .score-D {{ border-color: {C['red']}; color: {C['red']}; background: {C['red_bg']}; }}

    .insight-box {{
        background: {C['blue_light']};
        border-left: 3px solid {C['blue']};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 12px 0;
    }}
    .insight-box .insight-title {{
        font-size: 11px; font-weight: 700; color: {C['blue']};
        text-transform: uppercase; margin-bottom: 4px;
    }}
    .insight-box .insight-text {{
        font-size: 13px; color: {C['gray_700']}; line-height: 1.5;
    }}

    .warn-box {{
        background: {C['amber_bg']};
        border-left: 3px solid {C['amber']};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px; margin: 12px 0;
    }}
    .warn-box .warn-title {{
        font-size: 11px; font-weight: 700; color: {C['amber']};
        text-transform: uppercase; margin-bottom: 4px;
    }}
    .warn-box .warn-text {{ font-size: 13px; color: {C['gray_700']}; }}

    .priority-P0 {{ background: {C['red_bg']}; color: {C['red']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}
    .priority-P1 {{ background: {C['amber_bg']}; color: {C['amber']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}
    .priority-P2 {{ background: {C['blue_light']}; color: {C['blue']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}

    .empty-state {{
        text-align: center; padding: 48px 24px;
        border: 2px dashed {C['gray_200']}; border-radius: 16px; margin: 24px 0;
    }}
    .empty-state .icon {{ font-size: 48px; margin-bottom: 12px; }}
    .empty-state .msg {{ font-size: 13px; color: {C['gray_500']}; }}

    .nav-group {{
        font-size: 10px; font-weight: 700; color: {C['gray_400']};
        text-transform: uppercase; letter-spacing: 1px;
        margin: 16px 0 6px 0;
    }}

    .dim-bar {{
        height: 8px; border-radius: 4px; background: {C['gray_100']};
        overflow: hidden; margin-top: 4px;
    }}
    .dim-bar-fill {{ height: 100%; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Plotly 模板
# ============================================================
tpl = go.layout.Template()
tpl.layout = go.Layout(
    font=dict(family="-apple-system, BlinkMacSystemFont, sans-serif", size=12, color=C['gray_700']),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=8, r=8, t=32, b=8),
    colorway=C['chart'],
    xaxis=dict(gridcolor=C['gray_200'], zeroline=False),
    yaxis=dict(gridcolor=C['gray_200'], zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
)
pio.templates['saas'] = tpl
pio.templates.default = 'saas'

# ============================================================
# 多语言
# ============================================================
T = {
    "中文": {
        "brand": "SEO 健康智能分析平台",
        "brand_sub": "将搜索数据转化为可执行的 SEO 洞察 · Powered by GSC",
        "nav_exec": "🏠 Executive Overview",
        "nav_health": "🎯 SEO Health Score",
        "nav_trend": "📈 搜索趋势",
        "nav_keyword": "🔍 关键词洞察",
        "nav_page": "📄 页面效果",
        "nav_country": "🌍 国家/地区",
        "nav_device": "📱 设备分布",
        "nav_anomaly": "🚨 异常监控",
        "nav_recommend": "💡 优化建议",
        "group_overview": "概览", "group_intelligence": "搜索智能",
        "group_content": "内容智能", "group_market": "市场智能",
        "group_monitor": "监控", "group_action": "行动",
        "total_clicks": "总点击", "total_impressions": "总展示",
        "avg_ctr": "平均CTR", "avg_position": "平均排名",
        "health_score": "健康度评分", "grade": "等级", "score": "分数",
        "search_perf": "搜索表现", "content_eff": "内容效果", "tech_exp": "技术体验",
        "start_date": "开始日期", "end_date": "结束日期",
        "clicks": "点击", "impressions": "展示", "ctr": "CTR", "position": "排名",
        "country": "国家/地区", "device": "设备",
        "export_csv": "📥 导出", "no_data": "暂无数据",
        "no_data_desc": "请检查 data/ 文件夹中是否包含对应的 CSV 文件",
        "sensitivity": "灵敏度", "select_metric": "检测指标",
        "days_analyzed": "检测天数", "anomalies_found": "异常点", "anomaly_rate": "异常率",
        "normal": "正常", "anomaly": "异常", "rolling_mean": "7日均值",
        "anomaly_events": "异常事件", "actual": "实际值", "expected": "期望值",
        "total_keywords": "关键词总数", "kw_with_clicks": "有点击词",
        "position_dist": "排名分布", "opportunity_kw": "机会关键词",
        "opportunity_kw_desc": "高展示 + 低CTR + 排名11-30，优化后可快速提升",
        "top_keywords": "Top 关键词",
        "total_pages": "总页面", "pages_with_clicks": "有点击页面", "active_rate": "活跃率",
        "page_matrix": "页面机会矩阵",
        "opportunity_pages": "高展示低CTR页面",
        "opportunity_pages_desc": "展示高但CTR低，优化标题/描述可快速提升",
        "top_pages": "Top 页面",
        "countries_covered": "覆盖国家", "top_countries": "Top 国家",
        "geo_map": "全球流量分布", "detail_data": "详细数据",
        "imp_share": "展示占比", "click_share": "点击占比",
        "device_compare": "设备对比", "device_trend": "月度趋势",
        "monthly_summary": "月度汇总",
        "scoring_method": "评分方法",
        "backlink_reserved": "外链权威（待接入）",
        "backlink_desc": "外链权威维度已预留，待接入 Ahrefs/Moz API 后启用。届时权重：搜索35% + 内容30% + 技术20% + 外链15%",
        "data_missing_warn": "⚠️ 部分数据源缺失",
        "rec_title": "优化建议",
        "key_finding": "关键发现", "recommendation": "建议行动",
        "main_opportunity": "核心机会", "strength": "优势", "weakness": "短板",
        "exec_summary": "AI 诊断摘要",
        "score_path": "评分提升路径",
        "model_arch": "模型架构",
    },
    "English": {
        "brand": "SEO Health Intelligence Platform",
        "brand_sub": "Transform Search Data into Actionable SEO Insights · Powered by GSC",
        "nav_exec": "🏠 Executive Overview",
        "nav_health": "🎯 SEO Health Score",
        "nav_trend": "📈 Search Trends",
        "nav_keyword": "🔍 Keyword Insights",
        "nav_page": "📄 Page Performance",
        "nav_country": "🌍 Country/Region",
        "nav_device": "📱 Device Distribution",
        "nav_anomaly": "🚨 Anomaly Monitor",
        "nav_recommend": "💡 Recommendations",
        "group_overview": "Overview", "group_intelligence": "Search Intelligence",
        "group_content": "Content Intelligence", "group_market": "Market Intelligence",
        "group_monitor": "Monitoring", "group_action": "Action",
        "total_clicks": "Total Clicks", "total_impressions": "Total Impressions",
        "avg_ctr": "Avg CTR", "avg_position": "Avg Position",
        "health_score": "Health Score", "grade": "Grade", "score": "Score",
        "search_perf": "Search Performance", "content_eff": "Content Effectiveness", "tech_exp": "Technical Experience",
        "start_date": "Start Date", "end_date": "End Date",
        "clicks": "Clicks", "impressions": "Impressions", "ctr": "CTR", "position": "Position",
        "country": "Country/Region", "device": "Device",
        "export_csv": "📥 Export", "no_data": "No Data",
        "no_data_desc": "Please check if CSV files exist in data/ folder",
        "sensitivity": "Sensitivity", "select_metric": "Metric",
        "days_analyzed": "Days", "anomalies_found": "Anomalies", "anomaly_rate": "Rate",
        "normal": "Normal", "anomaly": "Anomaly", "rolling_mean": "7-day Mean",
        "anomaly_events": "Anomaly Events", "actual": "Actual", "expected": "Expected",
        "total_keywords": "Keywords", "kw_with_clicks": "With Clicks",
        "position_dist": "Position Distribution", "opportunity_kw": "Opportunity Keywords",
        "opportunity_kw_desc": "High impressions + Low CTR + Position 11-30, quick wins",
        "top_keywords": "Top Keywords",
        "total_pages": "Pages", "pages_with_clicks": "With Clicks", "active_rate": "Active Rate",
        "page_matrix": "Page Opportunity Matrix",
        "opportunity_pages": "High Impression Low CTR Pages",
        "opportunity_pages_desc": "High impressions but low CTR, optimize title/description",
        "top_pages": "Top Pages",
        "countries_covered": "Countries", "top_countries": "Top Countries",
        "geo_map": "Global Traffic Map", "detail_data": "Details",
        "imp_share": "Impression Share", "click_share": "Click Share",
        "device_compare": "Device Comparison", "device_trend": "Monthly Trend",
        "monthly_summary": "Monthly Summary",
        "scoring_method": "Methodology",
        "backlink_reserved": "Backlink Authority (Coming Soon)",
        "backlink_desc": "Backlink authority reserved. Once Ahrefs/Moz integrated: Search 35% + Content 30% + Technical 20% + Backlinks 15%",
        "data_missing_warn": "⚠️ Some data sources missing",
        "rec_title": "Recommendations",
        "key_finding": "Key Finding", "recommendation": "Recommendation",
        "main_opportunity": "Main Opportunity", "strength": "Strength", "weakness": "Weakness",
        "exec_summary": "AI Diagnostic Summary",
        "score_path": "Score Improvement Path",
        "model_arch": "Model Architecture",
    }
}

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
    base_path = "data/"
    data = {}
    file_mapping = {
        'by_date': 'cleaned_by_date.csv',
        'by_country': 'cleaned_by_country.csv',
        'by_device': 'cleaned_by_device.csv',
        'daily_summary': 'cleaned_daily_summary.csv',
        'by_query': 'cleaned_by_query.csv',
        'by_page': 'cleaned_by_page.csv',
    }
    for key, filename in file_mapping.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if 'data_date' in df.columns:
                df['data_date'] = pd.to_datetime(df['data_date'])
            data[key] = df
        else:
            data[key] = None
    return data

data = load_data()

# ============================================================
# SEO 健康度评分 V2.0
# ============================================================
def calculate_health_score(data):
    scores = {}
    missing = []

    # 搜索表现 (40%)
    s_scores = []
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        avg_ctr = df['ctr'].mean()
        ctr_score = min(100, (avg_ctr / 0.03) * 100)
        s_scores.append(ctr_score)
        avg_pos = df['position'].mean()
        if avg_pos <= 10:
            pos_score = 100
        elif avg_pos <= 20:
            pos_score = 80 - (avg_pos - 10) * 2
        elif avg_pos <= 50:
            pos_score = 60 - (avg_pos - 20)
        else:
            pos_score = max(10, 30 - (avg_pos - 50) * 0.5)
        s_scores.append(pos_score)
        df_s = df.sort_values('data_date')
        if len(df_s) >= 6:
            recent = df_s.tail(len(df_s) // 3)['clicks'].mean()
            earlier = df_s.head(len(df_s) // 3)['clicks'].mean()
            ratio = recent / earlier if earlier > 0 else 1
            if ratio >= 1.2:
                trend_score = 90
            elif ratio >= 0.8:
                trend_score = 70
            elif ratio >= 0.5:
                trend_score = 50
            else:
                trend_score = 30
        else:
            trend_score = 50
        s_scores.append(trend_score)
    else:
        missing.append('daily_summary')
    scores['search'] = round(np.mean(s_scores), 1) if s_scores else 0

    # 内容效果 (35%)
    c_scores = []
    if data.get('by_query') is not None:
        uq = data['by_query']['query'].nunique()
        if uq >= 500:
            c_scores.append(90)
        elif uq >= 200:
            c_scores.append(70 + (uq - 200) / 300 * 20)
        elif uq >= 50:
            c_scores.append(50 + (uq - 50) / 150 * 20)
        else:
            c_scores.append(max(20, uq))
    else:
        missing.append('by_query')
    if data.get('by_page') is not None:
        dp = data['by_page']
        tp = dp['page'].nunique()
        ap = dp[dp['clicks'] > 0]['page'].nunique()
        c_scores.append(min(100, (ap / tp * 100 * 2)) if tp > 0 else 0)
    else:
        missing.append('by_page')
    if data.get('by_country') is not None:
        uc = data['by_country']['country'].nunique()
        c_scores.append(min(100, (uc / 50) * 100))
    else:
        missing.append('by_country')
    scores['content'] = round(np.mean(c_scores), 1) if c_scores else 0

    # 技术体验 (25%)
    t_scores = []
    if data.get('by_device') is not None:
        dd = data['by_device']
        t_scores.append(min(100, (dd['device'].nunique() / 3) * 100))
        ti = dd['impressions'].sum()
        if ti > 0:
            mr = dd[dd['device'] == 'MOBILE']['impressions'].sum() / ti
            if 0.15 <= mr <= 0.35:
                t_scores.append(90)
            elif 0.10 <= mr <= 0.45:
                t_scores.append(70)
            else:
                t_scores.append(50)
        else:
            t_scores.append(50)
    else:
        missing.append('by_device')
    if data.get('by_date') is not None:
        dfd = data['by_date']
        td = (dfd['data_date'].max() - dfd['data_date'].min()).days
        ad = dfd['data_date'].nunique()
        t_scores.append(min(100, (ad / td * 100)) if td > 0 else 50)
    else:
        missing.append('by_date')
    scores['tech'] = round(np.mean(t_scores), 1) if t_scores else 0

    total = scores['search'] * 0.40 + scores['content'] * 0.35 + scores['tech'] * 0.25
    scores['total'] = round(total, 1)
    scores['grade'] = 'A' if total >= 90 else 'B' if total >= 70 else 'C' if total >= 50 else 'D'
    scores['grade_label'] = {'A': 'Excellent', 'B': 'Good', 'C': 'Moderate', 'D': 'Needs Work'}[scores['grade']]
    scores['grade_cn'] = {'A': '优秀', 'B': '良好', 'C': '一般', 'D': '较差'}[scores['grade']]
    scores['missing'] = missing
    return scores

health = calculate_health_score(data)

# ============================================================
# 侧边栏（分组导航）
# ============================================================
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:12px 0 16px;'>"
                f"<div style='font-size:24px;'>🎯</div>"
                f"<div style='font-size:14px; font-weight:700; color:{C['gray_900']}; margin-top:4px;'>SEO Health</div>"
                f"<div style='font-size:10px; color:{C['gray_500']}; margin-top:2px;'>Intelligence Platform v2.0</div>"
                f"</div>", unsafe_allow_html=True)
    st.markdown("---")

    lang = st.selectbox("🌐", list(T.keys()), label_visibility="collapsed")
    t = T[lang]

    # 分组导航
    st.markdown(f"<div class='nav-group'>{t['group_overview']}</div>", unsafe_allow_html=True)
    nav_list = [t['nav_exec'], t['nav_health']]

    st.markdown(f"<div class='nav-group'>{t['group_intelligence']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_trend'], t['nav_keyword']]

    st.markdown(f"<div class='nav-group'>{t['group_content']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_page']]

    st.markdown(f"<div class='nav-group'>{t['group_market']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_country'], t['nav_device']]

    st.markdown(f"<div class='nav-group'>{t['group_monitor']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_anomaly']]

    st.markdown(f"<div class='nav-group'>{t['group_action']}</div>", unsafe_allow_html=True)
    nav_list += [t['nav_recommend']]

    page = st.radio("nav", nav_list, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"<p style='font-size:10px; font-weight:700; color:{C['gray_400']}; letter-spacing:1px;'>📅 DATA FILTER</p>", unsafe_allow_html=True)
    if data.get('by_date') is not None:
        min_d = data['by_date']['data_date'].min().date()
        max_d = data['by_date']['data_date'].max().date()
        g_start = st.date_input(t['start_date'], value=min_d, min_value=min_d, max_value=max_d)
        g_end = st.date_input(t['end_date'], value=max_d, min_value=min_d, max_value=max_d)
    else:
        g_start, g_end = None, None

    st.markdown("---")
    st.caption(t['brand_sub'])

# ============================================================
# 辅助函数
# ============================================================
def empty_state(icon, msg=""):
    st.markdown(f"<div class='empty-state'><div class='icon'>{icon}</div>"
                f"<div class='msg'>{msg or t['no_data_desc']}</div></div>", unsafe_allow_html=True)

def date_filter(df, s, e):
    if s and e and 'data_date' in df.columns:
        return df[(df['data_date'].dt.date >= s) & (df['data_date'].dt.date <= e)]
    return df

def csv_export(df, name):
    st.download_button(t['export_csv'], df.to_csv(index=False).encode('utf-8-sig'), name, 'text/csv')

def kpi(label, value):
    return f"<div class='kpi-box'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>"

def insight_box(text):
    title = t['key_finding']
    st.markdown(f"<div class='insight-box'><div class='insight-title'>💡 {title}</div>"
                f"<div class='insight-text'>{text}</div></div>", unsafe_allow_html=True)

def warn_box(text):
    title = t['recommendation']
    st.markdown(f"<div class='warn-box'><div class='warn-title'>🎯 {title}</div>"
                f"<div class='warn-text'>{text}</div></div>", unsafe_allow_html=True)

def dim_bar(label, score, weight):
    color = C['green'] if score >= 70 else C['amber'] if score >= 50 else C['red']
    return f"""<div style='margin-bottom:12px;'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <span style='font-size:13px; font-weight:500; color:{C["gray_700"]};'>{label}</span>
            <span style='font-size:13px; font-weight:700; color:{C["gray_900"]};'>{score}</span>
        </div>
        <div style='font-size:10px; color:{C["gray_400"]}; margin-bottom:4px;'>Weight: {weight}%</div>
        <div class='dim-bar'><div class='dim-bar-fill' style='width:{score}%; background:{color};'></div></div>
    </div>"""


