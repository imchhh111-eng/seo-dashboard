
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# ============================================================
# 全局配置
# ============================================================
st.set_page_config(
    page_title="B2B SEO Health Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局样式 - 统一蓝色主色调 + 大字体
st.markdown("""
<style>
    /* 全局字体放大 */
    html, body, [class*="css"] {
        font-size: 16px;
    }
    /* 侧边栏标题 */
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a56db;
        padding: 1rem 0;
        border-bottom: 2px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    /* 指标卡片 */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a56db;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #6b7280;
        font-weight: 500;
    }
    /* 评分圆环 */
    .score-ring {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        margin: 0 auto;
        border: 8px solid;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 800;
    }
    .score-grade {
        font-size: 1.2rem;
        font-weight: 600;
    }
    /* 页面标题 */
    .page-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    .page-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    /* 统一图表字体 */
    .js-plotly-plot .plotly .gtitle {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
    """加载所有数据文件"""
    data = {}
    base_path = "data/"
    
    file_mapping = {
        'by_date': 'cleaned_by_date.csv',
        'by_country': 'cleaned_by_country.csv',
        'by_device': 'cleaned_by_device.csv',
        'daily_summary': 'cleaned_daily_summary.csv',
        'by_query': 'cleaned_by_query.csv',
        'by_page': 'cleaned_by_page.csv',
        'date_query': 'cleaned_date_query.csv',
        'date_page': 'cleaned_date_page.csv',
        'query_country': 'cleaned_query_country.csv',
        'query_device': 'cleaned_query_device.csv',
        'page_country': 'cleaned_page_country.csv',
        'page_device': 'cleaned_page_device.csv',
        'query_page': 'cleaned_query_page.csv',
    }
    
    for key, filename in file_mapping.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            data[key] = pd.read_csv(filepath)
        else:
            data[key] = None
    
    return data

data = load_data()

# ============================================================
# SEO 健康度评分模型（三维：40/35/25）
# ============================================================
def calculate_seo_score(data):
    """计算 SEO 健康度评分 - 三维模型"""
    scores = {}
    
    # === 维度1：搜索表现 Search Performance（40%）===
    search_scores = []
    
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        total_months = len(df)
        monthly_clicks_avg = df['clicks'].sum() / max(total_months, 1)
        
        # 1.1 月均点击量得分
        if monthly_clicks_avg >= 500:
            click_score = 100
        elif monthly_clicks_avg >= 200:
            click_score = 80
        elif monthly_clicks_avg >= 100:
            click_score = 60
        elif monthly_clicks_avg >= 50:
            click_score = 40
        else:
            click_score = 20
        search_scores.append(('monthly_clicks', click_score, 0.25))
        
        # 1.2 平均CTR得分
        avg_ctr = df['clicks'].sum() / max(df['impressions'].sum(), 1)
        if avg_ctr >= 0.05:
            ctr_score = 100
        elif avg_ctr >= 0.03:
            ctr_score = 80
        elif avg_ctr >= 0.02:
            ctr_score = 60
        elif avg_ctr >= 0.01:
            ctr_score = 40
        else:
            ctr_score = 20
        search_scores.append(('avg_ctr', ctr_score, 0.25))
        
        # 1.3 平均排名得分
        avg_position = df['position'].mean()
        if avg_position <= 10:
            pos_score = 100
        elif avg_position <= 20:
            pos_score = 80
        elif avg_position <= 30:
            pos_score = 60
        elif avg_position <= 50:
            pos_score = 40
        else:
            pos_score = 20
        search_scores.append(('avg_position', pos_score, 0.25))
    
    if data.get('by_date') is not None:
        df = data['by_date']
        df_sorted = df.sort_values('data_date')
        if len(df_sorted) >= 60:
            recent = df_sorted.tail(30)['clicks'].sum()
            previous = df_sorted.iloc[-60:-30]['clicks'].sum()
            if previous > 0:
                trend = (recent - previous) / previous
            else:
                trend = 0
        else:
            trend = 0
        
        # 1.4 点击趋势得分
        if trend >= 0.1:
            trend_score = 100
        elif trend >= 0:
            trend_score = 70
        elif trend >= -0.2:
            trend_score = 40
        else:
            trend_score = 20
        search_scores.append(('click_trend', trend_score, 0.25))
    
    if search_scores:
        search_total = sum(s * w for _, s, w in search_scores) / sum(w for _, _, w in search_scores)
    else:
        search_total = 50
    scores['search_performance'] = search_total
    
    # === 维度2：内容效果 Content Effectiveness（35%）===
    content_scores = []
    
    if data.get('by_query') is not None:
        df = data['by_query']
        total_keywords = df['query'].nunique()
        
        # 2.1 关键词覆盖度
        if total_keywords >= 1000:
            kw_score = 100
        elif total_keywords >= 500:
            kw_score = 80
        elif total_keywords >= 200:
            kw_score = 60
        elif total_keywords >= 50:
            kw_score = 40
        else:
            kw_score = 20
        content_scores.append(('keyword_coverage', kw_score, 0.35))
    
    if data.get('by_page') is not None:
        df = data['by_page']
        total_pages = df['page'].nunique()
        active_pages = df[df['clicks'] > 0]['page'].nunique()
        active_rate = active_pages / max(total_pages, 1)
        
        # 2.2 活跃页面比例
        if active_rate >= 0.8:
            page_score = 100
        elif active_rate >= 0.6:
            page_score = 80
        elif active_rate >= 0.4:
            page_score = 60
        elif active_rate >= 0.2:
            page_score = 40
        else:
            page_score = 20
        content_scores.append(('active_pages', page_score, 0.35))
    
    if data.get('by_country') is not None:
        df = data['by_country']
        countries_with_clicks = df[df['clicks'] > 0]['country'].nunique()
        
        # 2.3 地理覆盖度
        if countries_with_clicks >= 30:
            geo_score = 100
        elif countries_with_clicks >= 20:
            geo_score = 80
        elif countries_with_clicks >= 10:
            geo_score = 60
        elif countries_with_clicks >= 5:
            geo_score = 40
        else:
            geo_score = 20
        content_scores.append(('geo_coverage', geo_score, 0.30))
    
    if content_scores:
        content_total = sum(s * w for _, s, w in content_scores) / sum(w for _, _, w in content_scores)
    else:
        content_total = 50
    scores['content_effectiveness'] = content_total
    
    # === 维度3：技术体验信号 Technical Experience（25%）===
    tech_scores = []
    
    if data.get('by_device') is not None:
        df = data['by_device']
        devices = df['device'].nunique()
        
        # 3.1 设备覆盖
        if devices >= 3:
            device_score = 100
        elif devices >= 2:
            device_score = 70
        else:
            device_score = 40
        tech_scores.append(('device_coverage', device_score, 0.4))
        
        # 3.2 移动端占比（B2B 特征：桌面为主是正常的）
        total_imp = df['impressions'].sum()
        mobile_imp = df[df['device'] == 'MOBILE']['impressions'].sum()
        mobile_ratio = mobile_imp / max(total_imp, 1)
        
        if 0.15 <= mobile_ratio <= 0.45:
            mobile_score = 100
        elif 0.10 <= mobile_ratio <= 0.50:
            mobile_score = 70
        else:
            mobile_score = 40
        tech_scores.append(('mobile_ratio', mobile_score, 0.3))
        
        # 3.3 设备间CTR一致性
        device_ctrs = df.groupby('device').apply(
            lambda x: x['clicks'].sum() / max(x['impressions'].sum(), 1)
        )
        if len(device_ctrs) > 1:
            ctr_std = device_ctrs.std()
            if ctr_std <= 0.01:
                consistency_score = 100
            elif ctr_std <= 0.02:
                consistency_score = 70
            else:
                consistency_score = 40
        else:
            consistency_score = 50
        tech_scores.append(('ctr_consistency', consistency_score, 0.3))
    
    if tech_scores:
        tech_total = sum(s * w for _, s, w in tech_scores) / sum(w for _, _, w in tech_scores)
    else:
        tech_total = 50
    scores['technical_experience'] = tech_total
    
    # === 综合评分 ===
    final_score = (
        scores['search_performance'] * 0.40 +
        scores['content_effectiveness'] * 0.35 +
        scores['technical_experience'] * 0.25
    )
    
    # 等级判定
    if final_score >= 90:
        grade = 'A'
        grade_label = 'Excellent'
        grade_color = '#059669'
    elif final_score >= 70:
        grade = 'B'
        grade_label = 'Good'
        grade_color = '#2563eb'
    elif final_score >= 50:
        grade = 'C'
        grade_label = 'Average'
        grade_color = '#d97706'
    else:
        grade = 'D'
        grade_label = 'Poor'
        grade_color = '#dc2626'
    
    return {
        'final_score': round(final_score, 1),
        'grade': grade,
        'grade_label': grade_label,
        'grade_color': grade_color,
        'dimensions': scores,
        'search_details': search_scores,
        'content_details': content_scores,
        'tech_details': tech_scores
    }

# ============================================================
# 侧边栏导航
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 SEO Health Intelligence</div>', unsafe_allow_html=True)
    
    # 多语言切换
    lang = st.radio("🌐 Language", ['中文', 'English'], horizontal=True, key="lang_switch")
    
    st.markdown("---")
    
    # 导航菜单
    nav_items = {
        '中文': [
            "📊 总览仪表盘",
            "🎯 SEO 健康度评分",
            "📈 搜索表现趋势",
            "🔍 关键词洞察",
            "📄 页面效果分析",
            "🌍 国家/地区分析",
            "📱 设备分布",
            "🚨 流量异常检测",
            "🚀 优化建议"
        ],
        'English': [
            "📊 Overview Dashboard",
            "🎯 SEO Health Score",
            "📈 Search Trends",
            "🔍 Keyword Insights",
            "📄 Page Analysis",
            "🌍 Country/Region",
            "📱 Device Distribution",
            "🚨 Anomaly Detection",
            "🚀 Recommendations"
        ]
    }
    
    page = st.radio(
        "导航菜单" if lang == '中文' else "Navigation",
        nav_items[lang],
        key="nav_menu"
    )
    
    st.markdown("---")
    
    # 数据范围信息
    if data.get('by_date') is not None:
        date_range = data['by_date']['data_date']
        st.caption(f"📅 {'数据范围' if lang == '中文' else 'Data Range'}: {date_range.min()} → {date_range.max()}")
    
    st.markdown("---")
    st.caption("B2B SEO Health Intelligence v2.0 | Based on GSC Data")

# ============================================================
# 页面1：总览仪表盘
# ============================================================
if page in ["📊 总览仪表盘", "📊 Overview Dashboard"]:
    st.markdown(f'<div class="page-title">{"📊 B2B SEO 总览仪表盘" if lang == "中文" else "📊 B2B SEO Overview Dashboard"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于 Google Search Console 数据的全方位 SEO 健康诊断" if lang == "中文" else "Comprehensive SEO health diagnosis based on GSC data"}</div>', unsafe_allow_html=True)
    
    # 计算评分
    score_result = calculate_seo_score(data)
    
    # 顶部评分 + 核心指标
    col_score, col_metrics = st.columns([1, 3])
    
    with col_score:
        st.markdown(f"""
        <div class="score-ring" style="border-color: {score_result['grade_color']};">
            <div class="score-number" style="color: {score_result['grade_color']};">{score_result['final_score']}</div>
            <div class="score-grade" style="color: {score_result['grade_color']};">Grade {score_result['grade']} · {score_result['grade_label']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_metrics:
        if data.get('daily_summary') is not None:
            df = data['daily_summary']
            total_clicks = df['clicks'].sum()
            total_impressions = df['impressions'].sum()
            avg_ctr = total_clicks / max(total_impressions, 1)
            avg_position = df['position'].mean()
            
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{"总点击" if lang == "中文" else "Total Clicks"}</div>
                    <div class="metric-value">{total_clicks:,}</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{"总展示" if lang == "中文" else "Total Impressions"}</div>
                    <div class="metric-value">{total_impressions:,}</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{"平均CTR" if lang == "中文" else "Avg CTR"}</div>
                    <div class="metric-value">{avg_ctr:.2%}</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{"平均排名" if lang == "中文" else "Avg Position"}</div>
                    <div class="metric-value">{avg_position:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 三维度得分条
    st.markdown(f"### {'📐 各维度得分' if lang == '中文' else '📐 Dimension Scores'}")
    dim_col1, dim_col2, dim_col3 = st.columns(3)
    
    dims = [
        ('search_performance', '搜索表现' if lang == '中文' else 'Search Performance', '40%', dim_col1),
        ('content_effectiveness', '内容效果' if lang == '中文' else 'Content Effectiveness', '35%', dim_col2),
        ('technical_experience', '技术体验' if lang == '中文' else 'Technical Experience', '25%', dim_col3)
    ]
    
    for key, label, weight, col in dims:
        with col:
            score_val = score_result['dimensions'][key]
            st.metric(f"{label} ({weight})", f"{score_val:.1f}/100")
            st.progress(score_val / 100)
    
    st.markdown("---")
    
    # 雷达图
    st.markdown(f"### {'🎯 综合能力雷达图' if lang == '中文' else '🎯 Capability Radar'}")
    
    radar_labels = ['搜索表现', '内容效果', '技术体验'] if lang == '中文' else ['Search', 'Content', 'Technical']
    radar_values = [
        score_result['dimensions']['search_performance'],
        score_result['dimensions']['content_effectiveness'],
        score_result['dimensions']['technical_experience']
    ]
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=radar_values + [radar_values[0]],
        theta=radar_labels + [radar_labels[0]],
        fill='toself',
        fillcolor='rgba(26, 86, 219, 0.15)',
        line=dict(color='#1a56db', width=2.5),
        marker=dict(size=8, color='#1a56db')
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=13)),
            angularaxis=dict(tickfont=dict(size=15))
        ),
        height=400,
        margin=dict(l=60, r=60, t=40, b=40),
        font=dict(size=14)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ============================================================
# 页面2：SEO 健康度评分详情
# ============================================================
elif page in ["🎯 SEO 健康度评分", "🎯 SEO Health Score"]:
    st.markdown(f'<div class="page-title">{"🎯 SEO 健康度评分详情" if lang == "中文" else "🎯 SEO Health Score Details"}</div>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score(data)
    
    # 总分展示
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem; background: linear-gradient(135deg, #eff6ff, #dbeafe); border-radius: 16px; margin-bottom: 2rem;">
        <div style="font-size: 4rem; font-weight: 800; color: {score_result['grade_color']};">{score_result['final_score']}</div>
        <div style="font-size: 1.5rem; color: {score_result['grade_color']}; font-weight: 600;">Grade {score_result['grade']} · {score_result['grade_label']}</div>
        <div style="font-size: 1rem; color: #6b7280; margin-top: 0.5rem;">{"评分模型：搜索表现(40%) + 内容效果(35%) + 技术体验(25%)" if lang == "中文" else "Model: Search(40%) + Content(35%) + Technical(25%)"}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 各维度详细得分
    st.markdown(f"### {'📊 维度1：搜索表现 (权重 40%)' if lang == '中文' else '📊 Dimension 1: Search Performance (40%)'}")
    if score_result['search_details']:
        for name, score, weight in score_result['search_details']:
            label_map = {
                'monthly_clicks': '月均点击量' if lang == '中文' else 'Monthly Clicks',
                'avg_ctr': '平均点击率' if lang == '中文' else 'Average CTR',
                'avg_position': '平均排名' if lang == '中文' else 'Average Position',
                'click_trend': '点击趋势' if lang == '中文' else 'Click Trend'
            }
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(score / 100)
            with col2:
                st.write(f"**{label_map.get(name, name)}**: {score}/100")
    
    st.markdown(f"### {'📊 维度2：内容效果 (权重 35%)' if lang == '中文' else '📊 Dimension 2: Content Effectiveness (35%)'}")
    if score_result['content_details']:
        for name, score, weight in score_result['content_details']:
            label_map = {
                'keyword_coverage': '关键词覆盖度' if lang == '中文' else 'Keyword Coverage',
                'active_pages': '活跃页面比例' if lang == '中文' else 'Active Pages Ratio',
                'geo_coverage': '地理覆盖度' if lang == '中文' else 'Geographic Coverage'
            }
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(score / 100)
            with col2:
                st.write(f"**{label_map.get(name, name)}**: {score}/100")
    
    st.markdown(f"### {'📊 维度3：技术体验 (权重 25%)' if lang == '中文' else '📊 Dimension 3: Technical Experience (25%)'}")
    if score_result['tech_details']:
        for name, score, weight in score_result['tech_details']:
            label_map = {
                'device_coverage': '设备覆盖' if lang == '中文' else 'Device Coverage',
                'mobile_ratio': '移动端占比' if lang == '中文' else 'Mobile Ratio',
                'ctr_consistency': 'CTR一致性' if lang == '中文' else 'CTR Consistency'
            }
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(score / 100)
            with col2:
                st.write(f"**{label_map.get(name, name)}**: {score}/100")
    
    # 外链权威预留说明
    st.markdown("---")
    st.info(f"{'💡 外链权威维度（Backlink Authority）已预留接口，待接入 Ahrefs/Moz API 后可扩展为四维模型。' if lang == '中文' else '💡 Backlink Authority dimension is reserved. Will be available after Ahrefs/Moz API integration.'}")

# ============================================================
# 页面3：搜索表现趋势（股市风格）
# ============================================================
elif page in ["📈 搜索表现趋势", "📈 Search Trends"]:
    st.markdown(f'<div class="page-title">{"📈 搜索表现趋势" if lang == "中文" else "📈 Search Performance Trends"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"股市风格趋势图 — 点击量 + 移动平均线 + 展示量柱状图" if lang == "中文" else "Stock-style chart — Clicks + Moving Average + Impressions Volume"}</div>', unsafe_allow_html=True)
    
    if data.get('by_date') is not None:
        df = data['by_date'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date')
        
        # 日期范围筛选
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input(
                "开始日期" if lang == '中文' else "Start Date",
                value=df['data_date'].min(),
                key="trend_start"
            )
        with col_end:
            end_date = st.date_input(
                "结束日期" if lang == '中文' else "End Date",
                value=df['data_date'].max(),
                key="trend_end"
            )
        
        mask = (df['data_date'] >= pd.to_datetime(start_date)) & (df['data_date'] <= pd.to_datetime(end_date))
        df_filtered = df[mask].copy()
        
        if len(df_filtered) > 0:
            # 计算移动平均线
            df_filtered['MA7'] = df_filtered['clicks'].rolling(window=7, min_periods=1).mean()
            df_filtered['MA30'] = df_filtered['clicks'].rolling(window=30, min_periods=1).mean()
            
            # 股市风格图：上方点击线+MA，下方展示量柱
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                row_heights=[0.7, 0.3],
                subplot_titles=(
                    '点击数 & 移动平均线' if lang == '中文' else 'Clicks & Moving Averages',
                    '展示量 (Volume)' if lang == '中文' else 'Impressions (Volume)'
                )
            )
            
            # 上图：点击数散点 + MA7 + MA30
            fig.add_trace(go.Scatter(
                x=df_filtered['data_date'],
                y=df_filtered['clicks'],
                mode='markers',
                name='Clicks' if lang == 'English' else '每日点击',
                marker=dict(color='#93c5fd', size=4, opacity=0.6),
                hovertemplate='%{x}<br>Clicks: %{y}<extra></extra>'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df_filtered['data_date'],
                y=df_filtered['MA7'],
                mode='lines',
                name='MA7',
                line=dict(color='#1a56db', width=2.5),
                hovertemplate='%{x}<br>MA7: %{y:.1f}<extra></extra>'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df_filtered['data_date'],
                y=df_filtered['MA30'],
                mode='lines',
                name='MA30',
                line=dict(color='#dc2626', width=2, dash='dash'),
                hovertemplate='%{x}<br>MA30: %{y:.1f}<extra></extra>'
            ), row=1, col=1)
            
            # 下图：展示量柱状图（模拟成交量）
            colors = ['#22c55e' if row['clicks'] > 0 else '#ef4444' for _, row in df_filtered.iterrows()]
            fig.add_trace(go.Bar(
                x=df_filtered['data_date'],
                y=df_filtered['impressions'],
                name='Impressions' if lang == 'English' else '展示量',
                marker_color=colors,
                opacity=0.7,
                hovertemplate='%{x}<br>Impressions: %{y:,}<extra></extra>'
            ), row=2, col=1)
            
            fig.update_layout(
                height=650,
                font=dict(size=14),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=13)),
                margin=dict(l=60, r=20, t=80, b=40),
                hovermode='x unified'
            )
            fig.update_xaxes(tickfont=dict(size=12))
            fig.update_yaxes(tickfont=dict(size=12))
            fig.update_yaxes(title_text='Clicks', row=1, col=1, title_font=dict(size=14))
            fig.update_yaxes(title_text='Impressions', row=2, col=1, title_font=dict(size=14))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # CTR & Position 趋势
            st.markdown(f"### {'📉 CTR & 排名趋势' if lang == '中文' else '📉 CTR & Position Trend'}")
            
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            
            df_filtered['ctr_ma7'] = df_filtered['ctr'].rolling(window=7, min_periods=1).mean()
            df_filtered['pos_ma7'] = df_filtered['position'].rolling(window=7, min_periods=1).mean()
            
            fig2.add_trace(go.Scatter(
                x=df_filtered['data_date'],
                y=df_filtered['ctr_ma7'] * 100,
                mode='lines',
                name='CTR (MA7)',
                line=dict(color='#059669', width=2.5),
            ), secondary_y=False)
            
            fig2.add_trace(go.Scatter(
                x=df_filtered['data_date'],
                y=df_filtered['pos_ma7'],
                mode='lines',
                name='Position (MA7)',
                line=dict(color='#d97706', width=2.5),
            ), secondary_y=True)
            
            fig2.update_layout(
                height=400,
                font=dict(size=14),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=13)),
                margin=dict(l=60, r=60, t=40, b=40)
            )
            fig2.update_yaxes(title_text="CTR (%)", secondary_y=False, title_font=dict(size=14))
            fig2.update_yaxes(title_text="Position", autorange="reversed", secondary_y=True, title_font=dict(size=14))
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("所选日期范围内无数据" if lang == '中文' else "No data in selected date range")
    else:
        st.warning("未找到日期维度数据" if lang == '中文' else "Date dimension data not found")


# ============================================================
# 页面4：关键词洞察
# ============================================================
elif page in ["🔍 关键词洞察", "🔍 Keyword Insights"]:
    st.markdown(f'<div class="page-title">{"🔍 关键词洞察" if lang == "中文" else "🔍 Keyword Insights"}</div>', unsafe_allow_html=True)
    
    if data.get('by_query') is not None:
        df = data['by_query'].copy()
        
        # 关键词概览指标
        total_kw = df['query'].nunique()
        kw_with_clicks = df[df['clicks'] > 0]['query'].nunique()
        top_kw = df.nlargest(1, 'clicks')['query'].values[0] if len(df) > 0 else 'N/A'
        
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("总关键词数" if lang == '中文' else "Total Keywords", f"{total_kw:,}")
        with k2:
            st.metric("有点击关键词" if lang == '中文' else "Keywords with Clicks", f"{kw_with_clicks:,}")
        with k3:
            st.metric("最佳关键词" if lang == '中文' else "Top Keyword", top_kw[:30])
        
        st.markdown("---")
        
        # Top 20 关键词表格
        st.markdown(f"### {'🏆 Top 20 关键词' if lang == '中文' else '🏆 Top 20 Keywords'}")
        top20 = df.nlargest(20, 'clicks')[['query', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        top20.index = top20.index + 1
        top20['ctr'] = top20['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
        top20['position'] = top20['position'].apply(lambda x: f"{x:.1f}")
        top20.columns = ['Keyword', 'Clicks', 'Impressions', 'CTR', 'Position']
        st.dataframe(top20, use_container_width=True, height=500)
        
        # 关键词机会矩阵（高展示低点击）
        st.markdown(f"### {'💎 关键词机会矩阵' if lang == '中文' else '💎 Keyword Opportunity Matrix'}")
        st.caption("高展示 + 低CTR = 优化机会" if lang == '中文' else "High impressions + Low CTR = Optimization opportunity")
        
        df_opp = df[(df['impressions'] >= 10) & (df['clicks'] >= 0)].copy()
        if len(df_opp) > 0:
            df_opp['ctr_val'] = df_opp['clicks'] / df_opp['impressions'].clip(lower=1)
            
            fig_opp = px.scatter(
                df_opp,
                x='impressions',
                y='ctr_val',
                size='clicks',
                color='position',
                hover_data=['query'],
                color_continuous_scale='RdYlGn_r',
                labels={
                    'impressions': '展示数' if lang == '中文' else 'Impressions',
                    'ctr_val': 'CTR',
                    'position': '排名' if lang == '中文' else 'Position'
                }
            )
            fig_opp.update_layout(
                height=500,
                font=dict(size=14),
                margin=dict(l=60, r=20, t=40, b=60)
            )
            fig_opp.update_xaxes(tickfont=dict(size=13), title_font=dict(size=15))
            fig_opp.update_yaxes(tickfont=dict(size=13), title_font=dict(size=15))
            st.plotly_chart(fig_opp, use_container_width=True)
    else:
        st.info("请确保 data/ 文件夹中包含 cleaned_by_query.csv" if lang == '中文' else "Please ensure cleaned_by_query.csv is in data/ folder")

# ============================================================
# 页面5：页面效果分析
# ============================================================
elif page in ["📄 页面效果分析", "📄 Page Analysis"]:
    st.markdown(f'<div class="page-title">{"📄 页面效果分析" if lang == "中文" else "📄 Page Performance Analysis"}</div>', unsafe_allow_html=True)
    
    if data.get('by_page') is not None:
        df = data['by_page'].copy()
        
        # 页面概览
        total_pages = df['page'].nunique()
        active_pages = df[df['clicks'] > 0]['page'].nunique()
        active_rate = active_pages / max(total_pages, 1)
        
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("总页面数" if lang == '中文' else "Total Pages", f"{total_pages}")
        with p2:
            st.metric("活跃页面" if lang == '中文' else "Active Pages", f"{active_pages}")
        with p3:
            st.metric("活跃率" if lang == '中文' else "Active Rate", f"{active_rate:.1%}")
        
        st.markdown("---")
        
        # Top 15 页面
        st.markdown(f"### {'🏆 Top 15 页面' if lang == '中文' else '🏆 Top 15 Pages'}")
        top15 = df.nlargest(15, 'clicks')[['page', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        
        fig_pages = px.bar(
            top15,
            x='clicks',
            y='page',
            orientation='h',
            color='ctr',
            color_continuous_scale='Blues',
            labels={'clicks': 'Clicks', 'page': 'Page', 'ctr': 'CTR'}
        )
        fig_pages.update_layout(
            height=600,
            font=dict(size=13),
            yaxis=dict(tickfont=dict(size=11)),
            margin=dict(l=300, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_pages, use_container_width=True)
        
        # 页面机会矩阵
        st.markdown(f"### {'💎 页面优化机会' if lang == '中文' else '💎 Page Optimization Opportunities'}")
        
        high_imp_low_ctr = df[(df['impressions'] >= 50) & (df['clicks'] <= 5)].nlargest(10, 'impressions')
        if len(high_imp_low_ctr) > 0:
            st.caption("高展示但低点击的页面 — 优化 Title/Description 可快速提升流量" if lang == '中文' else "High impression but low click pages — optimize Title/Description for quick wins")
            display_df = high_imp_low_ctr[['page', 'impressions', 'clicks', 'ctr', 'position']].reset_index(drop=True)
            display_df.index = display_df.index + 1
            display_df['ctr'] = display_df['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
            display_df.columns = ['Page URL', 'Impressions', 'Clicks', 'CTR', 'Position']
            st.dataframe(display_df, use_container_width=True)
        else:
            st.success("暂无明显的页面优化机会" if lang == '中文' else "No obvious page optimization opportunities")
    else:
        st.info("请确保 data/ 文件夹中包含 cleaned_by_page.csv" if lang == '中文' else "Please ensure cleaned_by_page.csv is in data/ folder")

# ============================================================
# 页面6：国家/地区分析（世界地图 + 对数色阶）
# ============================================================
elif page in ["🌍 国家/地区分析", "🌍 Country/Region"]:
    st.markdown(f'<div class="page-title">{"🌍 国家/地区分析" if lang == "中文" else "🌍 Country/Region Analysis"}</div>', unsafe_allow_html=True)
    
    if data.get('by_country') is not None:
        df = data['by_country'].copy()
        
        # 汇总数据
        map_data = df.groupby('country').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        }).reset_index()
        
        # 国家代码转大写（Plotly 需要大写 ISO-3）
        map_data['country_upper'] = map_data['country'].str.upper()
        
        # 对数变换（解决数据偏斜）
        map_data['clicks_log'] = np.log1p(map_data['clicks'])
        map_data['impressions_log'] = np.log1p(map_data['impressions'])
        
        # 地图指标选择
        map_metric = st.selectbox(
            "🗺️ 地图展示指标" if lang == '中文' else "🗺️ Map Metric",
            ['clicks', 'impressions', 'ctr', 'position'],
            format_func=lambda x: {
                'clicks': '点击数' if lang == '中文' else 'Clicks',
                'impressions': '展示数' if lang == '中文' else 'Impressions',
                'ctr': '点击率 CTR',
                'position': '平均排名' if lang == '中文' else 'Avg Position'
            }[x],
            key="map_metric_sel"
        )
        
        # 根据指标选择色阶
        if map_metric in ['clicks', 'impressions']:
            color_col = f'{map_metric}_log'
            color_scale = [
                [0, '#f7fbff'], [0.15, '#deebf7'], [0.3, '#c6dbef'],
                [0.45, '#9ecae1'], [0.6, '#6baed6'], [0.75, '#4292c6'],
                [0.85, '#2171b5'], [0.95, '#08519c'], [1.0, '#08306b']
            ]
        elif map_metric == 'ctr':
            color_col = 'ctr'
            color_scale = [
                [0, '#fff5f0'], [0.2, '#fee0d2'], [0.4, '#fcbba1'],
                [0.6, '#fc9272'], [0.8, '#fb6a4a'], [1.0, '#de2d26']
            ]
        else:
            color_col = 'position'
            color_scale = [
                [0, '#006d2c'], [0.2, '#31a354'], [0.4, '#74c476'],
                [0.6, '#fed976'], [0.8, '#fd8d3c'], [1.0, '#e31a1c']
            ]
        
        # 自定义 hover
        map_data['hover_text'] = map_data.apply(
            lambda row: f"{'国家' if lang == '中文' else 'Country'}: {row['country_upper']}<br>"
                        f"{'点击' if lang == '中文' else 'Clicks'}: {int(row['clicks'])}<br>"
                        f"{'展示' if lang == '中文' else 'Impressions'}: {int(row['impressions'])}<br>"
                        f"CTR: {row['ctr']:.2%}<br>"
                        f"{'排名' if lang == '中文' else 'Position'}: {row['position']:.1f}",
            axis=1
        )
        
        # 绘制世界地图
        fig_map = go.Figure(data=go.Choropleth(
            locations=map_data['country_upper'],
            z=map_data[color_col],
            locationmode='ISO-3',
            colorscale=color_scale,
            hovertext=map_data['hover_text'],
            hoverinfo='text',
            marker_line_color='#ffffff',
            marker_line_width=0.5,
            colorbar=dict(
                title=dict(text=map_metric, font=dict(size=14)),
                thickness=15,
                len=0.7,
                tickfont=dict(size=12)
            )
        ))
        
        fig_map.update_layout(
            title=dict(
                text='🌍 全球搜索流量分布' if lang == '中文' else '🌍 Global Search Traffic Distribution',
                font=dict(size=20),
                x=0.5
            ),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor='#d4d4d4',
                projection_type='natural earth',
                showland=True,
                landcolor='#f8f9fa',
                showocean=True,
                oceancolor='#e8f4f8',
                showcountries=True,
                countrycolor='#e0e0e0',
                countrywidth=0.5
            ),
            height=550,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Top 10 国家排行
        st.markdown(f"### {'📊 Top 10 国家/地区' if lang == '中文' else '📊 Top 10 Countries/Regions'}")
        
        top10 = map_data.nlargest(10, 'clicks')[['country_upper', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        top10.index = top10.index + 1
        top10['ctr'] = top10['ctr'].apply(lambda x: f"{x:.2%}")
        top10['position'] = top10['position'].apply(lambda x: f"{x:.1f}")
        top10.columns = ['Country', 'Clicks', 'Impressions', 'CTR', 'Avg Position']
        st.dataframe(top10, use_container_width=True, height=400)
        
        # 区域对比柱状图
        st.markdown(f"### {'📊 Top 10 点击数对比' if lang == '中文' else '📊 Top 10 Clicks Comparison'}")
        top10_bar = map_data.nlargest(10, 'clicks')
        fig_bar = px.bar(
            top10_bar,
            x='country_upper',
            y='clicks',
            color='clicks',
            color_continuous_scale='Blues',
            labels={'country_upper': 'Country', 'clicks': 'Clicks'}
        )
        fig_bar.update_layout(
            height=400,
            font=dict(size=14),
            xaxis=dict(tickfont=dict(size=13)),
            yaxis=dict(tickfont=dict(size=13)),
            margin=dict(l=60, r=20, t=20, b=60)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("未找到国家维度数据" if lang == '中文' else "Country dimension data not found")

# ============================================================
# 页面7：设备分布
# ============================================================
elif page in ["📱 设备分布", "📱 Device Distribution"]:
    st.markdown(f'<div class="page-title">{"📱 设备分布分析" if lang == "中文" else "📱 Device Distribution Analysis"}</div>', unsafe_allow_html=True)
    
    if data.get('by_device') is not None:
        df = data['by_device'].copy()
        
        # 按设备汇总
        device_summary = df.groupby('device').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        }).reset_index()
        
        # 设备占比饼图 + 指标对比
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            st.markdown(f"#### {'点击数占比' if lang == '中文' else 'Clicks Distribution'}")
            fig_pie = px.pie(
                device_summary,
                values='clicks',
                names='device',
                color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'],
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
            fig_pie.update_layout(
                height=400,
                font=dict(size=14),
                legend=dict(font=dict(size=13)),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_bar:
            st.markdown(f"#### {'各设备 CTR 对比' if lang == '中文' else 'CTR by Device'}")
            device_summary['ctr_pct'] = device_summary['clicks'] / device_summary['impressions'].clip(lower=1)
            fig_ctr = px.bar(
                device_summary,
                x='device',
                y='ctr_pct',
                color='device',
                color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'],
                labels={'ctr_pct': 'CTR', 'device': 'Device'}
            )
            fig_ctr.update_layout(
                height=400,
                font=dict(size=14),
                xaxis=dict(tickfont=dict(size=14)),
                yaxis=dict(tickfont=dict(size=13), tickformat='.2%'),
                showlegend=False,
                margin=dict(l=60, r=20, t=20, b=60)
            )
            st.plotly_chart(fig_ctr, use_container_width=True)
        
        # 设备趋势（按月）
        st.markdown(f"### {'📈 设备月度趋势' if lang == '中文' else '📈 Monthly Device Trends'}")
        df['data_date'] = pd.to_datetime(df['data_date'])
        df['month'] = df['data_date'].dt.to_period('M').astype(str)
        
        monthly_device = df.groupby(['month', 'device']).agg({'clicks': 'sum', 'impressions': 'sum'}).reset_index()
        
        fig_trend = px.line(
            monthly_device,
            x='month',
            y='clicks',
            color='device',
            markers=True,
            color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'],
            labels={'month': 'Month', 'clicks': 'Clicks', 'device': 'Device'}
        )
        fig_trend.update_layout(
            height=400,
            font=dict(size=14),
            legend=dict(font=dict(size=13)),
            xaxis=dict(tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=13)),
            margin=dict(l=60, r=20, t=20, b=60)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 设备详细数据表
        st.markdown(f"### {'📋 设备详细数据' if lang == '中文' else '📋 Device Details'}")
        display_device = device_summary.copy()
        display_device['ctr'] = display_device['ctr_pct'].apply(lambda x: f"{x:.2%}")
        display_device['position'] = display_device['position'].apply(lambda x: f"{x:.1f}")
        display_device = display_device[['device', 'clicks', 'impressions', 'ctr', 'position']]
        display_device.columns = ['Device', 'Clicks', 'Impressions', 'CTR', 'Avg Position']
        st.dataframe(display_device, use_container_width=True)
    else:
        st.warning("未找到设备维度数据" if lang == '中文' else "Device dimension data not found")

# ============================================================
# 页面8：流量异常检测
# ============================================================
elif page in ["🚨 流量异常检测", "🚨 Anomaly Detection"]:
    st.markdown(f'<div class="page-title">{"🚨 流量异常检测" if lang == "中文" else "🚨 Traffic Anomaly Detection"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于统计方法自动识别流量异常波动" if lang == "中文" else "Statistical methods to identify traffic anomalies"}</div>', unsafe_allow_html=True)
    
    if data.get('by_date') is not None:
        df = data['by_date'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date')
        
        # 异常检测参数
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            metric_choice = st.selectbox(
                "检测指标" if lang == '中文' else "Detection Metric",
                ['clicks', 'impressions', 'ctr', 'position'],
                format_func=lambda x: {
                    'clicks': '点击数' if lang == '中文' else 'Clicks',
                    'impressions': '展示数' if lang == '中文' else 'Impressions',
                    'ctr': 'CTR',
                    'position': '排名' if lang == '中文' else 'Position'
                }[x],
                key="anomaly_metric"
            )
        with col_param2:
            sensitivity = st.slider(
                "灵敏度 (σ)" if lang == '中文' else "Sensitivity (σ)",
                min_value=1.0, max_value=3.0, value=2.0, step=0.5,
                key="anomaly_sensitivity"
            )
        
        # Z-Score 异常检测
        df['rolling_mean'] = df[metric_choice].rolling(window=14, min_periods=3).mean()
        df['rolling_std'] = df[metric_choice].rolling(window=14, min_periods=3).std()
        df['z_score'] = (df[metric_choice] - df['rolling_mean']) / df['rolling_std'].clip(lower=0.001)
        df['is_anomaly'] = df['z_score'].abs() > sensitivity
        
        anomaly_count = df['is_anomaly'].sum()
        
        # 异常统计
        st.metric(
            "检测到的异常点" if lang == '中文' else "Anomalies Detected",
            f"{anomaly_count} {'个' if lang == '中文' else ' points'}"
        )
        
        # 异常可视化
        fig_anomaly = go.Figure()
        
        # 正常数据
        normal = df[~df['is_anomaly']]
        fig_anomaly.add_trace(go.Scatter(
            x=normal['data_date'],
            y=normal[metric_choice],
            mode='lines',
            name='Normal' if lang == 'English' else '正常',
            line=dict(color='#1a56db', width=1.5),
            opacity=0.7
        ))
        
        # 异常点
        anomalies = df[df['is_anomaly']]
        fig_anomaly.add_trace(go.Scatter(
            x=anomalies['data_date'],
            y=anomalies[metric_choice],
            mode='markers',
            name='Anomaly' if lang == 'English' else '异常',
            marker=dict(color='#dc2626', size=10, symbol='x', line=dict(width=2)),
        ))
        
        # 置信区间
        fig_anomaly.add_trace(go.Scatter(
            x=df['data_date'],
            y=df['rolling_mean'] + sensitivity * df['rolling_std'],
            mode='lines',
            name=f'Upper Bound (+{sensitivity}σ)',
            line=dict(color='#9ca3af', width=1, dash='dash'),
        ))
        fig_anomaly.add_trace(go.Scatter(
            x=df['data_date'],
            y=(df['rolling_mean'] - sensitivity * df['rolling_std']).clip(lower=0),
            mode='lines',
            name=f'Lower Bound (-{sensitivity}σ)',
            line=dict(color='#9ca3af', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(156, 163, 175, 0.1)'
        ))
        
        fig_anomaly.update_layout(
            height=500,
            font=dict(size=14),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=13)),
            xaxis=dict(tickfont=dict(size=12)),
            
              yaxis=dict(tickfont=dict(size=13), title=dict(text=metric_choice, font=dict(size=14))),
            margin=dict(l=60, r=20, t=40, b=40)
        )
        
        st.plotly_chart(fig_anomaly, use_container_width=True)
        
        # 异常事件列表
        if anomaly_count > 0:
            st.markdown(f"### {'📋 异常事件明细' if lang == '中文' else '📋 Anomaly Details'}")
            anomaly_list = anomalies[['data_date', metric_choice, 'z_score']].copy()
            anomaly_list['data_date'] = anomaly_list['data_date'].dt.strftime('%Y-%m-%d')
            anomaly_list['z_score'] = anomaly_list['z_score'].apply(lambda x: f"{x:.2f}")
            anomaly_list['type'] = anomaly_list['z_score'].apply(
                lambda x: ('📈 正向异常' if lang == '中文' else '📈 Positive') if float(x) > 0 else ('📉 负向异常' if lang == '中文' else '📉 Negative')
            )
            anomaly_list.columns = [
                'Date' if lang == 'English' else '日期',
                metric_choice,
                'Z-Score',
                'Type' if lang == 'English' else '类型'
            ]
            st.dataframe(anomaly_list.reset_index(drop=True), use_container_width=True)
    else:
        st.warning("未找到日期维度数据" if lang == '中文' else "Date dimension data not found")

# ============================================================
# 页面9：优化建议
# ============================================================
elif page in ["🚀 优化建议", "🚀 Recommendations"]:
    st.markdown(f'<div class="page-title">{"🚀 SEO 优化建议" if lang == "中文" else "🚀 SEO Recommendations"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于数据分析自动生成的优化优先级建议" if lang == "中文" else "Data-driven optimization recommendations"}</div>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score(data)
    
    # 优化优先级
    recommendations = []
    
    # 基于评分维度生成建议
    dims_scores = score_result['dimensions']
    
    # 搜索表现建议
    if dims_scores['search_performance'] < 70:
        recommendations.append({
            'priority': 'P0',
            'category': '搜索表现' if lang == '中文' else 'Search Performance',
            'issue': '平均排名偏低（23.8），大量关键词未进入前10' if lang == '中文' else 'Average position too low (23.8), many keywords not in top 10',
            'action': '聚焦排名11-20的关键词，优化对应页面的内容深度和内链结构' if lang == '中文' else 'Focus on keywords ranked 11-20, optimize content depth and internal linking',
            'impact': '⬆️ 高' if lang == '中文' else '⬆️ High'
        })
    
    if dims_scores['search_performance'] < 60:
        recommendations.append({
            'priority': 'P0',
            'category': '点击率' if lang == '中文' else 'CTR',
            'issue': 'CTR仅1.46%，远低于行业平均2-3%' if lang == '中文' else 'CTR only 1.46%, well below industry average 2-3%',
            'action': '优化 Title 和 Meta Description，加入数字、年份、行动号召词' if lang == '中文' else 'Optimize Title & Meta Description with numbers, dates, and CTAs',
            'impact': '⬆️ 高' if lang == '中文' else '⬆️ High'
        })
    
    # 内容效果建议
    if dims_scores['content_effectiveness'] < 80:
        recommendations.append({
            'priority': 'P1',
            'category': '内容效果' if lang == '中文' else 'Content',
            'issue': '活跃页面比例有提升空间' if lang == '中文' else 'Active page ratio can be improved',
            'action': '识别零点击页面，更新内容或合并低质量页面' if lang == '中文' else 'Identify zero-click pages, update content or consolidate low-quality pages',
            'impact': '⬆️ 中' if lang == '中文' else '⬆️ Medium'
        })
    
    # 技术体验建议
    if dims_scores['technical_experience'] < 80:
        recommendations.append({
            'priority': 'P1',
            'category': '技术体验' if lang == '中文' else 'Technical',
            'issue': '移动端体验可能需要优化' if lang == '中文' else 'Mobile experience may need optimization',
            'action': '检查移动端页面加载速度和Core Web Vitals指标' if lang == '中文' else 'Check mobile page speed and Core Web Vitals',
            'impact': '⬆️ 中' if lang == '中文' else '⬆️ Medium'
        })
    
    # 通用建议
    recommendations.append({
        'priority': 'P2',
        'category': '外链建设' if lang == '中文' else 'Backlinks',
        'issue': '当前未接入外链数据，无法评估域名权威度' if lang == '中文' else 'No backlink data available, cannot assess domain authority',
        'action': '接入 Ahrefs/Moz API，建立外链监控体系' if lang == '中文' else 'Integrate Ahrefs/Moz API for backlink monitoring',
        'impact': '⬆️ 中' if lang == '中文' else '⬆️ Medium'
    })
    
    recommendations.append({
        'priority': 'P2',
        'category': '趋势监控' if lang == '中文' else 'Trend Monitoring',
        'issue': '近期点击量呈下降趋势' if lang == '中文' else 'Recent click trend is declining',
        'action': '排查是否有页面被降权、索引丢失或算法更新影响' if lang == '中文' else 'Investigate potential deindexing, penalties, or algorithm updates',
        'impact': '⬆️ 高' if lang == '中文' else '⬆️ High'
    })
    
    # 展示建议表格
    if recommendations:
        st.markdown(f"### {'📋 优化行动清单' if lang == '中文' else '📋 Action Items'}")
        
        for i, rec in enumerate(recommendations):
            priority_color = {'P0': '#dc2626', 'P1': '#d97706', 'P2': '#2563eb'}
            color = priority_color.get(rec['priority'], '#6b7280')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 1rem 1.5rem; margin: 0.8rem 0; background: #f9fafb; border-radius: 0 8px 8px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: {color}; font-size: 0.9rem;">{rec['priority']}</span>
                    <span style="font-size: 0.85rem; color: #6b7280;">{rec['category']}</span>
                    <span style="font-size: 0.85rem;">{rec['impact']}</span>
                </div>
                <div style="margin-top: 0.5rem; font-size: 1rem; color: #111827; font-weight: 600;">{rec['issue']}</div>
                <div style="margin-top: 0.3rem; font-size: 0.95rem; color: #4b5563;">💡 {rec['action']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 评分提升路径
    st.markdown("---")
    st.markdown(f"### {'📈 评分提升路径' if lang == '中文' else '📈 Score Improvement Path'}")
    
    current_score = score_result['final_score']
    
    st.markdown(f"""
    <div style="background: #eff6ff; padding: 1.5rem; border-radius: 12px;">
        <div style="font-size: 1.1rem; font-weight: 600; color: #1a56db; margin-bottom: 1rem;">
            {"当前评分" if lang == "中文" else "Current Score"}: {current_score} → {"目标" if lang == "中文" else "Target"}: 75+
        </div>
        <div style="font-size: 0.95rem; color: #374151; line-height: 1.8;">
            {"• 短期（1-2周）：优化 Title/Description → CTR 提升至 2%+ → 预计 +5 分" if lang == "中文" else "• Short-term (1-2 weeks): Optimize Title/Description → CTR to 2%+ → Est. +5 pts"}<br>
            {"• 中期（1-2月）：关键词排名优化 → 平均排名进入前15 → 预计 +8 分" if lang == "中文" else "• Mid-term (1-2 months): Keyword ranking optimization → Avg position to top 15 → Est. +8 pts"}<br>
            {"• 长期（3-6月）：内容体系建设 + 外链积累 → 综合提升 → 预计 +12 分" if lang == "中文" else "• Long-term (3-6 months): Content system + backlink building → Est. +12 pts"}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 外链权威预留
    st.markdown("---")
    st.info(f"{'🔗 外链权威维度（Backlink Authority, 预留权重15%）将在接入第三方 API 后启用，届时评分模型将升级为四维体系。' if lang == '中文' else '🔗 Backlink Authority dimension (reserved 15% weight) will be enabled after third-party API integration.'}")

