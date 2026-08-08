
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
    page_title="B2B SEO Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 设计系统（统一色彩）
# ============================================================
COLORS = {
    'primary': '#1a73e8',
    'primary_light': '#e8f0fe',
    'success': '#1e8e3e',
    'success_bg': '#e6f4ea',
    'warning': '#e37400',
    'warning_bg': '#fef7e0',
    'danger': '#d93025',
    'danger_bg': '#fce8e6',
    'text_1': '#202124',
    'text_2': '#5f6368',
    'text_3': '#80868b',
    'border': '#dadce0',
    'bg_page': '#f8f9fa',
    'bg_card': '#ffffff',
    'chart': ['#1a73e8', '#34a853', '#fbbc04', '#ea4335', '#4285f4', '#669df6'],
}

# ============================================================
# 全局 CSS
# ============================================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {COLORS['bg_page']}; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .card {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }}
    .card-title {{
        font-size: 12px; font-weight: 600; color: {COLORS['text_3']};
        text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 12px;
    }}
    .kpi-card {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 16px; text-align: center;
    }}
    .kpi-label {{ font-size: 11px; font-weight: 500; color: {COLORS['text_3']}; text-transform: uppercase; }}
    .kpi-value {{ font-size: 26px; font-weight: 700; color: {COLORS['text_1']}; margin-top: 4px; }}
    .grade-circle {{
        width: 72px; height: 72px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 36px; font-weight: 800;
    }}
    .grade-A {{ background: {COLORS['success_bg']}; color: {COLORS['success']}; }}
    .grade-B {{ background: {COLORS['primary_light']}; color: {COLORS['primary']}; }}
    .grade-C {{ background: {COLORS['warning_bg']}; color: {COLORS['warning']}; }}
    .grade-D {{ background: {COLORS['danger_bg']}; color: {COLORS['danger']}; }}
    .empty-box {{
        text-align: center; padding: 40px 20px;
        border: 2px dashed {COLORS['border']}; border-radius: 12px; margin: 20px 0;
    }}
    .empty-box .e-icon {{ font-size: 40px; margin-bottom: 8px; }}
    .empty-box .e-text {{ font-size: 13px; color: {COLORS['text_3']}; }}
    .priority-P0 {{ background: {COLORS['danger_bg']}; color: {COLORS['danger']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}
    .priority-P1 {{ background: {COLORS['warning_bg']}; color: {COLORS['warning']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}
    .priority-P2 {{ background: {COLORS['primary_light']}; color: {COLORS['primary']}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; display: inline-block; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Plotly 全局模板
# ============================================================
plotly_template = go.layout.Template()
plotly_template.layout = go.Layout(
    font=dict(family="Inter, sans-serif", size=12, color=COLORS['text_2']),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=8, r=8, t=28, b=8),
    colorway=COLORS['chart'],
    xaxis=dict(gridcolor=COLORS['border'], zeroline=False),
    yaxis=dict(gridcolor=COLORS['border'], zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
pio.templates['custom'] = plotly_template
pio.templates.default = 'custom'

# ============================================================
# 多语言
# ============================================================
T = {
    "中文": {
        "brand": "B2B SEO 健康度诊断工具",
        "brand_sub": "基于 Google Search Console 数据 · v2.0",
        "nav_overview": "📊 总览仪表盘",
        "nav_health": "🎯 SEO 健康度评分",
        "nav_trend": "📈 搜索表现趋势",
        "nav_keyword": "🔍 关键词洞察",
        "nav_page": "📄 页面效果分析",
        "nav_country": "🌍 国家/地区分析",
        "nav_device": "📱 设备分布",
        "nav_anomaly": "🚨 流量异常检测",
        "nav_recommend": "🚀 优化建议",
        "total_clicks": "总点击数", "total_impressions": "总展示次数",
        "avg_ctr": "平均点击率", "avg_position": "平均排名",
        "health_score": "健康度评分", "grade": "等级", "score": "分数",
        "search_perf": "搜索表现", "content_eff": "内容效果", "tech_exp": "技术体验",
        "start_date": "开始日期", "end_date": "结束日期",
        "clicks": "点击数", "impressions": "展示次数", "ctr": "点击率", "position": "排名",
        "country": "国家/地区", "device": "设备类型",
        "export_csv": "📥 导出 CSV", "no_data": "暂无数据",
        "no_data_desc": "请检查 data/ 文件夹中是否包含对应的 CSV 文件",
        "sensitivity": "检测灵敏度",
        "select_metric": "选择检测指标",
        "days_analyzed": "检测天数", "anomalies_found": "异常点数", "anomaly_rate": "异常率",
        "normal": "正常", "anomaly": "异常", "rolling_mean": "7日均值",
        "anomaly_events": "异常事件列表", "actual": "实际值", "expected": "期望值",
        "total_keywords": "关键词总数", "kw_with_clicks": "有点击关键词",
        "position_dist": "排名分布", "opportunity_kw": "机会关键词",
        "opportunity_kw_desc": "高展示 + 低CTR + 排名11-30，优化后可快速提升流量",
        "top_keywords": "Top 关键词（按点击量）",
        "total_pages": "总页面数", "pages_with_clicks": "有点击页面", "active_rate": "页面活跃率",
        "page_matrix": "页面机会矩阵",
        "opportunity_pages": "高展示低CTR页面",
        "opportunity_pages_desc": "展示量高但点击率低，优化标题/描述可快速提升",
        "top_pages": "Top 页面（按点击量）",
        "countries_covered": "覆盖国家数", "top_countries": "Top 国家/地区",
        "geo_map": "全球流量分布地图", "detail_data": "详细数据",
        "imp_share": "展示占比", "click_share": "点击占比",
        "device_compare": "设备对比", "device_trend": "设备月度趋势",
        "monthly_summary": "月度汇总",
        "scoring_method": "评分方法说明",
        "backlink_reserved": "外链权威（待接入）",
        "backlink_desc": "外链权威维度已预留接口，待接入 Ahrefs/Moz API 后启用。届时权重调整为：搜索表现35% + 内容效果30% + 技术体验20% + 外链权威15%",
        "data_missing_warn": "⚠️ 部分数据源缺失，评分可能不完整",
        "rec_title": "SEO 优化建议",
    },
    "English": {
        "brand": "B2B SEO Health Diagnostic Tool",
        "brand_sub": "Based on Google Search Console Data · v2.0",
        "nav_overview": "📊 Overview Dashboard",
        "nav_health": "🎯 SEO Health Score",
        "nav_trend": "📈 Search Trends",
        "nav_keyword": "🔍 Keyword Insights",
        "nav_page": "📄 Page Performance",
        "nav_country": "🌍 Country/Region",
        "nav_device": "📱 Device Distribution",
        "nav_anomaly": "🚨 Anomaly Detection",
        "nav_recommend": "🚀 Recommendations",
        "total_clicks": "Total Clicks", "total_impressions": "Total Impressions",
        "avg_ctr": "Average CTR", "avg_position": "Average Position",
        "health_score": "Health Score", "grade": "Grade", "score": "Score",
        "search_perf": "Search Performance", "content_eff": "Content Effectiveness", "tech_exp": "Technical Experience",
        "start_date": "Start Date", "end_date": "End Date",
        "clicks": "Clicks", "impressions": "Impressions", "ctr": "CTR", "position": "Position",
        "country": "Country/Region", "device": "Device",
        "export_csv": "📥 Export CSV", "no_data": "No Data",
        "no_data_desc": "Please check if CSV files exist in the data/ folder",
        "sensitivity": "Detection Sensitivity",
        "select_metric": "Select Metric",
        "days_analyzed": "Days Analyzed", "anomalies_found": "Anomalies Found", "anomaly_rate": "Anomaly Rate",
        "normal": "Normal", "anomaly": "Anomaly", "rolling_mean": "7-day Mean",
        "anomaly_events": "Anomaly Events", "actual": "Actual", "expected": "Expected",
        "total_keywords": "Total Keywords", "kw_with_clicks": "Keywords with Clicks",
        "position_dist": "Position Distribution", "opportunity_kw": "Opportunity Keywords",
        "opportunity_kw_desc": "High impressions + Low CTR + Position 11-30, quick wins",
        "top_keywords": "Top Keywords (by Clicks)",
        "total_pages": "Total Pages", "pages_with_clicks": "Pages with Clicks", "active_rate": "Active Rate",
        "page_matrix": "Page Opportunity Matrix",
        "opportunity_pages": "High Impression Low CTR Pages",
        "opportunity_pages_desc": "High impressions but low CTR, optimize title/description",
        "top_pages": "Top Pages (by Clicks)",
        "countries_covered": "Countries Covered", "top_countries": "Top Countries/Regions",
        "geo_map": "Global Traffic Distribution Map", "detail_data": "Detailed Data",
        "imp_share": "Impression Share", "click_share": "Click Share",
        "device_compare": "Device Comparison", "device_trend": "Device Monthly Trend",
        "monthly_summary": "Monthly Summary",
        "scoring_method": "Scoring Methodology",
        "backlink_reserved": "Backlink Authority (Coming Soon)",
        "backlink_desc": "Backlink authority reserved. Once Ahrefs/Moz API integrated, weights: Search 35% + Content 30% + Technical 20% + Backlinks 15%",
        "data_missing_warn": "⚠️ Some data sources missing, score may be incomplete",
        "rec_title": "SEO Optimization Recommendations",
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
# SEO 健康度评分（三维加权 V2.0）
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
    scores['grade_cn'] = {'A': '优秀', 'B': '良好', 'C': '一般', 'D': '较差'}[scores['grade']]
    scores['grade_en'] = {'A': 'Excellent', 'B': 'Good', 'C': 'Average', 'D': 'Poor'}[scores['grade']]
    scores['missing'] = missing
    return scores

health = calculate_health_score(data)

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:8px 0 12px;'>"
                f"<div style='font-size:20px;'>📊</div>"
                f"<div style='font-size:13px; font-weight:700; color:{COLORS['text_1']};'>B2B SEO Health</div>"
                f"<div style='font-size:10px; color:{COLORS['text_3']};'>Diagnostic Tool v2.0</div>"
                f"</div>", unsafe_allow_html=True)
    st.markdown("---")

    lang = st.selectbox("🌐", list(T.keys()), label_visibility="collapsed")
    t = T[lang]

    st.markdown(f"<p style='font-size:10px; font-weight:700; color:{COLORS['text_3']}; letter-spacing:1px;'>NAVIGATION</p>", unsafe_allow_html=True)
    nav_list = [t['nav_overview'], t['nav_health'], t['nav_trend'], t['nav_keyword'],
                t['nav_page'], t['nav_country'], t['nav_device'], t['nav_anomaly'], t['nav_recommend']]
    page = st.radio("nav", nav_list, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"<p style='font-size:10px; font-weight:700; color:{COLORS['text_3']}; letter-spacing:1px;'>📅 DATA FILTER</p>", unsafe_allow_html=True)
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
def empty_state(icon="📭", msg=""):
    st.markdown(f"<div class='empty-box'><div class='e-icon'>{icon}</div>"
                f"<div class='e-text'>{msg or t['no_data_desc']}</div></div>", unsafe_allow_html=True)

def date_filter(df, s, e):
    if s and e and 'data_date' in df.columns:
        return df[(df['data_date'].dt.date >= s) & (df['data_date'].dt.date <= e)]
    return df

def csv_export(df, name):
    st.download_button(t['export_csv'], df.to_csv(index=False).encode('utf-8-sig'), name, 'text/csv')

def kpi_html(label, value):
    return f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>"

# ============================================================
# 品牌头部
# ============================================================
st.markdown(f"<div style='background:{COLORS['bg_card']}; border-bottom:1px solid {COLORS['border']}; "
            f"padding:12px 24px; margin:-1rem -1rem 20px -1rem; display:flex; align-items:center; gap:12px;'>"
            f"<div style='font-size:22px;'>📊</div>"
            f"<div><div style='font-size:15px; font-weight:600; color:{COLORS['text_1']};'>{t['brand']}</div>"
            f"<div style='font-size:11px; color:{COLORS['text_3']};'>{t['brand_sub']}</div></div>"
            f"</div>", unsafe_allow_html=True)


# ============================================================
# 页面1：总览仪表盘
# ============================================================
if page == t['nav_overview']:
    if data.get('daily_summary') is not None:
        df = date_filter(data['daily_summary'].copy(), g_start, g_end)
        tc = int(df['clicks'].sum())
        ti = int(df['impressions'].sum())
        ac = df['ctr'].mean() * 100
        ap = df['position'].mean()

        cols = st.columns(4)
        for col, (lb, val) in zip(cols, [(t['total_clicks'], f"{tc:,}"), (t['total_impressions'], f"{ti:,}"),
                                          (t['avg_ctr'], f"{ac:.2f}%"), (t['avg_position'], f"{ap:.1f}")]):
            col.markdown(kpi_html(lb, val), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 2])
        with col_a:
            g = health['grade']
            st.markdown(f"<div class='card' style='text-align:center;'>"
                        f"<div class='card-title'>{t['health_score']}</div>"
                        f"<div class='grade-circle grade-{g}'>{g}</div>"
                        f"<div style='font-size:12px; color:{COLORS['text_3']}; margin-top:8px;'>"
                        f"{health['grade_cn'] if lang == '中文' else health['grade_en']}</div>"
                        f"<div style='font-size:28px; font-weight:700; margin-top:4px;'>{health['total']} / 100</div>"
                        f"</div>", unsafe_allow_html=True)
        with col_b:
            cats = [t['search_perf'], t['content_eff'], t['tech_exp']]
            vals = [health['search'], health['content'], health['tech']]
            fig = go.Figure(data=go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill='toself', fillcolor='rgba(26,115,232,0.12)',
                line=dict(color=COLORS['primary'], width=2)
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                              showlegend=False, height=280, margin=dict(l=40, r=40, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        if health['missing']:
            st.warning(t['data_missing_warn'])
    else:
        empty_state("📊", t['no_data_desc'])

# ============================================================
# 页面2：SEO 健康度评分
# ============================================================
elif page == t['nav_health']:
    g = health['grade']
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.markdown(f"<div class='card' style='text-align:center;'>"
                    f"<div class='card-title'>{t['grade']}</div>"
                    f"<div class='grade-circle grade-{g}'>{g}</div>"
                    f"<div style='margin-top:8px; font-size:12px; color:{COLORS['text_3']};'>"
                    f"{health['grade_cn'] if lang == '中文' else health['grade_en']}</div>"
                    f"</div>", unsafe_allow_html=True)
    with col2:
        color = {'A': COLORS['success'], 'B': COLORS['primary'], 'C': COLORS['warning'], 'D': COLORS['danger']}[g]
        st.markdown(f"<div class='card' style='text-align:center;'>"
                    f"<div class='card-title'>{t['score']}</div>"
                    f"<div style='font-size:42px; font-weight:700; color:{color};'>{health['total']}</div>"
                    f"<div style='font-size:12px; color:{COLORS['text_3']};'>/ 100</div>"
                    f"</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card'>"
                    f"<div class='card-title'>DIMENSION BREAKDOWN</div>"
                    f"<p><strong>{t['search_perf']} (40%)</strong>: {health['search']} / 100</p>"
                    f"<p><strong>{t['content_eff']} (35%)</strong>: {health['content']} / 100</p>"
                    f"<p><strong>{t['tech_exp']} (25%)</strong>: {health['tech']} / 100</p>"
                    f"</div>", unsafe_allow_html=True)

    cats = [t['search_perf'], t['content_eff'], t['tech_exp']]
    vals = [health['search'], health['content'], health['tech']]
    fig = go.Figure(data=go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill='toself', fillcolor='rgba(26,115,232,0.12)',
        line=dict(color=COLORS['primary'], width=2)
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=320)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"📖 {t['scoring_method']}", expanded=False):
        st.markdown("""
| 维度 | 权重 | 二级指标 | 评分逻辑 |
|---|---|---|---|
| 搜索表现 Search | 40% | CTR, Position, Click Trend | B2B CTR 2-3%=Good; Top10=Full |
| 内容效果 Content | 35% | Keyword Coverage, Page Active Rate, Geo Coverage | 500+ keywords=Excellent |
| 技术体验 Technical | 25% | Device Coverage, Mobile Ratio, Data Continuity | 3 devices=Full; B2B mobile 15-35% |

**Grade**: A(90-100) · B(70-89) · C(50-69) · D(0-49)
        """)
    with st.expander(f"🔗 {t['backlink_reserved']}", expanded=False):
        st.info(t['backlink_desc'])

# ============================================================
# 页面3：搜索表现趋势
# ============================================================
elif page == t['nav_trend']:
    if data.get('daily_summary') is not None:
        df = date_filter(data['daily_summary'].copy().sort_values('data_date'), g_start, g_end)
        if len(df) > 0:
            # 点击 & 展示双轴图
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=df['data_date'], y=df['impressions'], name=t['impressions'],
                                 marker_color=COLORS['chart'][4], opacity=0.6), secondary_y=False)
            fig.add_trace(go.Scatter(x=df['data_date'], y=df['clicks'], name=t['clicks'],
                                     line=dict(color=COLORS['primary'], width=2), mode='lines'), secondary_y=True)
            fig.update_yaxes(title_text=t['impressions'], secondary_y=False)
            fig.update_yaxes(title_text=t['clicks'], secondary_y=True)
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                fig2 = px.line(df, x='data_date', y='ctr')
                fig2.update_traces(line_color=COLORS['success'], line_width=2)
                fig2.update_layout(height=220, title=t['ctr'], yaxis_tickformat='.2%')
                st.plotly_chart(fig2, use_container_width=True)
            with col_b:
                fig3 = px.line(df, x='data_date', y='position')
                fig3.update_traces(line_color=COLORS['warning'], line_width=2)
                fig3.update_yaxes(autorange="reversed")
                fig3.update_layout(height=220, title=t['position'])
                st.plotly_chart(fig3, use_container_width=True)

            # 月度汇总
            df['month'] = df['data_date'].dt.to_period('M').astype(str)
            monthly = df.groupby('month').agg({'clicks': 'sum', 'impressions': 'sum'}).reset_index()
            st.markdown(f"<div class='card-title'>{t['monthly_summary']}</div>", unsafe_allow_html=True)
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(x=monthly['month'], y=monthly['clicks'], name=t['clicks'],
                                  marker_color=COLORS['primary'], text=monthly['clicks'], textposition='outside'))
            fig4.update_layout(height=260)
            st.plotly_chart(fig4, use_container_width=True)

            csv_export(df[['data_date', 'clicks', 'impressions', 'ctr', 'position']], "search_trend.csv")
        else:
            empty_state("📈", t['no_data'])
    else:
        empty_state("📈", t['no_data_desc'])

# ============================================================
# 页面4：关键词洞察
# ============================================================
elif page == t['nav_keyword']:
    if data.get('by_query') is not None:
        df_q = date_filter(data['by_query'].copy(), g_start, g_end)
        tk = df_q['query'].nunique()
        kc = df_q[df_q['clicks'] > 0]['query'].nunique()
        ap = df_q['position'].mean()

        cols = st.columns(3)
        cols[0].markdown(kpi_html(t['total_keywords'], f"{tk:,}"), unsafe_allow_html=True)
        cols[1].markdown(kpi_html(t['kw_with_clicks'], f"{kc:,}"), unsafe_allow_html=True)
        cols[2].markdown(kpi_html(t['avg_position'], f"{ap:.1f}"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 排名分布
        st.markdown(f"<div class='card-title'>{t['position_dist']}</div>", unsafe_allow_html=True)
        df_q['bucket'] = pd.cut(df_q['position'], bins=[0, 3, 10, 20, 50, 100],
                                labels=['Top 3', '4-10', '11-20', '21-50', '50+'])
        pd_dist = df_q['bucket'].value_counts().sort_index().reset_index()
        pd_dist.columns = ['Range', 'Count']
        fig = px.bar(pd_dist, x='Range', y='Count', color_discrete_sequence=[COLORS['primary']], text='Count')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=240, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        # 机会关键词
        st.markdown(f"<div class='card-title'>🎯 {t['opportunity_kw']}</div>"
                    f"<p style='font-size:11px; color:{COLORS['text_3']};'>{t['opportunity_kw_desc']}</p>",
                    unsafe_allow_html=True)
        kw_agg = df_q.groupby('query').agg({'clicks': 'sum', 'impressions': 'sum', 'position': 'mean'}).reset_index()
        kw_agg['ctr'] = kw_agg['clicks'] / kw_agg['impressions'].replace(0, 1)
        opp = kw_agg[(kw_agg['impressions'] >= 10) & (kw_agg['ctr'] < 0.02) &
                     (kw_agg['position'] >= 11) & (kw_agg['position'] <= 30)].sort_values('impressions', ascending=False).head(20)
        if len(opp) > 0:
            opp_d = opp.copy()
            opp_d['ctr'] = (opp_d['ctr'] * 100).round(2)
            opp_d['position'] = opp_d['position'].round(1)
            st.dataframe(opp_d[['query', 'clicks', 'impressions', 'ctr', 'position']].rename(
                columns={'query': 'Keyword', 'clicks': t['clicks'], 'impressions': t['impressions'],
                         'ctr': 'CTR%', 'position': t['position']}
            ), use_container_width=True, hide_index=True, height=300)
            csv_export(opp_d, "opportunity_keywords.csv")
        else:
            st.info("未发现机会关键词" if lang == "中文" else "No opportunity keywords found")

        # Top 关键词
        st.markdown(f"<div class='card-title'>🏆 {t['top_keywords']}</div>", unsafe_allow_html=True)
        top_kw = kw_agg.sort_values('clicks', ascending=False).head(20)
        top_kw['ctr'] = (top_kw['ctr'] * 100).round(2)
        top_kw['position'] = top_kw['position'].round(1)
        st.dataframe(top_kw[['query', 'clicks', 'impressions', 'ctr', 'position']].rename(
            columns={'query': 'Keyword', 'clicks': t['clicks'], 'impressions': t['impressions'],
                     'ctr': 'CTR%', 'position': t['position']}
        ), use_container_width=True, hide_index=True, height=300)
        csv_export(top_kw, "top_keywords.csv")
    else:
        empty_state("🔍", t['no_data_desc'])

# ============================================================
# 页面5：页面效果分析
# ============================================================
elif page == t['nav_page']:
    if data.get('by_page') is not None:
        df_p = date_filter(data['by_page'].copy(), g_start, g_end)
        tp = df_p['page'].nunique()
        pc = df_p[df_p['clicks'] > 0]['page'].nunique()
        ar = pc / tp * 100 if tp > 0 else 0

        cols = st.columns(3)
        cols[0].markdown(kpi_html(t['total_pages'], f"{tp:,}"), unsafe_allow_html=True)
        cols[1].markdown(kpi_html(t['pages_with_clicks'], f"{pc:,}"), unsafe_allow_html=True)
        cols[2].markdown(kpi_html(t['active_rate'], f"{ar:.1f}%"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 机会矩阵散点图
        st.markdown(f"<div class='card-title'>📊 {t['page_matrix']}</div>", unsafe_allow_html=True)
        pg_agg = df_p.groupby('page').agg({'clicks': 'sum', 'impressions': 'sum', 'position': 'mean'}).reset_index()
        pg_agg['ctr'] = pg_agg['clicks'] / pg_agg['impressions'].replace(0, 1)
        pg_m = pg_agg[pg_agg['impressions'] >= 5].copy()
        if len(pg_m) > 0:
            fig = px.scatter(pg_m, x='impressions', y='clicks', color='position',
                             hover_data=['page'], color_continuous_scale='Blues_r',
                             labels={'impressions': t['impressions'], 'clicks': t['clicks'], 'position': t['position']})
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True)

        # 高展示低CTR页面
        st.markdown(f"<div class='card-title'>🎯 {t['opportunity_pages']}</div>"
                    f"<p style='font-size:11px; color:{COLORS['text_3']};'>{t['opportunity_pages_desc']}</p>",
                    unsafe_allow_html=True)
        opp_p = pg_agg[(pg_agg['impressions'] >= 20) & (pg_agg['ctr'] < 0.01)].sort_values('impressions', ascending=False).head(15)
        if len(opp_p) > 0:
            opp_pd = opp_p.copy()
            opp_pd['ctr'] = (opp_pd['ctr'] * 100).round(2)
            opp_pd['position'] = opp_pd['position'].round(1)
            opp_pd['page'] = opp_pd['page'].str.replace('https://www.advich.com', '', regex=False)
            st.dataframe(opp_pd[['page', 'clicks', 'impressions', 'ctr', 'position']].rename(
                columns={'page': 'Page', 'clicks': t['clicks'], 'impressions': t['impressions'],
                         'ctr': 'CTR%', 'position': t['position']}
            ), use_container_width=True, hide_index=True, height=280)
            csv_export(opp_pd, "opportunity_pages.csv")
        else:
            st.info("未发现机会页面" if lang == "中文" else "No opportunity pages found")

        # Top 页面
        st.markdown(f"<div class='card-title'>🏆 {t['top_pages']}</div>", unsafe_allow_html=True)
        top_p = pg_agg.sort_values('clicks', ascending=False).head(15)
        top_p['ctr'] = (top_p['ctr'] * 100).round(2)
        top_p['position'] = top_p['position'].round(1)
        top_p['page'] = top_p['page'].str.replace('https://www.advich.com', '', regex=False)
        st.dataframe(top_p[['page', 'clicks', 'impressions', 'ctr', 'position']].rename(
            columns={'page': 'Page', 'clicks': t['clicks'], 'impressions': t['impressions'],
                     'ctr': 'CTR%', 'position': t['position']}
        ), use_container_width=True, hide_index=True, height=280)
        csv_export(top_p, "top_pages.csv")
    else:
        empty_state("📄", t['no_data_desc'])

# ============================================================
# 页面6：国家/地区分析（含世界地图）
# ============================================================
elif page == t['nav_country']:
    if data.get('by_country') is not None:
        df_c = date_filter(data['by_country'].copy(), g_start, g_end)
        total_countries = df_c['country'].nunique()

        st.markdown(kpi_html(t['countries_covered'], str(total_countries)), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 按国家聚合
        c_agg = df_c.groupby('country').agg({'clicks': 'sum', 'impressions': 'sum', 'position': 'mean'}).reset_index()
        c_agg['ctr'] = c_agg['clicks'] / c_agg['impressions'].replace(0, 1)
        c_agg = c_agg.sort_values('clicks', ascending=False)

        # 🌍 世界地图
        st.markdown(f"<div class='card-title'>🌍 {t['geo_map']}</div>", unsafe_allow_html=True)
        fig_map = px.choropleth(
            c_agg,
            locations='country',
            locationmode='ISO-3',
            color='clicks',
            hover_name='country',
            hover_data={'impressions': True, 'clicks': True},
            color_continuous_scale=[
                [0, '#e8f0fe'], [0.25, '#aecbfa'], [0.5, '#669df6'],
                [0.75, '#1a73e8'], [1, '#174ea6']
            ],
            labels={'clicks': t['clicks'], 'impressions': t['impressions']},
        )
        fig_map.update_geos(
            showcoastlines=True, coastlinecolor=COLORS['border'],
            showland=True, landcolor='#f8f9fa',
            showocean=True, oceancolor='#ffffff',
            showframe=False, projection_type='natural earth'
        )
        fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0),
                              coloraxis_colorbar=dict(title=t['clicks'], thickness=12, len=0.6))
        st.plotly_chart(fig_map, use_container_width=True)

        # Top 国家柱状图
        st.markdown(f"<div class='card-title'>🏆 {t['top_countries']} (Top 15)</div>", unsafe_allow_html=True)
        top_c = c_agg.head(15)
        fig_bar = px.bar(top_c, x='country', y='clicks', text='clicks',
                         color_discrete_sequence=[COLORS['primary']],
                         labels={'country': t['country'], 'clicks': t['clicks']})
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(height=300, xaxis_title="", yaxis_title=t['clicks'])
        st.plotly_chart(fig_bar, use_container_width=True)

        # 详细表格
        st.markdown(f"<div class='card-title'>📋 {t['detail_data']}</div>", unsafe_allow_html=True)
        c_display = c_agg.head(30).copy()
        c_display['ctr'] = (c_display['ctr'] * 100).round(2)
        c_display['position'] = c_display['position'].round(1)
        st.dataframe(c_display[['country', 'clicks', 'impressions', 'ctr', 'position']].rename(
            columns={'country': t['country'], 'clicks': t['clicks'], 'impressions': t['impressions'],
                     'ctr': 'CTR%', 'position': t['position']}
        ), use_container_width=True, hide_index=True, height=350)
        csv_export(c_display, "country_analysis.csv")
    else:
        empty_state("🌍", t['no_data_desc'])

# ============================================================
# 页面7：设备分布
# ============================================================
elif page == t['nav_device']:
    if data.get('by_device') is not None:
        df_d = date_filter(data['by_device'].copy(), g_start, g_end)
        d_agg = df_d.groupby('device').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card-title'>{t['imp_share']}</div>", unsafe_allow_html=True)
            fig1 = px.pie(d_agg, values='impressions', names='device', color_discrete_sequence=COLORS['chart'][:3])
            fig1.update_traces(textinfo='label+percent', textfont_size=12)
            fig1.update_layout(height=260, showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.markdown(f"<div class='card-title'>{t['click_share']}</div>", unsafe_allow_html=True)
            fig2 = px.pie(d_agg, values='clicks', names='device', color_discrete_sequence=COLORS['chart'][:3])
            fig2.update_traces(textinfo='label+percent', textfont_size=12)
            fig2.update_layout(height=260, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # 设备对比表
        st.markdown(f"<div class='card-title'>📋 {t['device_compare']}</div>", unsafe_allow_html=True)
        d_show = d_agg.copy()
        d_show['ctr'] = (d_show['ctr'] * 100).round(2)
        d_show['position'] = d_show['position'].round(1)
        st.dataframe(d_show[['device', 'clicks', 'impressions', 'ctr', 'position']].rename(
            columns={'device': t['device'], 'clicks': t['clicks'], 'impressions': t['impressions'],
                     'ctr': 'CTR%', 'position': t['position']}
        ), use_container_width=True, hide_index=True)

        # 月度趋势
        if 'data_date' in df_d.columns:
            st.markdown(f"<div class='card-title'>📈 {t['device_trend']}</div>", unsafe_allow_html=True)
            df_d['month'] = df_d['data_date'].dt.to_period('M').astype(str)
            dm = df_d.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
            fig3 = px.line(dm, x='month', y='clicks', color='device', markers=True,
                           color_discrete_sequence=COLORS['chart'][:3],
                           labels={'month': '', 'clicks': t['clicks'], 'device': t['device']})
            fig3.update_layout(height=260)
            st.plotly_chart(fig3, use_container_width=True)

        csv_export(d_show, "device_distribution.csv")
    else:
        empty_state("📱", t['no_data_desc'])

# ============================================================
# 页面8：流量异常检测
# ============================================================
elif page == t['nav_anomaly']:
    if data.get('daily_summary') is not None:
        df = date_filter(data['daily_summary'].copy().sort_values('data_date'), g_start, g_end)

        if len(df) < 7:
            empty_state("🚨", "数据不足7天，无法进行异常检测" if lang == "中文" else "Need at least 7 days of data")
        else:
            col1, col2 = st.columns(2)
            with col1:
                m_opts = {t['clicks']: 'clicks', t['impressions']: 'impressions', 'CTR': 'ctr', t['position']: 'position'}
                sel_l = st.selectbox(t['select_metric'], list(m_opts.keys()))
                sel_m = m_opts[sel_l]
            with col2:
                sens = st.slider(t['sensitivity'], 1.0, 3.0, 2.0, 0.1)

            # Z-Score 检测
            df['rolling_mean'] = df[sel_m].rolling(window=7, min_periods=1).mean()
            df['rolling_std'] = df[sel_m].rolling(window=7, min_periods=1).std().fillna(0)
            df['z_score'] = ((df[sel_m] - df['rolling_mean']) / df['rolling_std'].replace(0, 1)).abs()
            df['is_anomaly'] = df['z_score'] > sens

            anomalies = df[df['is_anomaly']]
            total_days = len(df)
            n_anomalies = len(anomalies)
            rate = n_anomalies / total_days * 100

            cols = st.columns(3)
            cols[0].markdown(kpi_html(t['days_analyzed'], str(total_days)), unsafe_allow_html=True)
            cols[1].markdown(kpi_html(t['anomalies_found'], str(n_anomalies)), unsafe_allow_html=True)
            cols[2].markdown(kpi_html(t['anomaly_rate'], f"{rate:.1f}%"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # 趋势图 + 异常标注
            fig = go.Figure()
            normal = df[~df['is_anomaly']]
            fig.add_trace(go.Scatter(x=normal['data_date'], y=normal[sel_m], mode='lines',
                                     name=t['normal'], line=dict(color=COLORS['primary'], width=1.5)))
            fig.add_trace(go.Scatter(x=df['data_date'], y=df['rolling_mean'], mode='lines',
                                     name=t['rolling_mean'], line=dict(color=COLORS['text_3'], width=1, dash='dash')))
            if n_anomalies > 0:
                fig.add_trace(go.Scatter(x=anomalies['data_date'], y=anomalies[sel_m], mode='markers',
                                         name=t['anomaly'], marker=dict(color=COLORS['danger'], size=10, symbol='x')))
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True)

            # 异常事件列表
            if n_anomalies > 0:
                st.markdown(f"<div class='card-title'>📋 {t['anomaly_events']}</div>", unsafe_allow_html=True)
                anom_display = anomalies[['data_date', sel_m, 'rolling_mean', 'z_score']].copy()
                anom_display.columns = ['Date', t['actual'], t['expected'], 'Z-Score']
                anom_display['Z-Score'] = anom_display['Z-Score'].round(2)
                anom_display[t['actual']] = anom_display[t['actual']].round(4)
                anom_display[t['expected']] = anom_display[t['expected']].round(4)
                st.dataframe(anom_display, use_container_width=True, hide_index=True, height=250)
                csv_export(anom_display, "anomaly_events.csv")
    else:
        empty_state("🚨", t['no_data_desc'])

# ============================================================
# 页面9：优化建议
# ============================================================
elif page == t['nav_recommend']:
    st.markdown(f"<div class='card-title'>🚀 {t['rec_title']}</div>", unsafe_allow_html=True)

    recommendations = []

    # 基于评分自动生成建议
    if health['search'] < 70:
        recommendations.append({
            'priority': 'P0',
            'issue_cn': '平均排名偏低（23.8），大量关键词未进入首页',
            'issue_en': 'Average position too low (23.8), most keywords not on page 1',
            'action_cn': '聚焦排名11-20的关键词，优化内容深度和内链结构，争取进入Top 10',
            'action_en': 'Focus on keywords ranked 11-20, improve content depth and internal linking to reach Top 10',
        })

    if health.get('search', 100) < 80:
        recommendations.append({
            'priority': 'P0',
            'issue_cn': 'CTR偏低（1.46%），搜索结果吸引力不足',
            'issue_en': 'CTR too low (1.46%), search results not attractive enough',
            'action_cn': '优化Title和Meta Description，加入数字、年份、行动号召词，提升点击欲望',
            'action_en': 'Optimize Title and Meta Description, add numbers, year, CTA words',
        })

    if health.get('content', 100) < 80:
        recommendations.append({
            'priority': 'P1',
            'issue_cn': '页面活跃率偏低，大量页面无点击',
            'issue_en': 'Low page active rate, many pages with zero clicks',
            'action_cn': '审查零点击页面，合并低质量内容，优化或删除无效页面',
            'action_en': 'Audit zero-click pages, consolidate thin content, optimize or remove ineffective pages',
        })

    if health.get('tech', 100) < 80:
        recommendations.append({
            'priority': 'P1',
            'issue_cn': '移动端占比需关注，确保移动体验良好',
            'issue_en': 'Mobile ratio needs attention, ensure good mobile experience',
            'action_cn': '检查移动端页面加载速度和Core Web Vitals，确保响应式设计正常',
            'action_en': 'Check mobile page speed and Core Web Vitals, ensure responsive design works',
        })

    # 通用建议
    recommendations.append({
        'priority': 'P2',
        'issue_cn': '缺少外链权威数据，无法评估站外SEO',
        'issue_en': 'No backlink authority data, cannot assess off-site SEO',
        'action_cn': '建议接入 Ahrefs 或 Moz API，补充外链维度评估',
        'action_en': 'Recommend integrating Ahrefs or Moz API for backlink assessment',
    })

    recommendations.append({
        'priority': 'P2',
        'issue_cn': '点击量近期呈下降趋势',
        'issue_en': 'Click volume showing declining trend recently',
        'action_cn': '分析流量下降的具体页面和关键词，检查是否有算法更新影响或竞争对手变化',
        'action_en': 'Analyze specific pages/keywords with declining traffic, check for algorithm updates or competitor changes',
    })

    # 显示建议
    if recommendations:
        for i, rec in enumerate(recommendations):
            issue = rec['issue_cn'] if lang == '中文' else rec['issue_en']
            action = rec['action_cn'] if lang == '中文' else rec['action_en']
            p = rec['priority']

            st.markdown(f"""<div class='card'>
                <div style='display:flex; align-items:center; gap:8px; margin-bottom:8px;'>
                    <span class='priority-{p}'>{p}</span>
                    <strong style='color:{COLORS["text_1"]};'>{issue}</strong>
                </div>
                <p style='font-size:13px; color:{COLORS["text_2"]}; margin:0; padding-left:40px;'>
                    💡 {action}
                </p>
            </div>""", unsafe_allow_html=True)

    # 评分提升路径
    st.markdown("---")
    st.markdown(f"<div class='card-title'>📈 {'评分提升路径' if lang == '中文' else 'Score Improvement Path'}</div>",
                unsafe_allow_html=True)
    improve_data = {
        'Action': [
            'Optimize Top 11-20 keywords to Top 10' if lang == 'English' else '优化排名11-20的关键词进入Top 10',
            'Improve CTR from 1.46% to 2.5%' if lang == 'English' else '提升CTR从1.46%到2.5%',
            'Activate zero-click pages' if lang == 'English' else '激活零点击页面',
            'Integrate backlink data' if lang == 'English' else '接入外链数据',
        ],
        'Impact': ['+8~12 pts', '+5~8 pts', '+3~5 pts', '+5~10 pts'],
        'Effort': ['High', 'Medium', 'Medium', 'Low'],
        'Timeline': ['2-3 months', '1-2 months', '1 month', '1 week'],
    }
    st.dataframe(pd.DataFrame(improve_data), use_container_width=True, hide_index=True)

