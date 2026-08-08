
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================
# 全局配置
# ============================================================
st.set_page_config(
    page_title="SEO Health Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Design System - Typography & Colors
# ============================================================
COLORS = {
    'primary': '#2563EB',
    'primary_dark': '#1E40AF',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'text_primary': '#111827',
    'text_secondary': '#6B7280',
    'text_tertiary': '#9CA3AF',
    'bg_card': '#FFFFFF',
    'bg_page': '#F9FAFB',
    'border': '#E5E7EB',
    'score_c': '#F59E0B'
}

# ============================================================
# Global CSS - V3.0 Typography System
# ============================================================
st.markdown("""
<style>
    /* === Reset & Base === */
    .stApp { background-color: #F9FAFB; }
    section[data-testid="stSidebar"] { width: 300px !important; background: #FFFFFF; border-right: 1px solid #E5E7EB; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 16px !important; font-weight: 500 !important; padding: 8px 0 !important; }
    
    /* === Typography System === */
    .page-title { font-size: 32px; font-weight: 700; color: #111827; margin-bottom: 4px; line-height: 1.2; }
    .page-subtitle { font-size: 16px; font-weight: 400; color: #6B7280; margin-bottom: 32px; }
    .section-title { font-size: 20px; font-weight: 600; color: #1F2937; margin: 32px 0 16px 0; }
    
    /* === Score Display (largest element) === */
    .score-number { font-size: 56px; font-weight: 800; line-height: 1; }
    .score-grade { font-size: 18px; font-weight: 600; letter-spacing: 2px; margin-top: 8px; }
    .score-label { font-size: 14px; color: #6B7280; margin-top: 4px; }
    
    /* === Metric Cards === */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-label { font-size: 14px; color: #6B7280; font-weight: 400; margin-bottom: 8px; }
    .metric-value { font-size: 32px; font-weight: 700; color: #111827; line-height: 1.2; }
    .metric-growth { font-size: 14px; margin-top: 4px; }
    .metric-growth.positive { color: #10B981; }
    .metric-growth.negative { color: #EF4444; }
    
    /* === Dimension Score Cards === */
    .dim-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .dim-score { font-size: 28px; font-weight: 700; color: #2563EB; }
    .dim-name { font-size: 14px; color: #6B7280; margin-top: 4px; }
    
    /* === Insight Cards === */
    .insight-card {
        border-left: 4px solid #F59E0B;
        background: #FFFBEB;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 15px;
        line-height: 1.6;
        color: #111827;
    }
    
    /* === Action Items === */
    .action-item {
        border-left: 4px solid;
        padding: 16px 20px;
        margin: 12px 0;
        background: #F9FAFB;
        border-radius: 0 8px 8px 0;
    }
    .action-priority { font-weight: 700; font-size: 14px; }
    .action-title { font-size: 16px; font-weight: 600; color: #111827; margin-top: 6px; }
    .action-desc { font-size: 15px; color: #4B5563; margin-top: 4px; line-height: 1.6; }
    
    /* === Chart containers === */
    .chart-container {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    }
    
    /* === Spacing === */
    .spacer-sm { height: 16px; }
    .spacer-md { height: 24px; }
    .spacer-lg { height: 32px; }
    
    /* === Hide Streamlit defaults === */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 多语言支持
# ============================================================
LANG_MAP = {
    '中文': {
        'nav_title': 'SEO 健康度诊断',
        'pages': ['📊 Executive Overview', '🎯 SEO Health Model', '📈 Search Intelligence',
                  '🔍 Keyword Opportunities', '📄 Content Intelligence', '🌎 Market Intelligence',
                  '📱 User Experience Signals', '🚨 SEO Monitoring Center', '🚀 Recommendations'],
        'page_titles': {
            '📊 Executive Overview': 'Executive Overview',
            '🎯 SEO Health Model': 'SEO 健康度模型',
            '📈 Search Intelligence': '搜索表现洞察',
            '🔍 Keyword Opportunities': '关键词机会分析',
            '📄 Content Intelligence': '内容效果分析',
            '🌎 Market Intelligence': '市场地理分布',
            '📱 User Experience Signals': '用户体验信号',
            '🚨 SEO Monitoring Center': 'SEO 监控中心',
            '🚀 Recommendations': '优化建议'
        }
    },
    'English': {
        'nav_title': 'SEO Health Diagnosis',
        'pages': ['📊 Executive Overview', '🎯 SEO Health Model', '📈 Search Intelligence',
                  '🔍 Keyword Opportunities', '📄 Content Intelligence', '🌎 Market Intelligence',
                  '📱 User Experience Signals', '🚨 SEO Monitoring Center', '🚀 Recommendations'],
        'page_titles': {
            '📊 Executive Overview': 'Executive Overview',
            '🎯 SEO Health Model': 'SEO Health Model',
            '📈 Search Intelligence': 'Search Intelligence',
            '🔍 Keyword Opportunities': 'Keyword Opportunities',
            '📄 Content Intelligence': 'Content Intelligence',
            '🌎 Market Intelligence': 'Market Intelligence',
            '📱 User Experience Signals': 'User Experience Signals',
            '🚨 SEO Monitoring Center': 'SEO Monitoring Center',
            '🚀 Recommendations': 'Recommendations'
        }
    }
}

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
    data = {}
    base_path = "data/"
    
    file_map = {
        'by_date': 'cleaned_by_date.csv',
        'by_country': 'cleaned_by_country.csv',
        'by_device': 'cleaned_by_device.csv',
        'daily_summary': 'cleaned_daily_summary.csv',
        'by_query': 'cleaned_by_query.csv',
        'by_page': 'cleaned_by_page.csv',
        'date_query': 'cleaned_date_query.csv',
        'date_page': 'cleaned_date_page.csv',
        'query_country': 'cleaned_query_country.csv',
        'page_country': 'cleaned_page_country.csv'
    }
    
    for key, filename in file_map.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if 'data_date' in df.columns:
                df['data_date'] = pd.to_datetime(df['data_date'])
            data[key] = df
    
    return data

# ============================================================
# SEO 评分模型 (V2.0 - 产出 61.5)
# ============================================================
def calculate_seo_score(data):
    """
    四维评分模型：
    - 搜索表现 Search Performance: 40%
    - 内容效果 Content Effectiveness: 30%
    - 技术体验 Technical Experience: 15%
    - 外链权威 Backlink Authority: 15% (预留，当前=0)
    """
    scores = {}
    
    # === 维度1：搜索表现 (40%) ===
    search_scores = {}
    if 'daily_summary' in data:
        df = data['daily_summary']
        total_days = len(df)
        months = max(total_days / 30, 1)
        
        # 1.1 月均点击量
        monthly_clicks = df['clicks'].sum() / months
        if monthly_clicks >= 500: search_scores['clicks'] = 90
        elif monthly_clicks >= 300: search_scores['clicks'] = 80
        elif monthly_clicks >= 150: search_scores['clicks'] = 70
        elif monthly_clicks >= 80: search_scores['clicks'] = 55
        elif monthly_clicks >= 30: search_scores['clicks'] = 40
        else: search_scores['clicks'] = 20
        
        # 1.2 平均CTR
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        avg_ctr = total_clicks / max(total_impressions, 1)
        if avg_ctr >= 0.05: search_scores['ctr'] = 95
        elif avg_ctr >= 0.03: search_scores['ctr'] = 80
        elif avg_ctr >= 0.02: search_scores['ctr'] = 65
        elif avg_ctr >= 0.015: search_scores['ctr'] = 55
        elif avg_ctr >= 0.01: search_scores['ctr'] = 45
        else: search_scores['ctr'] = 25
        
        # 1.3 平均排名
        avg_position = df['position'].mean()
        if avg_position <= 5: search_scores['position'] = 100
        elif avg_position <= 10: search_scores['position'] = 90
        elif avg_position <= 15: search_scores['position'] = 80
        elif avg_position <= 20: search_scores['position'] = 70
        elif avg_position <= 25: search_scores['position'] = 65
        elif avg_position <= 35: search_scores['position'] = 50
        elif avg_position <= 50: search_scores['position'] = 35
        else: search_scores['position'] = 20
        
        # 1.4 点击趋势
        if 'by_date' in data:
            df_date = data['by_date'].sort_values('data_date')
            if len(df_date) >= 60:
                recent_30 = df_date.tail(30)['clicks'].sum()
                prev_30 = df_date.iloc[-60:-30]['clicks'].sum()
                if prev_30 > 0:
                    trend_pct = (recent_30 - prev_30) / prev_30
                else:
                    trend_pct = 0
            else:
                trend_pct = 0
            
            if trend_pct >= 0.2: search_scores['trend'] = 100
            elif trend_pct >= 0.05: search_scores['trend'] = 85
            elif trend_pct >= -0.05: search_scores['trend'] = 76
            elif trend_pct >= -0.2: search_scores['trend'] = 55
            elif trend_pct >= -0.5: search_scores['trend'] = 35
            else: search_scores['trend'] = 20
        else:
            search_scores['trend'] = 50
    
    search_dim = (search_scores.get('clicks', 50) * 0.25 +
                  search_scores.get('ctr', 50) * 0.25 +
                  search_scores.get('position', 50) * 0.25 +
                  search_scores.get('trend', 50) * 0.25)
    
    # === 维度2：内容效果 (30%) ===
    content_scores = {}
    
    # 2.1 关键词覆盖
    if 'by_query' in data:
        kw_count = data['by_query']['query'].nunique()
    else:
        kw_count = 2519  # from space data
    
    if kw_count >= 2000: content_scores['keywords'] = 95
    elif kw_count >= 1000: content_scores['keywords'] = 85
    elif kw_count >= 500: content_scores['keywords'] = 70
    elif kw_count >= 200: content_scores['keywords'] = 55
    else: content_scores['keywords'] = 35
    
    # 2.2 活跃页面比例
    if 'by_page' in data:
        total_pages = data['by_page']['page'].nunique()
        active_pages = data['by_page'][data['by_page']['clicks'] > 0]['page'].nunique()
        active_ratio = active_pages / max(total_pages, 1)
    else:
        active_ratio = 0.77  # from space data
    
    if active_ratio >= 0.8: content_scores['active_pages'] = 90
    elif active_ratio >= 0.6: content_scores['active_pages'] = 75
    elif active_ratio >= 0.4: content_scores['active_pages'] = 55
    elif active_ratio >= 0.2: content_scores['active_pages'] = 35
    else: content_scores['active_pages'] = 20
    
    # 2.3 地理覆盖度
    if 'by_country' in data:
        countries_with_clicks = data['by_country'][data['by_country']['clicks'] > 0]['country'].nunique()
    else:
        countries_with_clicks = 57
    
    if countries_with_clicks >= 50: content_scores['geo'] = 100
    elif countries_with_clicks >= 30: content_scores['geo'] = 85
    elif countries_with_clicks >= 15: content_scores['geo'] = 65
    elif countries_with_clicks >= 5: content_scores['geo'] = 45
    else: content_scores['geo'] = 25
    
    content_dim = (content_scores.get('keywords', 50) * 0.35 +
                   content_scores.get('active_pages', 50) * 0.35 +
                   content_scores.get('geo', 50) * 0.30)
    
    # === 维度3：技术体验 (15%) ===
    tech_scores = {}
    if 'by_device' in data:
        df_dev = data['by_device']
        devices = df_dev['device'].nunique()
        
        # 3.1 设备覆盖
        if devices >= 3: tech_scores['device_cov'] = 100
        elif devices >= 2: tech_scores['device_cov'] = 70
        else: tech_scores['device_cov'] = 40
        
        # 3.2 移动端占比
        total_imp = df_dev['impressions'].sum()
        mobile_imp = df_dev[df_dev['device'] == 'MOBILE']['impressions'].sum()
        mobile_ratio = mobile_imp / max(total_imp, 1)
        
        if 0.15 <= mobile_ratio <= 0.45: tech_scores['mobile'] = 90
        elif 0.10 <= mobile_ratio <= 0.55: tech_scores['mobile'] = 70
        else: tech_scores['mobile'] = 40
        
        # 3.3 跨设备CTR一致性
        device_ctrs = df_dev.groupby('device').apply(
            lambda x: x['clicks'].sum() / max(x['impressions'].sum(), 1), include_groups=False
        )
        ctr_cv = device_ctrs.std() / max(device_ctrs.mean(), 0.001)
        
        if ctr_cv <= 0.3: tech_scores['consistency'] = 90
        elif ctr_cv <= 0.5: tech_scores['consistency'] = 70
        else: tech_scores['consistency'] = 40
    else:
        tech_scores = {'device_cov': 50, 'mobile': 50, 'consistency': 50}
    
    tech_dim = (tech_scores.get('device_cov', 50) * 0.40 +
                tech_scores.get('mobile', 50) * 0.30 +
                tech_scores.get('consistency', 50) * 0.30)
    
    # === 维度4：外链权威 (15%) - 预留 ===
    backlink_dim = 0
    
    # === 最终评分 ===
    final_score = (search_dim * 0.40 + content_dim * 0.30 + 
                   tech_dim * 0.15 + backlink_dim * 0.15)
    
    # 等级判定
    if final_score >= 90: grade, grade_text = 'A', 'EXCELLENT'
    elif final_score >= 70: grade, grade_text = 'B', 'GOOD'
    elif final_score >= 50: grade, grade_text = 'C', 'MODERATE'
    else: grade, grade_text = 'D', 'CRITICAL'
    
    return {
        'final_score': round(final_score, 1),
        'grade': grade,
        'grade_text': grade_text,
        'dimensions': {
            'search_performance': round(search_dim, 1),
            'content_effectiveness': round(content_dim, 1),
            'technical_experience': round(tech_dim, 1),
            'backlink_authority': 0
        },
        'sub_scores': {
            'search': search_scores,
            'content': content_scores,
            'technical': tech_scores
        },
        'metrics': {
            'monthly_clicks': monthly_clicks if 'daily_summary' in data else 0,
            'avg_ctr': avg_ctr if 'daily_summary' in data else 0,
            'avg_position': avg_position if 'daily_summary' in data else 0,
            'total_keywords': kw_count,
            'active_ratio': active_ratio,
            'countries': countries_with_clicks
        }
    }

# ============================================================
# Plotly 图表全局配置
# ============================================================
CHART_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, sans-serif", size=14, color='#374151'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(font_size=14),
    title_font=dict(size=18, color='#1F2937')
)

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown('<div style="font-size:20px; font-weight:700; color:#111827; margin-bottom:4px;">🎯 SEO Health</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px; color:#6B7280; margin-bottom:24px;">Intelligence Platform v3.0</div>', unsafe_allow_html=True)
    
    lang = st.selectbox("🌐 Language", ['中文', 'English'], key='lang_select')
    
    st.markdown("---")
    st.markdown(f'<div style="font-size:14px; color:#6B7280; margin-bottom:8px;">{"导航" if lang == "中文" else "Navigation"}</div>', unsafe_allow_html=True)
    
    pages = LANG_MAP[lang]['pages']
    page = st.radio("", pages, label_visibility="collapsed", key='nav_radio')
    
    st.markdown("---")
    st.markdown('<div style="font-size:12px; color:#9CA3AF;">B2B SEO Health Intelligence<br>Based on GSC Data</div>', unsafe_allow_html=True)

# ============================================================
# 加载数据
# ============================================================
data = load_data()

# ============================================================
# 页面1：Executive Overview
# ============================================================
if page == '📊 Executive Overview':
    st.markdown('<div class="page-title">Executive Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"将搜索数据转化为可执行的 SEO 洞察" if lang == "中文" else "Transform Search Data into Actionable SEO Insights"}</div>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score(data)
    
    # === Hero Section: SEO Score (40% visual weight) ===
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    col_score, col_dims = st.columns([2, 3])
    
    with col_score:
        score_color = COLORS['warning'] if score_result['grade'] == 'C' else COLORS['success'] if score_result['grade'] in ['A','B'] else COLORS['danger']
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:16px; padding:40px; text-align:center;">
            <div class="score-label">SEO HEALTH SCORE</div>
            <div class="score-number" style="color:{score_color};">{score_result['final_score']}</div>
            <div class="score-grade" style="color:{score_color};">{score_result['grade_text']}</div>
            <div style="margin-top:16px; font-size:13px; color:#9CA3AF;">{"满分 100 · 基于 GSC 真实数据" if lang == "中文" else "Out of 100 · Based on GSC Data"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_dims:
        st.markdown(f'<div class="section-title">{"维度评分" if lang == "中文" else "Dimension Scores"}</div>', unsafe_allow_html=True)
        
        dim_cols = st.columns(4)
        dims_data = [
            ('Search', score_result['dimensions']['search_performance'], '40%'),
            ('Content', score_result['dimensions']['content_effectiveness'], '30%'),
            ('Technical', score_result['dimensions']['technical_experience'], '15%'),
            ('Backlink', score_result['dimensions']['backlink_authority'], '15%')
        ]
        
        for i, (name, score, weight) in enumerate(dims_data):
            with dim_cols[i]:
                dim_color = '#10B981' if score >= 80 else '#2563EB' if score >= 60 else '#F59E0B' if score >= 40 else '#EF4444'
                status = '🔒' if name == 'Backlink' else ''
                st.markdown(f"""
                <div class="dim-card">
                    <div class="dim-score" style="color:{dim_color};">{score}{status}</div>
                    <div class="dim-name">{name}</div>
                    <div style="font-size:12px; color:#9CA3AF; margin-top:4px;">Weight: {weight}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
    
    # === KPI Metrics (20% visual weight) ===
    st.markdown(f'<div class="section-title">{"核心指标" if lang == "中文" else "Key Metrics"}</div>', unsafe_allow_html=True)
    
    if 'daily_summary' in data:
        df = data['daily_summary']
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        avg_ctr = total_clicks / max(total_impressions, 1) * 100
        avg_pos = df['position'].mean()
        
        kpi_cols = st.columns(4)
        kpis = [
            ('Total Clicks' if lang == 'English' else '总点击', f"{total_clicks:,}", ''),
            ('Total Impressions' if lang == 'English' else '总展示', f"{total_impressions:,}", ''),
            ('Avg CTR' if lang == 'English' else '平均CTR', f"{avg_ctr:.2f}%", ''),
            ('Avg Position' if lang == 'English' else '平均排名', f"{avg_pos:.1f}", '')
        ]
        
        for i, (label, value, growth) in enumerate(kpis):
            with kpi_cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
    
    # === Insights (15% visual weight) ===
    st.markdown(f'<div class="section-title">{"关键洞察" if lang == "中文" else "Key Insights"}</div>', unsafe_allow_html=True)
    
    insights = []
    if score_result['dimensions']['search_performance'] < 70:
        insights.append('⚠️ ' + ('搜索表现是最大短板，平均排名23.8需优化至前15' if lang == '中文' else 'Search performance is the weakest dimension. Average position 23.8 needs to reach top 15.'))
    if score_result['metrics']['avg_ctr'] < 0.02:
        insights.append('⚠️ ' + ('CTR仅1.46%，低于B2B行业基准2-3%，建议优化标题和描述' if lang == '中文' else 'CTR only 1.46%, below B2B benchmark of 2-3%. Optimize titles and descriptions.'))
    if score_result['dimensions']['backlink_authority'] == 0:
        insights.append('🔗 ' + ('外链权威维度未接入（预留15%权重），接入后评分预计提升8-12分' if lang == '中文' else 'Backlink authority not connected (15% weight reserved). Score could improve 8-12 pts after integration.'))
    
    for insight in insights:
        st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

# ============================================================
# 页面2：SEO Health Model
# ============================================================
elif page == '🎯 SEO Health Model':
    st.markdown(f'<div class="page-title">{"SEO 健康度模型" if lang == "中文" else "SEO Health Model"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"三维九指标评分体系 · 外链权威预留可扩展" if lang == "中文" else "3-Dimension 9-Indicator Scoring System · Backlink Authority Reserved"}</div>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score(data)
    
    # Score Hero
    score_color = COLORS['warning'] if score_result['grade'] == 'C' else COLORS['success'] if score_result['grade'] in ['A','B'] else COLORS['danger']
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:16px; padding:40px; text-align:center;">
            <div class="score-label">OVERALL SCORE</div>
            <div class="score-number" style="color:{score_color};">{score_result['final_score']}</div>
            <div class="score-grade" style="color:{score_color};">{score_result['grade']} · {score_result['grade_text']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Radar Chart
        dims = score_result['dimensions']
        categories = ['Search\nPerformance', 'Content\nEffectiveness', 'Technical\nExperience', 'Backlink\nAuthority']
        values = [dims['search_performance'], dims['content_effectiveness'], dims['technical_experience'], dims['backlink_authority']]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(37,99,235,0.15)',
            line=dict(color='#2563EB', width=2),
            marker=dict(size=8, color='#2563EB')
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=12)),
                angularaxis=dict(tickfont=dict(size=13))
            ),
            showlegend=False,
            **{k: v for k, v in CHART_LAYOUT.items() if k not in ['plot_bgcolor']}
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
    
    # Dimension Details
    st.markdown(f'<div class="section-title">{"各维度详细评分" if lang == "中文" else "Dimension Breakdown"}</div>', unsafe_allow_html=True)
    
    # Search Performance
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:12px; padding:20px; margin:12px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:16px; font-weight:600; color:#1F2937;">{"搜索表现 Search Performance" if lang == "中文" else "Search Performance"}</span>
            <span style="font-size:24px; font-weight:700; color:#2563EB;">{dims['search_performance']}</span>
        </div>
        <div style="font-size:13px; color:#6B7280; margin-top:4px;">{"权重 40% · 月均点击149次 · CTR 1.46% · 排名23.8" if lang == "中文" else "Weight 40% · Monthly clicks 149 · CTR 1.46% · Position 23.8"}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Content Effectiveness
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:12px; padding:20px; margin:12px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:16px; font-weight:600; color:#1F2937;">{"内容效果 Content Effectiveness" if lang == "中文" else "Content Effectiveness"}</span>
            <span style="font-size:24px; font-weight:700; color:#10B981;">{dims['content_effectiveness']}</span>
        </div>
        <div style="font-size:13px; color:#6B7280; margin-top:4px;">{"权重 30% · 覆盖2519关键词 · 活跃页77% · 57国有点击" if lang == "中文" else "Weight 30% · 2519 keywords · 77% active pages · 57 countries with clicks"}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Technical Experience
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:12px; padding:20px; margin:12px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:16px; font-weight:600; color:#1F2937;">{"技术体验 Technical Experience" if lang == "中文" else "Technical Experience"}</span>
            <span style="font-size:24px; font-weight:700; color:#10B981;">{dims['technical_experience']}</span>
        </div>
        <div style="font-size:13px; color:#6B7280; margin-top:4px;">{"权重 15% · 三设备覆盖 · 移动端占比12.96% · CTR一致性良好" if lang == "中文" else "Weight 15% · 3 devices · Mobile 12.96% · Good CTR consistency"}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Backlink Authority (Reserved)
    st.markdown(f"""
    <div style="background:#F9FAFB; border:1px dashed #D1D5DB; border-radius:12px; padding:20px; margin:12px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:16px; font-weight:600; color:#9CA3AF;">🔒 {"外链权威 Backlink Authority" if lang == "中文" else "Backlink Authority"}</span>
            <span style="font-size:24px; font-weight:700; color:#9CA3AF;">N/A</span>
        </div>
        <div style="font-size:13px; color:#9CA3AF; margin-top:4px;">{"权重 15% · 预留接口 · 待接入 Ahrefs/Moz API" if lang == "中文" else "Weight 15% · Reserved · Pending Ahrefs/Moz API integration"}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 页面3：Search Intelligence
# ============================================================
elif page == '📈 Search Intelligence':
    st.markdown(f'<div class="page-title">{"搜索表现洞察" if lang == "中文" else "Search Intelligence"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"点击、展示、CTR 与排名的时间序列分析" if lang == "中文" else "Time-series analysis of clicks, impressions, CTR and position"}</div>', unsafe_allow_html=True)
    
    if 'by_date' in data:
        df_date = data['by_date'].sort_values('data_date')
        
        # Date range filter
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            date_range = st.date_input(
                "Date Range" if lang == 'English' else "日期范围",
                value=(df_date['data_date'].min(), df_date['data_date'].max()),
                key='search_date_range'
            )
        with col_f2:
            granularity = st.selectbox(
                "Granularity" if lang == 'English' else "时间粒度",
                ['Daily' if lang == 'English' else '日', 'Weekly' if lang == 'English' else '周', 'Monthly' if lang == 'English' else '月'],
                key='search_granularity'
            )
        
        # Filter data
        if len(date_range) == 2:
            mask = (df_date['data_date'] >= pd.Timestamp(date_range[0])) & (df_date['data_date'] <= pd.Timestamp(date_range[1]))
            df_filtered = df_date[mask].copy()
        else:
            df_filtered = df_date.copy()
        
        # Resample based on granularity
        df_plot = df_filtered.set_index('data_date')
        if granularity in ['Weekly', '周']:
            df_plot = df_plot.resample('W').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()
        elif granularity in ['Monthly', '月']:
            df_plot = df_plot.resample('M').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()
        else:
            df_plot = df_plot.reset_index()
        
        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
        
        # Stock-style chart: Clicks + Impressions with MA
        st.markdown(f'<div class="section-title">{"点击 & 展示趋势（含移动平均线）" if lang == "中文" else "Clicks & Impressions Trend (with Moving Average)"}</div>', unsafe_allow_html=True)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                           row_heights=[0.7, 0.3])
        
        # Impressions as area (volume-like)
        fig.add_trace(go.Scatter(
            x=df_plot['data_date'], y=df_plot['impressions'],
            fill='tozeroy', fillcolor='rgba(37,99,235,0.08)',
            line=dict(color='#93C5FD', width=1),
            name='Impressions'
        ), row=2, col=1)
        
        # Clicks as main line
        fig.add_trace(go.Scatter(
            x=df_plot['data_date'], y=df_plot['clicks'],
            line=dict(color='#2563EB', width=2),
            name='Clicks'
        ), row=1, col=1)
        
        # 7-day MA
        if len(df_plot) >= 7:
            df_plot['clicks_ma7'] = df_plot['clicks'].rolling(7, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=df_plot['data_date'], y=df_plot['clicks_ma7'],
                line=dict(color='#F59E0B', width=2, dash='dot'),
                name='7-period MA'
            ), row=1, col=1)
        
        # 30-day MA
        if len(df_plot) >= 30:
            df_plot['clicks_ma30'] = df_plot['clicks'].rolling(30, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=df_plot['data_date'], y=df_plot['clicks_ma30'],
                line=dict(color='#EF4444', width=2, dash='dash'),
                name='30-period MA'
            ), row=1, col=1)
        
        fig.update_layout(
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=13)),
            xaxis2=dict(title=dict(text='Date', font=dict(size=14))),
            yaxis=dict(title=dict(text='Clicks', font=dict(size=14)), tickfont=dict(size=12), gridcolor='#F3F4F6'),
            yaxis2=dict(title=dict(text='Impressions', font=dict(size=14)), tickfont=dict(size=12), gridcolor='#F3F4F6'),
            **CHART_LAYOUT
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # CTR & Position dual axis
        st.markdown(f'<div class="section-title">{"CTR & 排名趋势" if lang == "中文" else "CTR & Position Trend"}</div>', unsafe_allow_html=True)
        
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig2.add_trace(go.Scatter(
            x=df_plot['data_date'], y=df_plot['ctr'] * 100,
            line=dict(color='#10B981', width=2),
            name='CTR %'
        ), secondary_y=False)
        
        fig2.add_trace(go.Scatter(
            x=df_plot['data_date'], y=df_plot['position'],
            line=dict(color='#8B5CF6', width=2),
            name='Position'
        ), secondary_y=True)
        
        fig2.update_layout(
            height=350,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=13)),
            yaxis=dict(title=dict(text='CTR %', font=dict(size=14)), tickfont=dict(size=12), gridcolor='#F3F4F6'),
            yaxis2=dict(title=dict(text='Position', font=dict(size=14)), tickfont=dict(size=12), autorange='reversed'),
            **CHART_LAYOUT
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("未找到日期维度数据" if lang == '中文' else "Date dimension data not found")

# ============================================================
# 页面4：Keyword Opportunities
# ============================================================
elif page == '🔍 Keyword Opportunities':
    st.markdown(f'<div class="page-title">{"关键词机会分析" if lang == "中文" else "Keyword Opportunities"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"发现高潜力关键词，识别快速排名提升机会" if lang == "中文" else "Discover high-potential keywords and quick-win ranking opportunities"}</div>', unsafe_allow_html=True)
    
    if 'by_query' in data:
        df_query = data['by_query'].copy()
        
        # Quick wins: position 8-20, high impressions
        st.markdown(f'<div class="section-title">{"🎯 快速提升机会（排名8-20，高展示）" if lang == "中文" else "🎯 Quick Wins (Position 8-20, High Impressions)"}</div>', unsafe_allow_html=True)
        
        quick_wins = df_query[(df_query['position'] >= 8) & (df_query['position'] <= 20) & (df_query['impressions'] >= 50)].sort_values('impressions', ascending=False).head(20)
        
        if len(quick_wins) > 0:
            fig_qw = go.Figure()
            fig_qw.add_trace(go.Scatter(
                x=quick_wins['position'],
                y=quick_wins['impressions'],
                mode='markers+text',
                marker=dict(size=quick_wins['clicks'].clip(lower=3) * 3, color='#2563EB', opacity=0.7),
                text=quick_wins['query'].str[:20],
                textposition='top center',
                textfont=dict(size=11),
                hovertemplate='<b>%{text}</b><br>Position: %{x:.1f}<br>Impressions: %{y}<br>Clicks: %{marker.size:.0f}<extra></extra>'
            ))
            fig_qw.update_layout(
                height=400,
                xaxis=dict(title=dict(text='Position', font=dict(size=14)), tickfont=dict(size=12), autorange='reversed', gridcolor='#F3F4F6'),
                yaxis=dict(title=dict(text='Impressions', font=dict(size=14)), tickfont=dict(size=12), gridcolor='#F3F4F6'),
                **CHART_LAYOUT
            )
            st.plotly_chart(fig_qw, use_container_width=True)
            
            st.markdown(f'<div class="section-title">{"📋 关键词明细" if lang == "中文" else "📋 Keyword Details"}</div>', unsafe_allow_html=True)
            display_df = quick_wins[['query', 'clicks', 'impressions', 'ctr', 'position']].copy()
            display_df['ctr'] = (display_df['ctr'] * 100).round(2).astype(str) + '%'
            display_df['position'] = display_df['position'].round(1)
            display_df.columns = ['Keyword', 'Clicks', 'Impressions', 'CTR', 'Position']
            st.dataframe(display_df.reset_index(drop=True), use_container_width=True, height=400)
        else:
            st.info("未找到符合条件的快速提升关键词" if lang == '中文' else "No quick-win keywords found")
        
        # Keyword distribution by position
        st.markdown(f'<div class="section-title">{"📊 关键词排名分布" if lang == "中文" else "📊 Keyword Position Distribution"}</div>', unsafe_allow_html=True)
        
        bins = [0, 3, 10, 20, 50, 100]
        labels = ['Top 3', '4-10', '11-20', '21-50', '50+']
        df_query['pos_group'] = pd.cut(df_query['position'], bins=bins, labels=labels)
        pos_dist = df_query.groupby('pos_group', observed=True).size().reset_index(name='count')
        
        fig_dist = go.Figure(go.Bar(
            x=pos_dist['pos_group'].astype(str),
            y=pos_dist['count'],
            marker_color=['#10B981', '#2563EB', '#F59E0B', '#F97316', '#EF4444'],
            text=pos_dist['count'],
            textposition='outside',
            textfont=dict(size=14)
        ))
        fig_dist.update_layout(
            height=350,
            xaxis=dict(title=dict(text='Position Range', font=dict(size=14)), tickfont=dict(size=13)),
            yaxis=dict(title=dict(text='Keywords Count', font=dict(size=14)), tickfont=dict(size=12), gridcolor='#F3F4F6'),
            **CHART_LAYOUT
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("请确保 data/ 文件夹中包含 cleaned_by_query.csv" if lang == '中文' else "Please ensure cleaned_by_query.csv is in the data/ folder")

# ============================================================
# 页面5：Content Intelligence
# ============================================================
elif page == '📄 Content Intelligence':
    st.markdown(f'<div class="page-title">{"内容效果分析" if lang == "中文" else "Content Intelligence"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"页面表现评估与内容优化机会识别" if lang == "中文" else "Page performance evaluation and content optimization opportunities"}</div>', unsafe_allow_html=True)
    
    if 'by_page' in data:
        df_page = data['by_page'].copy()
        
        # Top pages
        st.markdown(f'<div class="section-title">{"🏆 Top 20 页面" if lang == "中文" else "🏆 Top 20 Pages"}</div>', unsafe_allow_html=True)
        
        top_pages = df_page.nlargest(20, 'clicks')
        
        fig_pages = go.Figure(go.Bar(
            y=top_pages['page'].str.replace('https?://[^/]+', '', regex=True).str[:40],
            x=top_pages['clicks'],
            orientation='h',
            marker_color='#2563EB',
            text=top_pages['clicks'],
            textposition='outside',
            textfont=dict(size=12)
        ))
        fig_pages.update_layout(
            height=600,
            xaxis=dict(title=dict(text='Clicks', font=dict(size=14)), tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12), autorange='reversed'),
            **CHART_LAYOUT
        )
        st.plotly_chart(fig_pages, use_container_width=True)
        
        # Opportunity Matrix
        st.markdown(f'<div class="section-title">{"🎯 页面机会矩阵（高展示低点击 = 优化机会）" if lang == "中文" else "🎯 Page Opportunity Matrix (High Impressions + Low Clicks = Opportunity)"}</div>', unsafe_allow_html=True)
        
        df_opp = df_page[(df_page['impressions'] >= 100)].copy()
        if len(df_opp) > 0:
            df_opp['ctr_pct'] = df_opp['ctr'] * 100
            
            fig_matrix = go.Figure()
            fig_matrix.add_trace(go.Scatter(
                x=df_opp['impressions'],
                y=df_opp['ctr_pct'],
                mode='markers',
                marker=dict(
                    size=df_opp['clicks'].clip(lower=2) * 2,
                    color=df_opp['position'],
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title=dict(text='Position', font=dict(size=12)))
                ),
                text=df_opp['page'].str.replace('https?://[^/]+', '', regex=True).str[:30],
                hovertemplate='<b>%{text}</b><br>Impressions: %{x}<br>CTR: %{y:.2f}%<extra></extra>'
            ))
            
            # Add opportunity zone
            fig_matrix.add_hrect(y0=0, y1=1, fillcolor='rgba(239,68,68,0.05)', line_width=0)
            fig_matrix.add_annotation(x=0.8, y=0.5, xref='paper', text='⚠️ Low CTR Zone', showarrow=False, font=dict(size=13, color='#EF4444'))
            
            fig_matrix.update_layout(
                height=450,
                xaxis=dict(title=dict(text='Impressions', font=dict(size=14)), tickfont=dict(size=12), type='log', gridcolor='#F3F4F6'),
                yaxis=dict(title=dict(text='CTR %', font=dict(size=14)), tickfont=dict(size=12), gridcolor='#F3F4F6'),
                **CHART_LAYOUT
            )
            st.plotly_chart(fig_matrix, use_container_width=True)
    else:
        st.info("请确保 data/ 文件夹中包含 cleaned_by_page.csv" if lang == '中文' else "Please ensure cleaned_by_page.csv is in the data/ folder")

# ============================================================
# 页面6：Market Intelligence (World Map)
# ============================================================
elif page == '🌎 Market Intelligence':
    st.markdown(f'<div class="page-title">{"市场地理分布" if lang == "中文" else "Market Intelligence"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"全球搜索流量地理分布与区域市场洞察" if lang == "中文" else "Global search traffic distribution and regional market insights"}</div>', unsafe_allow_html=True)
    
    if 'by_country' in data:
        df_country = data['by_country'].copy()
        
        # Aggregate by country
        country_agg = df_country.groupby('country').agg({
            'clicks': 'sum', 'impressions': 'sum'
        }).reset_index()
        country_agg['ctr'] = country_agg['clicks'] / country_agg['impressions'].clip(lower=1) * 100
        country_agg['country_upper'] = country_agg['country'].str.upper()
        
        # World Map with log scale
        st.markdown(f'<div class="section-title">{"🗺️ 全球点击分布热力图" if lang == "中文" else "🗺️ Global Click Distribution Heatmap"}</div>', unsafe_allow_html=True)
        
        country_with_clicks = country_agg[country_agg['clicks'] > 0].copy()
        country_with_clicks['clicks_log'] = np.log10(country_with_clicks['clicks'].clip(lower=1))
        
        fig_map = go.Figure(go.Choropleth(
            locations=country_with_clicks['country_upper'],
            z=country_with_clicks['clicks_log'],
            locationmode='ISO-3',
            colorscale=[
                [0, '#EFF6FF'],
                [0.25, '#BFDBFE'],
                [0.5, '#60A5FA'],
                [0.75, '#2563EB'],
                [1, '#1E3A8A']
            ],
            colorbar=dict(
                title=dict(text='Clicks (log)', font=dict(size=13)),
                tickvals=[0, 0.5, 1, 1.5, 2, 2.5, 3],
                ticktext=['1', '3', '10', '30', '100', '300', '1000'],
                tickfont=dict(size=12)
            ),
            hovertemplate='<b>%{location}</b><br>Clicks: %{customdata}<extra></extra>',
            customdata=country_with_clicks['clicks']
        ))
        
        fig_map.update_layout(
            height=500,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor='#D1D5DB',
                projection_type='natural earth',
                bgcolor='rgba(0,0,0,0)',
                landcolor='#F3F4F6',
                showlakes=False
            ),
            **CHART_LAYOUT
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Top countries table
        st.markdown(f'<div class="section-title">{"🏆 Top 15 国家/地区" if lang == "中文" else "🏆 Top 15 Countries/Regions"}</div>', unsafe_allow_html=True)
        
        top_countries = country_agg.nlargest(15, 'clicks')[['country_upper', 'clicks', 'impressions', 'ctr']].copy()
        top_countries['ctr'] = top_countries['ctr'].round(2).astype(str) + '%'
        top_countries.columns = ['Country', 'Clicks', 'Impressions', 'CTR']
        st.dataframe(top_countries.reset_index(drop=True), use_container_width=True)
    else:
        st.info("未找到国家维度数据" if lang == '中文' else "Country dimension data not found")

# ============================================================
# 页面7：User Experience Signals
# ============================================================
elif page == '📱 User Experience Signals':
    st.markdown(f'<div class="page-title">{"用户体验信号" if lang == "中文" else "User Experience Signals"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"跨设备搜索行为分析与移动端体验评估" if lang == "中文" else "Cross-device search behavior analysis and mobile experience assessment"}</div>', unsafe_allow_html=True)
    
    if 'by_device' in data:
        df_device = data['by_device'].copy()
        
        # Aggregate
        device_agg = df_device.groupby('device').agg({
            'clicks': 'sum', 'impressions': 'sum'
        }).reset_index()
        device_agg['ctr'] = device_agg['clicks'] / device_agg['impressions'].clip(lower=1) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'<div class="section-title">{"点击占比" if lang == "中文" else "Click Share"}</div>', unsafe_allow_html=True)
            
            fig_pie = go.Figure(go.Pie(
                labels=device_agg['device'],
                values=device_agg['clicks'],
                hole=0.5,
                marker=dict(colors=['#2563EB', '#10B981', '#F59E0B']),
                textinfo='label+percent',
                textfont=dict(size=14)
            ))
            fig_pie.update_layout(height=350, showlegend=False, **CHART_LAYOUT)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown(f'<div class="section-title">{"各设备 CTR 对比" if lang == "中文" else "CTR by Device"}</div>', unsafe_allow_html=True)
            
            fig_bar = go.Figure(go.Bar(
                x=device_agg['device'],
                y=device_agg['ctr'],
                marker_color=['#2563EB', '#10B981', '#F59E0B'],
                text=device_agg['ctr'].round(2).astype(str) + '%',
                textposition='outside',
                textfont=dict(size=14)
            ))
            fig_bar.update_layout(
                height=350,
                xaxis=dict(tickfont=dict(size=14)),
                yaxis=dict(title=dict(text='CTR %', font=dict(size=14)), tickfont=dict(size=12), gridcolor='#F3F4F6'),
                **CHART_LAYOUT
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Device trend over time
        st.markdown(f'<div class="section-title">{"📈 设备趋势变化" if lang == "中文" else "📈 Device Trend Over Time"}</div>', unsafe_allow_html=True)
        
        if 'data_date' in df_device.columns:
            device_trend = df_device.groupby(['data_date', 'device']).agg({'clicks': 'sum'}).reset_index()
            
            fig_trend = go.Figure()
            colors = {'DESKTOP': '#2563EB', 'MOBILE': '#10B981', 'TABLET': '#F59E0B'}
            for device in device_trend['device'].unique():
                d = device_trend[device_trend['device'] == device]
                fig_trend.add_trace(go.Scatter(
                    x=d['data_date'], y=d['clicks'],
                    name=device, line=dict(color=colors.get(device, '#6B7280'), width=2)
                ))
            
            fig_trend.update_layout(
                height=350,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=13)),
                xaxis=dict(tickfont=dict(size=12)),

