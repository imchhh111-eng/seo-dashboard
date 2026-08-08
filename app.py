
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
# 设计系统（SaaS 风格，统一蓝色主色调）
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
# 全局 CSS
# ============================================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {C['gray_50']}; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .card {{
        background: {C['white']}; border: 1px solid {C['gray_200']};
        border-radius: 16px; padding: 24px; margin-bottom: 16px;
    }}
    .card-title {{
        font-size: 11px; font-weight: 700; color: {C['gray_400']};
        text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;
    }}
    .kpi-box {{
        background: {C['white']}; border: 1px solid {C['gray_200']};
        border-radius: 12px; padding: 16px 12px; text-align: center;
    }}
    .kpi-label {{ font-size: 11px; font-weight: 500; color: {C['gray_500']}; }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: {C['gray_900']}; margin-top: 2px; }}
    .score-ring {{
        width: 100px; height: 100px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 32px; font-weight: 800; border: 4px solid;
    }}
    .score-A {{ border-color: {C['green']}; color: {C['green']}; background: {C['green_bg']}; }}
    .score-B {{ border-color: {C['blue']}; color: {C['blue']}; background: {C['blue_light']}; }}
    .score-C {{ border-color: {C['amber']}; color: {C['amber']}; background: {C['amber_bg']}; }}
    .score-D {{ border-color: {C['red']}; color: {C['red']}; background: {C['red_bg']}; }}
    .insight-box {{
        background: {C['blue_light']}; border-left: 3px solid {C['blue']};
        border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 12px 0;
    }}
    .insight-box .insight-title {{
        font-size: 11px; font-weight: 700; color: {C['blue']};
        text-transform: uppercase; margin-bottom: 4px;
    }}
    .insight-box .insight-text {{ font-size: 13px; color: {C['gray_700']}; line-height: 1.5; }}
    .warn-box {{
        background: {C['amber_bg']}; border-left: 3px solid {C['amber']};
        border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 12px 0;
    }}
    .warn-box .warn-title {{
        font-size: 11px; font-weight: 700; color: {C['amber']};
        text-transform: uppercase; margin-bottom: 4px;
    }}
    .warn-box .warn-text {{ font-size: 13px; color: {C['gray_700']}; }}
    .dim-bar {{
        height: 8px; border-radius: 4px; background: {C['gray_100']};
        overflow: hidden; margin-top: 4px;
    }}
    .dim-bar-fill {{ height: 100%; border-radius: 4px; }}
    .nav-group {{
        font-size: 10px; font-weight: 700; color: {C['gray_400']};
        text-transform: uppercase; letter-spacing: 1px; margin: 16px 0 6px 0;
    }}
    .empty-state {{
        text-align: center; padding: 48px 24px;
        border: 2px dashed {C['gray_200']}; border-radius: 16px; margin: 24px 0;
    }}
    .empty-state .icon {{ font-size: 48px; margin-bottom: 12px; }}
    .empty-state .msg {{ font-size: 13px; color: {C['gray_500']}; }}
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
        "device_trend": "月度趋势", "monthly_summary": "月度汇总",
        "scoring_method": "评分方法",
        "backlink_reserved": "外链权威（待接入）",
        "backlink_desc": "外链权威维度已预留，待接入 Ahrefs/Moz API 后启用。届时权重：搜索35% + 内容30% + 技术20% + 外链15%",
        "key_finding": "关键发现", "recommendation": "建议行动",
        "main_opportunity": "核心机会", "strength": "优势", "weakness": "短板",
        "exec_summary": "AI 诊断摘要", "model_arch": "模型架构",
        "rec_title": "优化建议",
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
        "device_trend": "Monthly Trend", "monthly_summary": "Monthly Summary",
        "scoring_method": "Methodology",
        "backlink_reserved": "Backlink Authority (Coming Soon)",
        "backlink_desc": "Backlink authority reserved. Once Ahrefs/Moz integrated: Search 35% + Content 30% + Technical 20% + Backlinks 15%",
        "key_finding": "Key Finding", "recommendation": "Recommendation",
        "main_opportunity": "Main Opportunity", "strength": "Strength", "weakness": "Weakness",
        "exec_summary": "AI Diagnostic Summary", "model_arch": "Model Architecture",
        "rec_title": "Recommendations",
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

    if data.get('by_page') is not None:
        dp = data['by_page']
        tp = dp['page'].nunique()
        ap = dp[dp['clicks'] > 0]['page'].nunique()
        c_scores.append(min(100, (ap / tp * 100 * 2)) if tp > 0 else 0)

    if data.get('by_country') is not None:
        uc = data['by_country']['country'].nunique()
        c_scores.append(min(100, (uc / 50) * 100))
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

    if data.get('by_date') is not None:
        dfd = data['by_date']
        td = (dfd['data_date'].max() - dfd['data_date'].min()).days
        ad = dfd['data_date'].nunique()
        t_scores.append(min(100, (ad / td * 100)) if td > 0 else 50)
    scores['tech'] = round(np.mean(t_scores), 1) if t_scores else 0

    total = scores['search'] * 0.40 + scores['content'] * 0.35 + scores['tech'] * 0.25
    scores['total'] = round(total, 1)
    scores['grade'] = 'A' if total >= 90 else 'B' if total >= 70 else 'C' if total >= 50 else 'D'
    scores['grade_cn'] = {'A': '优秀', 'B': '良好', 'C': '一般', 'D': '较差'}[scores['grade']]
    scores['grade_en'] = {'A': 'Excellent', 'B': 'Good', 'C': 'Moderate', 'D': 'Needs Work'}[scores['grade']]
    return scores

health = calculate_health_score(data)

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:12px 0 16px;'>"
                f"<div style='font-size:24px;'>🎯</div>"
                f"<div style='font-size:14px; font-weight:700; color:{C['gray_900']}; margin-top:4px;'>SEO Health</div>"
                f"<div style='font-size:10px; color:{C['gray_500']}; margin-top:2px;'>Intelligence Platform v2.0</div>"
                f"</div>", unsafe_allow_html=True)
    st.markdown("---")

    lang = st.selectbox("🌐", list(T.keys()), label_visibility="collapsed", key="lang_select")
    t = T[lang]

    nav_list = [
        t['nav_exec'], t['nav_health'], t['nav_trend'], t['nav_keyword'],
        t['nav_page'], t['nav_country'], t['nav_device'], t['nav_anomaly'], t['nav_recommend']
    ]
    page = st.radio("Navigation", nav_list, label_visibility="collapsed", key="nav_radio")

    st.markdown("---")
    st.markdown(f"<p style='font-size:10px; font-weight:700; color:{C['gray_400']}; letter-spacing:1px;'>📅 DATA FILTER</p>", unsafe_allow_html=True)
    if data.get('by_date') is not None:
        min_d = data['by_date']['data_date'].min().date()
        max_d = data['by_date']['data_date'].max().date()
        g_start = st.date_input(t['start_date'], value=min_d, min_value=min_d, max_value=max_d, key="date_start")
        g_end = st.date_input(t['end_date'], value=max_d, min_value=min_d, max_value=max_d, key="date_end")
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
    st.download_button(t['export_csv'], df.to_csv(index=False).encode('utf-8-sig'), name, 'text/csv', key=f"dl_{name}")

def kpi_html(label, value):
    return f"<div class='kpi-box'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>"

def insight_box(text):
    st.markdown(f"<div class='insight-box'><div class='insight-title'>💡 {t['key_finding']}</div>"
                f"<div class='insight-text'>{text}</div></div>", unsafe_allow_html=True)

def warn_box(text):
    st.markdown(f"<div class='warn-box'><div class='warn-title'>🎯 {t['recommendation']}</div>"
                f"<div class='warn-text'>{text}</div></div>", unsafe_allow_html=True)

def dim_bar(label, score, weight):
    color = C['green'] if score >= 70 else C['amber'] if score >= 50 else C['red']
    return f"""<div style='margin-bottom:12px;'>
        <div style='display:flex; justify-content:space-between;'>
            <span style='font-size:13px; font-weight:500; color:{C["gray_700"]};'>{label}</span>
            <span style='font-size:13px; font-weight:700; color:{C["gray_900"]};'>{score}</span>
        </div>
        <div style='font-size:10px; color:{C["gray_400"]};'>Weight: {weight}%</div>
        <div class='dim-bar'><div class='dim-bar-fill' style='width:{score}%; background:{color};'></div></div>
    </div>"""

# ============================================================
# 页面1：Executive Overview
# ============================================================
if page == t['nav_exec']:
    if data.get('daily_summary') is not None:
        df = date_filter(data['daily_summary'].copy(), g_start, g_end)
        tc = int(df['clicks'].sum())
        ti = int(df['impressions'].sum())
        ac = df['ctr'].mean() * 100
        ap = df['position'].mean()

        # 评分区域
        g = health['grade']
        col_score, col_dims, col_summary = st.columns([1, 1.2, 1.8])

        with col_score:
            st.markdown(f"<div class='card' style='text-align:center;'>"
                        f"<div class='card-title'>{t['health_score']}</div>"
                        f"<div class='score-ring score-{g}'>{g}</div>"
                        f"<div style='font-size:32px; font-weight:800; color:{C['gray_900']}; margin-top:8px;'>{health['total']}</div>"
                        f"<div style='font-size:12px; color:{C['gray_500']};'>/ 100 · {health['grade_cn'] if lang=='中文' else health['grade_en']}</div>"
                        f"</div>", unsafe_allow_html=True)

        with col_dims:
            st.markdown(f"<div class='card'>"
                        f"<div class='card-title'>DIMENSION SCORES</div>"
                        f"{dim_bar(t['search_perf'], health['search'], 40)}"
                        f"{dim_bar(t['content_eff'], health['content'], 35)}"
                        f"{dim_bar(t['tech_exp'], health['tech'], 25)}"
                        f"</div>", unsafe_allow_html=True)

        with col_summary:
            weakness = t['search_perf'] if health['search'] <= min(health['content'], health['tech']) else t['content_eff'] if health['content'] <= health['tech'] else t['tech_exp']
            w_score = min(health['search'], health['content'], health['tech'])
            if lang == '中文':
                summary_text = f"网站SEO整体处于<strong>中等水平</strong>。最大短板为<strong>{weakness}</strong>（{w_score}分），建议优先优化排名11-20的关键词和低CTR页面。"
                opp_text = "优化高展示低CTR页面的标题和描述"
            else:
                summary_text = f"Overall SEO health is <strong>moderate</strong>. Weakest: <strong>{weakness}</strong> ({w_score} pts). Priority: optimize keywords ranked 11-20 and low-CTR pages."
                opp_text = "Optimize title/description of high-impression low-CTR pages"

            st.markdown(f"<div class='card'>"
                        f"<div class='card-title'>🤖 {t['exec_summary']}</div>"
                        f"<p style='font-size:13px; color:{C['gray_700']}; line-height:1.6;'>{summary_text}</p>"
                        f"<div style='margin-top:12px; padding:8px 12px; background:{C['blue_light']}; border-radius:8px;'>"
                        f"<span style='font-size:10px; font-weight:700; color:{C['blue']};'>{t['main_opportunity']}</span><br>"
                        f"<span style='font-size:13px; color:{C['gray_900']}; font-weight:500;'>{opp_text}</span>"
                        f"</div></div>", unsafe_allow_html=True)

        # KPI
        st.markdown("<br>", unsafe_allow_html=True)
        kw_count = data['by_query']['query'].nunique() if data.get('by_query') is not None else '-'
        country_count = data['by_country']['country'].nunique() if data.get('by_country') is not None else '-'
        cols = st.columns(6)
        kpi_data = [
            (t['total_clicks'], f"{tc:,}"), (t['total_impressions'], f"{ti:,}"),
            (t['avg_ctr'], f"{ac:.2f}%"), (t['avg_position'], f"{ap:.1f}"),
            (t['total_keywords'], f"{kw_count:,}" if isinstance(kw_count, int) else kw_count),
            (t['countries_covered'], str(country_count)),
        ]
        for col, (lb, val) in zip(cols, kpi_data):
            col.markdown(kpi_html(lb, val), unsafe_allow_html=True)

        # 趋势缩略图
        st.markdown("<br>", unsafe_allow_html=True)
        col_t1, col_t2 = st.columns(2)
        df_s = df.sort_values('data_date')
        with col_t1:
            st.markdown(f"<div class='card-title'>{t['clicks']} TREND</div>", unsafe_allow_html=True)
            fig = px.area(df_s, x='data_date', y='clicks', color_discrete_sequence=[C['blue']])
            fig.update_traces(line_width=2, fillcolor='rgba(37,99,235,0.08)')
            fig.update_layout(height=180, xaxis_title="", yaxis_title="", showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="exec_clicks_trend")
        with col_t2:
            st.markdown(f"<div class='card-title'>{t['impressions']} TREND</div>", unsafe_allow_html=True)
            fig2 = px.area(df_s, x='data_date', y='impressions', color_discrete_sequence=[C['green']])
            fig2.update_traces(line_width=2, fillcolor='rgba(16,185,129,0.08)')
            fig2.update_layout(height=180, xaxis_title="", yaxis_title="", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True, key="exec_imp_trend")
    else:
        empty_state("📊", t['no_data_desc'])

# ============================================================
# 页面2：SEO Health Score
# ============================================================
elif page == t['nav_health']:
    g = health['grade']
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"<div class='card' style='text-align:center;'>"
                    f"<div class='card-title'>{t['health_score']}</div>"
                    f"<div class='score-ring score-{g}'>{g}</div>"
                    f"<div style='font-size:36px; font-weight:800; margin-top:8px;'>{health['total']}</div>"
                    f"<div style='font-size:12px; color:{C['gray_500']};'>/ 100</div>"
                    f"</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>"
                    f"<div class='card-title'>DIMENSIONS</div>"
                    f"{dim_bar(t['search_perf'], health['search'], 40)}"
                    f"{dim_bar(t['content_eff'], health['content'], 35)}"
                    f"{dim_bar(t['tech_exp'], health['tech'], 25)}"
                    f"</div>", unsafe_allow_html=True)

    with col2:
        cats = [t['search_perf'], t['content_eff'], t['tech_exp']]
        vals = [health['search'], health['content'], health['tech']]
        fig = go.Figure(data=go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill='toself', fillcolor='rgba(37,99,235,0.1)',
            line=dict(color=C['blue'], width=2)
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                          showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True, key="health_radar")

        st.markdown(f"<div class='card'><div class='card-title'>🏗️ {t['model_arch']}</div>"
                    f"<p style='font-size:12px; color:{C['gray_700']};'>"
                    f"<strong>V2.0</strong> — 3 Dimensions, 9 Metrics | Weighted Model<br><br>"
                    f"<code>Score = Search(40%) + Content(35%) + Technical(25%)</code><br><br>"
                    f"<strong>Future V3.0:</strong> + Backlink Authority (Ahrefs/Moz API)</p>"
                    f"</div>", unsafe_allow_html=True)

    with st.expander(f"📖 {t['scoring_method']}", expanded=False):
        st.markdown(f"""
| Dimension | Weight | Metrics | Benchmark |
|---|---|---|---|
| {t['search_perf']} | 40% | CTR, Position, Click Trend | B2B CTR 2-3%=Good; Top10=Full |
| {t['content_eff']} | 35% | Keyword Coverage, Page Active Rate, Geo Coverage | 500+ keywords=Excellent |
| {t['tech_exp']} | 25% | Device Coverage, Mobile Ratio, Data Continuity | 3 devices=Full; B2B mobile 15-35% |
        """)
    with st.expander(f"🔗 {t['backlink_reserved']}", expanded=False):
        st.info(t['backlink_desc'])

# ============================================================
# 页面3：搜索趋势
# ============================================================
elif page == t['nav_trend']:
    if data.get('daily_summary') is not None:
        df = date_filter(data['daily_summary'].copy().sort_values('data_date'), g_start, g_end)
        if len(df) > 0:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=df['data_date'], y=df['impressions'], name=t['impressions'],
                                 marker_color=C['chart'][4], opacity=0.4), secondary_y=False)
            fig.add_trace(go.Scatter(x=df['data_date'], y=df['clicks'], name=t['clicks'],
                                     line=dict(color=C['blue'], width=2), mode='lines'), secondary_y=True)
            fig.update_yaxes(title_text=t['impressions'], secondary_y=False)
            fig.update_yaxes(title_text=t['clicks'], secondary_y=True)
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True, key="trend_main")

            # Insight
            recent_clicks = df.tail(30)['clicks'].mean()
            earlier_clicks = df.head(30)['clicks'].mean()
            if earlier_clicks > 0:
                change = (recent_clicks - earlier_clicks) / earlier_clicks * 100
                if lang == '中文':
                    insight_box(f"近30天平均点击量相比早期{'上升' if change > 0 else '下降'}了 <strong>{abs(change):.1f}%</strong>。{'流量呈增长趋势。' if change > 0 else '建议排查流量下降原因。'}")
                else:
                    insight_box(f"Recent 30-day avg clicks {'increased' if change > 0 else 'decreased'} by <strong>{abs(change):.1f}%</strong>. {'Traffic growing.' if change > 0 else 'Investigate decline.'}")

            col_a, col_b = st.columns(2)
            with col_a:
                fig2 = px.line(df, x='data_date', y='ctr', color_discrete_sequence=[C['green']])
                fig2.update_layout(height=200, title=t['ctr'], yaxis_tickformat='.2%')
                st.plotly_chart(fig2, use_container_width=True, key="trend_ctr")
            with col_b:
                fig3 = px.line(df, x='data_date', y='position', color_discrete_sequence=[C['amber']])
                fig3.update_yaxes(autorange="reversed")
                fig3.update_layout(height=200, title=t['position'])
                st.plotly_chart(fig3, use_container_width=True, key="trend_pos")

            # 月度汇总
            df['month'] = df['data_date'].dt.to_period('M').astype(str)
            monthly = df.groupby('month').agg({'clicks': 'sum', 'impressions': 'sum'}).reset_index()
            st.markdown(f"<div class='card-title'>{t['monthly_summary']}</div>", unsafe_allow_html=True)
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(x=monthly['month'], y=monthly['clicks'], name=t['clicks'],
                                  marker_color=C['blue'], text=monthly['clicks'], textposition='outside'))
            fig4.update_layout(height=260)
            st.plotly_chart(fig4, use_container_width=True, key="trend_monthly")
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

        click_rate = kc / tk * 100 if tk > 0 else 0
        if lang == '中文':
            insight_box(f"共覆盖 <strong>{tk}</strong> 个关键词，其中仅 <strong>{click_rate:.1f}%</strong> 产生了点击。大量关键词有展示但无转化，存在优化空间。")
        else:
            insight_box(f"Covering <strong>{tk}</strong> keywords, only <strong>{click_rate:.1f}%</strong> generate clicks. Optimization opportunity exists.")

        # 排名分布
        st.markdown(f"<div class='card-title'>{t['position_dist']}</div>", unsafe_allow_html=True)
        df_q['bucket'] = pd.cut(df_q['position'], bins=[0, 3, 10, 20, 50, 100], labels=['Top 3', '4-10', '11-20', '21-50', '50+'])
        pd_dist = df_q['bucket'].value_counts().sort_index().reset_index()
        pd_dist.columns = ['Range', 'Count']
        fig = px.bar(pd_dist, x='Range', y='Count', color_discrete_sequence=[C['blue']], text='Count')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=240, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True, key="kw_dist")

        # 机会关键词
        st.markdown(f"<div class='card-title'>🎯 {t['opportunity_kw']}</div>"
                    f"<p style='font-size:11px; color:{C['gray_500']};'>{t['opportunity_kw_desc']}</p>", unsafe_allow_html=True)
        kw_agg = df_q.groupby('query').agg({'clicks': 'sum', 'impressions': 'sum', 'position': 'mean'}).reset_index()
        kw_agg['ctr'] = kw_agg['clicks'] / kw_agg['impressions'].replace(0, 1)
        opp = kw_agg[(kw_agg['impressions'] >= 10) & (kw_agg['ctr'] < 0.02) &
                     (kw_agg['position'] >= 11) & (kw_agg['position'] <= 30)].sort_values('impressions', ascending=False).head(20)
        if len(opp) > 0:
            warn_box(f"{'发现' if lang=='中文' else 'Found'} <strong>{len(opp)}</strong> {'个机会关键词，优化这些词的排名和CTR可快速提升流量。' if lang=='中文' else ' opportunity keywords. Optimizing these can quickly boost traffic.'}")
            opp_d = opp.copy()
            opp_d['ctr'] = (opp_d['ctr'] * 100).round(2)
            opp_d['position'] = opp_d['position'].round(1)
            st.dataframe(opp_d[['query', 'clicks', 'impressions', 'ctr', 'position']].rename(
                columns={'query': 'Keyword', 'clicks': t['clicks'], 'impressions': t['impressions'], 'ctr': 'CTR%', 'position': t['position']}
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
            columns={'query': 'Keyword', 'clicks': t['clicks'], 'impressions': t['impressions'], 'ctr': 'CTR%', 'position': t['position']}
        ), use_container_width=True, hide_index=True, height=300)
        csv_export(top_kw, "top_keywords.csv")
    else:
        empty_state("🔍", t['no_data_desc'])

# ============================================================
# 页面5：页面效果
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

        if lang == '中文':
            insight_box(f"共 <strong>{tp}</strong> 个页面被索引，其中 <strong>{100-ar:.1f}%</strong> 的页面零点击。建议审查无效页面，合并或优化低质量内容。")
        else:
            insight_box(f"<strong>{tp}</strong> pages indexed, <strong>{100-ar:.1f}%</strong> have zero clicks. Audit and consolidate thin content.")

        # 机会矩阵
        st.markdown(f"<div class='card-title'>📊 {t['page_matrix']}</div>", unsafe_allow_html=True)
        pg_agg = df_p.groupby('page').agg({'clicks': 'sum', 'impressions': 'sum', 'position': 'mean'}).reset_index()
        pg_agg['ctr'] = pg_agg['clicks'] / pg_agg['impressions'].replace(0, 1)
        pg_m = pg_agg[pg_agg['impressions'] >= 5].copy()
        if len(pg_m) > 0:
            fig = px.scatter(pg_m, x='impressions', y='clicks', color='position',
                             hover_data=['page'], color_continuous_scale='Blues_r',
                             labels={'impressions': t['impressions'], 'clicks': t['clicks'], 'position': t['position']})
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True, key="page_matrix")

        # 高展示低CTR
        st.markdown(f"<div class='card-title'>🎯 {t['opportunity_pages']}</div>"
                    f"<p style='font-size:11px; color:{C['gray_500']};'>{t['opportunity_pages_desc']}</p>", unsafe_allow_html=True)
        opp_p = pg_agg[(pg_agg['impressions'] >= 20) & (pg_agg['ctr'] < 0.01)].sort_values('impressions', ascending=False).head(15)
        if len(opp_p) > 0:
            warn_box(f"{'发现' if lang=='中文' else 'Found'} <strong>{len(opp_p)}</strong> {'个高展示低CTR页面，优化标题和描述可快速提升点击。' if lang=='中文' else ' high-impression low-CTR pages. Optimize titles for quick wins.'}")
            opp_pd = opp_p.copy()
            opp_pd['ctr'] = (opp_pd['ctr'] * 100).round(2)
            opp_pd['position'] = opp_pd['position'].round(1)
            opp_pd['page'] = opp_pd['page'].str.replace('https://www.advich.com', '', regex=False)
            st.dataframe(opp_pd[['page', 'clicks', 'impressions', 'ctr', 'position']].rename(
                columns={'page': 'Page', 'clicks': t['clicks'], 'impressions': t['impressions'], 'ctr': 'CTR%', 'position': t['position']}
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
            columns={'page': 'Page', 'clicks': t['clicks'], 'impressions': t['impressions'], 'ctr': 'CTR%', 'position': t['position']}
        ), use_container_width=True, hide_index=True, height=280)
        csv_export(top_p, "top_pages.csv")
    else:
        empty_state("📄", t['no_data_desc'])

# ============================================================
# 页面6：国家/地区（含世界地图）
# ============================================================
elif page == t['nav_country']:
    if data.get('by_country') is not None:
        df_c = date_filter(data['by_country'].copy(), g_start, g_end)
        total_countries = df_c['country'].nunique()

        st.markdown(kpi_html(t['countries_covered'], str(total_countries)), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        c_agg = df_c.groupby('country').agg({'clicks': 'sum', 'impressions': 'sum', 'position': 'mean'}).reset_index()
        c_agg['ctr'] = c_agg['clicks'] / c_agg['impressions'].replace(0, 1)
        c_agg = c_agg.sort_values('clicks', ascending=False)

        top3 = c_agg.head(3)['country'].tolist()
        top3_str = ', '.join(top3)
        if lang == '中文':
            insight_box(f"流量覆盖 <strong>{total_countries}</strong> 个国家/地区。Top 3 市场为 <strong>{top3_str}</strong>，集中度较高，建议拓展更多目标市场。")
        else:
            insight_box(f"Traffic covers <strong>{total_countries}</strong> countries. Top 3: <strong>{top3_str}</strong>. Consider expanding to more markets.")

        # 世界地图
        st.markdown(f"<div class='card-title'>🌍 {t['geo_map']}</div>", unsafe_allow_html=True)
        fig_map = px.choropleth(
            c_agg, locations='country', locationmode='ISO-3',
            color='clicks', hover_name='country',
            hover_data={'impressions': True, 'clicks': True},
            color_continuous_scale=[[0, '#EFF6FF'], [0.25, '#BFDBFE'], [0.5, '#60A5FA'], [0.75, '#2563EB'], [1, '#1D4ED8']],
            labels={'clicks': t['clicks'], 'impressions': t['impressions']},
        )
        fig_map.update_geos(
            showcoastlines=True, coastlinecolor=C['gray_200'],
            showland=True, landcolor=C['gray_50'],
            showocean=True, oceancolor=C['white'],
            showframe=False, projection_type='natural earth'
        )
        fig_map.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0),
                              coloraxis_colorbar=dict(title=t['clicks'], thickness=12, len=0.6))
        st.plotly_chart(fig_map, use_container_width=True, key="country_map")

        # Top 国家柱状图
        st.markdown(f"<div class='card-title'>🏆 {t['top_countries']} (Top 15)</div>", unsafe_allow_html=True)
        top_c = c_agg.head(15)
        fig_bar = px.bar(top_c, x='country', y='clicks', text='clicks',
                         color_discrete_sequence=[C['blue']])
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(height=300, xaxis_title="", yaxis_title=t['clicks'])
        st.plotly_chart(fig_bar, use_container_width=True, key="country_bar")

        # 详细数据表
        st.markdown(f"<div class='card-title'>📋 {t['detail_data']}</div>", unsafe_allow_html=True)
        c_display = c_agg.head(30).copy()
        c_display['ctr'] = (c_display['ctr'] * 100).round(2)
        c_display['position'] = c_display['position'].round(1)
        st.dataframe(c_display[['country', 'clicks', 'impressions', 'ctr', 'position']].rename(
            columns={'country': t['country'], 'clicks': t['clicks'], 'impressions': t['impressions'], 'ctr': 'CTR%', 'position': t['position']}
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

        total_imp = d_agg['impressions'].sum()
        if total_imp > 0:
            desktop_pct = d_agg[d_agg['device'] == 'DESKTOP']['impressions'].sum() / total_imp * 100
            mobile_pct = d_agg[d_agg['device'] == 'MOBILE']['impressions'].sum() / total_imp * 100
            if lang == '中文':
                insight_box(f"桌面端占比 <strong>{desktop_pct:.1f}%</strong>，移动端 <strong>{mobile_pct:.1f}%</strong>。符合B2B行业特征（桌面为主），但需确保移动端体验良好。")
            else:
                insight_box(f"Desktop: <strong>{desktop_pct:.1f}%</strong>, Mobile: <strong>{mobile_pct:.1f}%</strong>. Typical B2B pattern. Ensure good mobile experience.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card-title'>{t['imp_share']}</div>", unsafe_allow_html=True)
            fig1 = px.pie(d_agg, values='impressions', names='device', color_discrete_sequence=C['chart'][:3])
            fig1.update_traces(textinfo='label+percent', textfont_size=12)
            fig1.update_layout(height=260, showlegend=False)
            st.plotly_chart(fig1, use_container_width=True, key="device_imp_pie")
        with col2:
            st.markdown(f"<div class='card-title'>{t['click_share']}</div>", unsafe_allow_html=True)
            fig2 = px.pie(d_agg, values='clicks', names='device', color_discrete_sequence=C['chart'][:3])
            fig2.update_traces(textinfo='label+percent', textfont_size=12)
            fig2.update_layout(height=260, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True, key="device_click_pie")

        # 设备对比表
        st.markdown(f"<div class='card-title'>📊 DEVICE COMPARISON</div>", unsafe_allow_html=True)
        d_display = d_agg.copy()
        d_display['ctr'] = (d_display['ctr'] * 100).round(2)
        d_display['position'] = d_display['position'].round(1)
        st.dataframe(d_display[['device', 'clicks', 'impressions', 'ctr', 'position']].rename(
            columns={'device': t['device'], 'clicks': t['clicks'], 'impressions': t['impressions'], 'ctr': 'CTR%', 'position': t['position']}
        ), use_container_width=True, hide_index=True)

        # 月度趋势
        if 'data_date' in df_d.columns:
            st.markdown(f"<div class='card-title'>📈 {t['device_trend']}</div>", unsafe_allow_html=True)
            df_d['month'] = df_d['data_date'].dt.to_period('M').astype(str)
            monthly_d = df_d.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
            fig3 = px.line(monthly_d, x='month', y='clicks', color='device',
                           color_discrete_sequence=C['chart'][:3], markers=True)
            fig3.update_layout(height=280)
            st.plotly_chart(fig3, use_container_width=True, key="device_trend")
        csv_export(d_agg, "device_analysis.csv")
    else:
        empty_state("📱", t['no_data_desc'])

# ============================================================
# 页面8：异常监控
# ============================================================
elif page == t['nav_anomaly']:
    if data.get('daily_summary') is not None:
        df = date_filter(data['daily_summary'].copy().sort_values('data_date'), g_start, g_end)
        if len(df) > 0:
            col_s, col_m = st.columns(2)
            with col_s:
                sensitivity = st.slider(t['sensitivity'], 1.0, 3.0, 2.0, 0.1, key="anomaly_sens")
            with col_m:
                metric_col = st.selectbox(t['select_metric'], ['clicks', 'impressions', 'ctr', 'position'], key="anomaly_metric")

            # Z-Score 异常检测
            df['rolling_mean'] = df[metric_col].rolling(window=7, min_periods=1).mean()
            df['rolling_std'] = df[metric_col].rolling(window=7, min_periods=1).std()
            df['z_score'] = ((df[metric_col] - df['rolling_mean']) / df['rolling_std'].replace(0, 1)).abs()
            df['is_anomaly'] = df['z_score'] > sensitivity

            anomaly_count = df['is_anomaly'].sum()
            anomaly_rate = anomaly_count / len(df) * 100

            cols = st.columns(3)
            cols[0].markdown(kpi_html(t['days_analyzed'], str(len(df))), unsafe_allow_html=True)
            cols[1].markdown(kpi_html(t['anomalies_found'], str(anomaly_count)), unsafe_allow_html=True)
            cols[2].markdown(kpi_html(t['anomaly_rate'], f"{anomaly_rate:.1f}%"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            if anomaly_count > 0:
                if lang == '中文':
                    warn_box(f"检测到 <strong>{anomaly_count}</strong> 个异常点（异常率 {anomaly_rate:.1f}%）。建议逐一排查异常日期，确认是否有外部因素影响。")
                else:
                    warn_box(f"Detected <strong>{anomaly_count}</strong> anomalies ({anomaly_rate:.1f}% rate). Investigate each date for external factors.")

            # 异常可视化
            fig = go.Figure()
            normal = df[~df['is_anomaly']]
            anomaly = df[df['

