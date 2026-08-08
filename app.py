
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
st.set_page_config(page_title="SEO Health Intelligence", page_icon="📊", layout="wide")

# 统一图表布局
CHART_LAYOUT = dict(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#FFFFFF',
    font=dict(family='Inter, -apple-system, sans-serif', size=13),
    margin=dict(l=40, r=40, t=50, b=40)
)

# 品牌色系
COLORS = {
    'primary': '#2563EB',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'gray': '#6B7280',
    'light_gray': '#F9FAFB',
    'border': '#E5E7EB'
}

# ============================================================
# 全局 CSS
# ============================================================
st.markdown("""
<style>
/* 全局字体 */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 侧边栏 */
[data-testid="stSidebar"] {
    background: #FAFBFC;
    border-right: 1px solid #E5E7EB;
}
[data-testid="stSidebar"] .block-container { padding-top: 2rem; }

/* 页面标题 */
.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}
.page-subtitle {
    font-size: 15px;
    color: #6B7280;
    margin-bottom: 32px;
    font-weight: 400;
}

/* 区块标题 */
.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #1F2937;
    margin: 32px 0 16px 0;
}

/* 指标卡片 */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
}
.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #111827;
    margin: 8px 0 4px 0;
}
.metric-label {
    font-size: 13px;
    color: #6B7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-delta {
    font-size: 13px;
    margin-top: 4px;
}

/* 评分环 */
.score-ring {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    margin: 0 auto;
}
.score-number {
    font-size: 48px;
    font-weight: 700;
}
.score-grade {
    font-size: 16px;
    font-weight: 600;
    margin-top: 4px;
}

/* 优化建议卡片 */
.action-item {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-left: 4px solid;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.action-priority {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.action-title {
    font-size: 16px;
    font-weight: 600;
    color: #111827;
    margin: 6px 0;
}
.action-desc {
    font-size: 14px;
    color: #4B5563;
    line-height: 1.6;
}

/* 间距 */
.spacer-sm { height: 16px; }
.spacer-md { height: 24px; }
.spacer-lg { height: 40px; }

/* 隐藏 Streamlit 默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
    base_path = "data/"
    datasets = {}
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
        'page_country': 'cleaned_page_country.csv',
        'query_device': 'cleaned_query_device.csv',
        'page_device': 'cleaned_page_device.csv',
        'query_page': 'cleaned_query_page.csv'
    }
    for key, filename in file_map.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            datasets[key] = pd.read_csv(filepath)
    return datasets

data = load_data()

# ============================================================
# SEO 评分模型（V2.0 三维九指标）
# ============================================================
def calculate_seo_score(data):
    metrics = {}
    scores = {}
    
    # === 维度1：搜索表现 (40%) ===
    if 'daily_summary' in data:
        df = data['daily_summary']
        metrics['monthly_clicks'] = df['clicks'].sum() / max(df['data_date'].nunique() / 30, 1)
        metrics['monthly_impressions'] = df['impressions'].sum() / max(df['data_date'].nunique() / 30, 1)
        metrics['avg_ctr'] = df['ctr'].mean() if 'ctr' in df.columns else 0
        metrics['avg_position'] = df['position'].mean() if 'position' in df.columns else 50
        
        # 点击量得分 (0-100)
        click_score = min(metrics['monthly_clicks'] / 500 * 100, 100)
        # CTR得分
        ctr_score = min(metrics['avg_ctr'] / 0.05 * 100, 100)
        # 排名得分 (排名越低越好)
        position_score = max(0, (50 - metrics['avg_position']) / 50 * 100)
        # 展示量得分
        impression_score = min(metrics['monthly_impressions'] / 20000 * 100, 100)
        
        scores['search_performance'] = click_score * 0.3 + ctr_score * 0.3 + position_score * 0.25 + impression_score * 0.15
    else:
        scores['search_performance'] = 0
    
    # === 维度2：内容效果 (35%) ===
    content_scores = []
    if 'by_query' in data:
        df_q = data['by_query']
        metrics['total_keywords'] = len(df_q)
        metrics['active_keywords'] = len(df_q[df_q['clicks'] > 0]) if 'clicks' in df_q.columns else 0
        keyword_coverage = min(metrics['total_keywords'] / 1000 * 100, 100)
        active_ratio = metrics['active_keywords'] / max(metrics['total_keywords'], 1) * 100
        content_scores.extend([keyword_coverage, active_ratio])
    
    if 'by_page' in data:
        df_p = data['by_page']
        metrics['total_pages'] = len(df_p)
        metrics['active_pages'] = len(df_p[df_p['clicks'] > 0]) if 'clicks' in df_p.columns else 0
        page_active_ratio = metrics['active_pages'] / max(metrics['total_pages'], 1) * 100
        content_scores.append(page_active_ratio)
    
    if 'by_country' in data:
        df_c = data['by_country']
        metrics['country_count'] = df_c['country'].nunique() if 'country' in df_c.columns else 0
        geo_score = min(metrics['country_count'] / 50 * 100, 100)
        content_scores.append(geo_score)
    
    scores['content_effectiveness'] = np.mean(content_scores) if content_scores else 0
    
    # === 维度3：技术体验信号 (25%) ===
    tech_scores = []
    if 'by_device' in data:
        df_d = data['by_device']
        device_types = df_d['device'].nunique() if 'device' in df_d.columns else 0
        device_coverage = min(device_types / 3 * 100, 100)
        tech_scores.append(device_coverage)
        
        if 'device' in df_d.columns:
            total_clicks = df_d['clicks'].sum()
            if total_clicks > 0:
                mobile_clicks = df_d[df_d['device'].str.lower() == 'mobile']['clicks'].sum()
                mobile_ratio = mobile_clicks / total_clicks
                metrics['mobile_ratio'] = mobile_ratio
                mobile_score = 100 if 0.1 <= mobile_ratio <= 0.4 else 70
                tech_scores.append(mobile_score)
    
    if 'by_date' in data:
        df_date = data['by_date']
        metrics['data_days'] = df_date['data_date'].nunique() if 'data_date' in df_date.columns else 0
        continuity_score = min(metrics['data_days'] / 365 * 100, 100)
        tech_scores.append(continuity_score)
    
    scores['technical_experience'] = np.mean(tech_scores) if tech_scores else 0
    
    # === 最终加权得分 ===
    final_score = (
        scores['search_performance'] * 0.40 +
        scores['content_effectiveness'] * 0.35 +
        scores['technical_experience'] * 0.25
    )
    
    # 等级判定
    if final_score >= 90:
        grade, grade_label = 'A', 'Excellent'
    elif final_score >= 70:
        grade, grade_label = 'B', 'Good'
    elif final_score >= 50:
        grade, grade_label = 'C', 'Average'
    else:
        grade, grade_label = 'D', 'Poor'
    
    return {
        'final_score': round(final_score, 1),
        'grade': grade,
        'grade_label': grade_label,
        'dimensions': scores,
        'metrics': metrics
    }

# ============================================================
# 侧边栏导航
# ============================================================
with st.sidebar:
    st.markdown("### 📊 SEO Health Intelligence")
    st.markdown("---")
    
    # 语言切换
    lang = st.radio("🌐 Language", ['中文', 'English'], index=0, key='lang_select')
    
    st.markdown("---")
    st.markdown(f"**{'导航菜单' if lang == '中文' else 'Navigation'}**")
    
    pages = [
        '📊 Overview Dashboard',
        '🎯 SEO Health Score',
        '📈 Search Trends',
        '🔍 Keyword Insights',
        '📄 Page Analysis',
        '🌎 Country / Region',
        '📱 Device Distribution',
        '🚨 SEO Monitoring Center',
        '🚀 Recommendations'
    ]
    
    page = st.radio("", pages, label_visibility='collapsed', key='nav_radio')
    
    st.markdown("---")
    if 'by_date' in data:
        df_dates = data['by_date']
        if 'data_date' in df_dates.columns:
            date_range = f"{df_dates['data_date'].min()} ~ {df_dates['data_date'].max()}"
            st.caption(f"📅 {'数据范围' if lang == '中文' else 'Data Range'}: {date_range}")
    
    st.caption("B2B SEO Health Intelligence v3.0 | Based on GSC Data")


# ============================================================
# PAGE 1: Overview Dashboard
# ============================================================
if page == '📊 Overview Dashboard':
    st.markdown('<p class="page-title">Overview Dashboard</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-subtitle">{"网站搜索表现全局概览" if lang == "中文" else "Global overview of website search performance"}</p>', unsafe_allow_html=True)
    
    # 计算评分
    score_result = calculate_seo_score(data)
    
    # 评分卡片
    grade_colors = {'A': '#10B981', 'B': '#2563EB', 'C': '#F59E0B', 'D': '#EF4444'}
    grade_color = grade_colors.get(score_result['grade'], '#6B7280')
    
    col_score, col_metrics = st.columns([1, 2])
    
    with col_score:
        st.markdown(f"""
        <div style="text-align:center; padding:30px;">
            <div class="score-ring" style="border: 8px solid {grade_color};">
                <span class="score-number" style="color:{grade_color};">{score_result['final_score']}</span>
                <span class="score-grade" style="color:{grade_color};">Grade {score_result['grade']}</span>
            </div>
            <p style="margin-top:16px; font-size:14px; color:#6B7280;">
                {'SEO 健康度评分' if lang == '中文' else 'SEO Health Score'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_metrics:
        m1, m2, m3, m4 = st.columns(4)
        if 'daily_summary' in data:
            df_sum = data['daily_summary']
            total_clicks = int(df_sum['clicks'].sum())
            total_impressions = int(df_sum['impressions'].sum())
            avg_ctr = df_sum['ctr'].mean() * 100 if 'ctr' in df_sum.columns else 0
            avg_pos = df_sum['position'].mean() if 'position' in df_sum.columns else 0
            
            with m1:
                st.markdown(f"""<div class="metric-card">
                    <p class="metric-label">{'总点击' if lang == '中文' else 'Total Clicks'}</p>
                    <p class="metric-value">{total_clicks:,}</p>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card">
                    <p class="metric-label">{'总展示' if lang == '中文' else 'Impressions'}</p>
                    <p class="metric-value">{total_impressions:,}</p>
                </div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card">
                    <p class="metric-label">{'平均CTR' if lang == '中文' else 'Avg CTR'}</p>
                    <p class="metric-value">{avg_ctr:.2f}%</p>
                </div>""", unsafe_allow_html=True)
            with m4:
                st.markdown(f"""<div class="metric-card">
                    <p class="metric-label">{'平均排名' if lang == '中文' else 'Avg Position'}</p>
                    <p class="metric-value">{avg_pos:.1f}</p>
                </div>""", unsafe_allow_html=True)
    
    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
    
    # 趋势概览图
    if 'daily_summary' in data:
        st.markdown(f'<p class="section-title">{"📈 流量趋势概览" if lang == "中文" else "📈 Traffic Trend Overview"}</p>', unsafe_allow_html=True)
        df_trend = data['daily_summary'].copy()
        df_trend['data_date'] = pd.to_datetime(df_trend['data_date'])
        df_trend = df_trend.sort_values('data_date')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=df_trend['data_date'], y=df_trend['impressions'],
                   name='Impressions' if lang == 'English' else '展示次数',
                   marker_color='rgba(37,99,235,0.15)'),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=df_trend['data_date'], y=df_trend['clicks'],
                       name='Clicks' if lang == 'English' else '点击数',
                       line=dict(color='#2563EB', width=2.5)),
            secondary_y=True
        )
        fig.update_layout(
            **CHART_LAYOUT,
            height=380,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            yaxis=dict(title='Impressions' if lang == 'English' else '展示次数', tickfont=dict(size=12)),
            yaxis2=dict(title='Clicks' if lang == 'English' else '点击数', tickfont=dict(size=12))
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 2: SEO Health Score
# ============================================================
elif page == '🎯 SEO Health Score':
    st.markdown('<p class="page-title">SEO Health Score</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-subtitle">{"三维九指标评估体系 · V2.0" if lang == "中文" else "3-Dimension 9-Metric Assessment · V2.0"}</p>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score(data)
    grade_colors = {'A': '#10B981', 'B': '#2563EB', 'C': '#F59E0B', 'D': '#EF4444'}
    grade_color = grade_colors.get(score_result['grade'], '#6B7280')
    
    # 评分展示
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:40px 20px;">
            <div class="score-ring" style="border: 10px solid {grade_color};">
                <span class="score-number" style="color:{grade_color};">{score_result['final_score']}</span>
                <span class="score-grade" style="color:{grade_color};">Grade {score_result['grade']} · {score_result['grade_label']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # 雷达图
        dims = score_result['dimensions']
        categories = ['Search Performance', 'Content Effectiveness', 'Technical Experience']
        values = [dims.get('search_performance', 0), dims.get('content_effectiveness', 0), dims.get('technical_experience', 0)]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(37,99,235,0.1)',
            line=dict(color='#2563EB', width=2),
            marker=dict(size=8, color='#2563EB')
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=11)),
                angularaxis=dict(tickfont=dict(size=13))
            ),
            showlegend=False,
            height=350,
            margin=dict(l=60, r=60, t=40, b=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    
    # 维度详情
    st.markdown(f'<p class="section-title">{"📊 各维度得分详情" if lang == "中文" else "📊 Dimension Score Details"}</p>', unsafe_allow_html=True)
    
    dim_data = [
        ('Search Performance (40%)', dims.get('search_performance', 0), '搜索表现 (40%)'),
        ('Content Effectiveness (35%)', dims.get('content_effectiveness', 0), '内容效果 (35%)'),
        ('Technical Experience (25%)', dims.get('technical_experience', 0), '技术体验 (25%)')
    ]
    
    cols = st.columns(3)
    for i, (en_name, score, cn_name) in enumerate(dim_data):
        with cols[i]:
            name = cn_name if lang == '中文' else en_name
            color = '#10B981' if score >= 70 else '#F59E0B' if score >= 50 else '#EF4444'
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{name}</p>
                <p class="metric-value" style="color:{color};">{score:.1f}</p>
            </div>""", unsafe_allow_html=True)
    
    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    
    # 评分模型说明
    with st.expander(f"{'📐 评分模型说明' if lang == '中文' else '📐 Scoring Model Explanation'}"):
        st.markdown(f"""
        **{'权重分配' if lang == '中文' else 'Weight Distribution'}:**
        - {'搜索表现' if lang == '中文' else 'Search Performance'}: 40% — {'点击量、CTR、排名、展示量' if lang == '中文' else 'Clicks, CTR, Position, Impressions'}
        - {'内容效果' if lang == '中文' else 'Content Effectiveness'}: 35% — {'关键词覆盖、页面活跃度、地理覆盖' if lang == '中文' else 'Keyword coverage, Page activity, Geo coverage'}
        - {'技术体验' if lang == '中文' else 'Technical Experience'}: 25% — {'设备覆盖、移动端占比、数据连续性' if lang == '中文' else 'Device coverage, Mobile ratio, Data continuity'}
        
        **{'等级标准' if lang == '中文' else 'Grade Standards'}:** A (90-100) | B (70-89) | C (50-69) | D (0-49)
        
        **{'预留扩展' if lang == '中文' else 'Future Extension'}:** {'外链权威维度（待接入 Ahrefs/Moz API）' if lang == '中文' else 'Backlink Authority (pending Ahrefs/Moz API integration)'}
        """)

# ============================================================
# PAGE 3: Search Trends (股市风格)
# ============================================================
elif page == '📈 Search Trends':
    st.markdown('<p class="page-title">Search Performance Trends</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-subtitle">{"搜索表现时序分析 · 股市风格可视化" if lang == "中文" else "Time-series analysis with candlestick-style visualization"}</p>', unsafe_allow_html=True)
    
    if 'daily_summary' in data:
        df = data['daily_summary'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date')
        
        # 日期筛选
        col_start, col_end, col_metric = st.columns([1, 1, 1])
        with col_start:
            start_date = st.date_input(
                '开始日期' if lang == '中文' else 'Start Date',
                value=df['data_date'].min().date(),
                key='trend_start'
            )
        with col_end:
            end_date = st.date_input(
                '结束日期' if lang == '中文' else 'End Date',
                value=df['data_date'].max().date(),
                key='trend_end'
            )
        with col_metric:
            metric_options = {'点击数': 'clicks', '展示次数': 'impressions', 'CTR': 'ctr', '排名': 'position'} if lang == '中文' else {'Clicks': 'clicks', 'Impressions': 'impressions', 'CTR': 'ctr', 'Position': 'position'}
            selected_metric_label = st.selectbox(
                '指标' if lang == '中文' else 'Metric',
                list(metric_options.keys()),
                key='trend_metric'
            )
            selected_metric = metric_options[selected_metric_label]
        
        # 筛选数据
        mask = (df['data_date'].dt.date >= start_date) & (df['data_date'].dt.date <= end_date)
        df_filtered = df[mask].copy()
        
        if not df_filtered.empty:
            # 计算移动平均线
            df_filtered['MA7'] = df_filtered[selected_metric].rolling(window=7, min_periods=1).mean()
            df_filtered['MA30'] = df_filtered[selected_metric].rolling(window=30, min_periods=1).mean()
            
            # 股市风格图表
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                row_heights=[0.7, 0.3],
                vertical_spacing=0.08
            )
            
            # 主图：指标值 + MA线
            fig.add_trace(
                go.Scatter(
                    x=df_filtered['data_date'], y=df_filtered[selected_metric],
                    name=selected_metric_label,
                    line=dict(color='#2563EB', width=1.5),
                    fill='tozeroy', fillcolor='rgba(37,99,235,0.05)'
                ), row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df_filtered['data_date'], y=df_filtered['MA7'],
                    name='MA7', line=dict(color='#F59E0B', width=2, dash='dot')
                ), row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df_filtered['data_date'], y=df_filtered['MA30'],
                    name='MA30', line=dict(color='#EF4444', width=2)
                ), row=1, col=1
            )
            
            # 副图：成交量（用展示量代替）
            if selected_metric != 'impressions' and 'impressions' in df_filtered.columns:
                fig.add_trace(
                    go.Bar(
                        x=df_filtered['data_date'], y=df_filtered['impressions'],
                        name='Impressions' if lang == 'English' else '展示量',
                        marker_color='rgba(37,99,235,0.2)'
                    ), row=2, col=1
                )
            elif selected_metric != 'clicks' and 'clicks' in df_filtered.columns:
                fig.add_trace(
                    go.Bar(
                        x=df_filtered['data_date'], y=df_filtered['clicks'],
                        name='Clicks' if lang == 'English' else '点击量',
                        marker_color='rgba(37,99,235,0.2)'
                    ), row=2, col=1
                )
            
            fig.update_layout(
                **CHART_LAYOUT,
                height=520,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=12)),
                xaxis2=dict(tickfont=dict(size=12)),
                yaxis=dict(tickfont=dict(size=12), title=dict(text=selected_metric_label, font=dict(size=13))),
                yaxis2=dict(tickfont=dict(size=11))
            )
            fig.update_xaxes(rangeslider=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)
            
            # 月度汇总表
            st.markdown(f'<p class="section-title">{"📅 月度汇总" if lang == "中文" else "📅 Monthly Summary"}</p>', unsafe_allow_html=True)
            df_filtered['month'] = df_filtered['data_date'].dt.to_period('M').astype(str)
            monthly = df_filtered.groupby('month').agg(
                clicks=('clicks', 'sum'),
                impressions=('impressions', 'sum'),
                avg_ctr=('ctr', 'mean'),
                avg_position=('position', 'mean')
            ).reset_index()
            monthly['avg_ctr'] = (monthly['avg_ctr'] * 100).round(2)
            monthly['avg_position'] = monthly['avg_position'].round(1)
            monthly.columns = ['Month', 'Clicks', 'Impressions', 'Avg CTR(%)', 'Avg Position']
            st.dataframe(monthly, use_container_width=True, hide_index=True)
    else:
        st.info("未找到日期维度数据" if lang == '中文' else "Date dimension data not found")

# ============================================================
# PAGE 4: Keyword Insights
# ============================================================
elif page == '🔍 Keyword Insights':
    st.markdown('<p class="page-title">Keyword Insights</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-subtitle">{"关键词表现深度分析" if lang == "中文" else "Deep analysis of keyword performance"}</p>', unsafe_allow_html=True)
    
    if 'by_query' in data:
        df_q = data['by_query'].copy()
        
        # 关键指标
        c1, c2, c3, c4 = st.columns(4)
        total_kw = len(df_q)
        active_kw = len(df_q[df_q['clicks'] > 0]) if 'clicks' in df_q.columns else 0
        top10_kw = len(df_q[df_q['position'] <= 10]) if 'position' in df_q.columns else 0
        top3_kw = len(df_q[df_q['position'] <= 3]) if 'position' in df_q.columns else 0
        
        with c1:
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{'总关键词' if lang == '中文' else 'Total Keywords'}</p>
                <p class="metric-value">{total_kw:,}</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{'有点击' if lang == '中文' else 'With Clicks'}</p>
                <p class="metric-value">{active_kw}</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{'Top 10 排名' if lang == '中文' else 'Top 10 Ranked'}</p>
                <p class="metric-value">{top10_kw}</p>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{'Top 3 排名' if lang == '中文' else 'Top 3 Ranked'}</p>
                <p class="metric-value">{top3_kw}</p>
            </div>""", unsafe_allow_html=True)
        
        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
        
        # 关键词排名分布
        st.markdown(f'<p class="section-title">{"🎯 排名分布" if lang == "中文" else "🎯 Ranking Distribution"}</p>', unsafe_allow_html=True)
        if 'position' in df_q.columns:
            bins = [0, 3, 10, 20, 50, 100]
            labels = ['Top 3', '4-10', '11-20', '21-50', '50+']
            df_q['rank_group'] = pd.cut(df_q['position'], bins=bins, labels=labels, include_lowest=True)
            rank_dist = df_q['rank_group'].value_counts().reindex(labels).fillna(0)
            
            fig_rank = go.Figure(go.Bar(
                x=rank_dist.index,
                y=rank_dist.values,
                marker_color=['#10B981', '#2563EB', '#F59E0B', '#F97316', '#EF4444'],
                text=rank_dist.values.astype(int),
                textposition='outside',
                textfont=dict(size=13)
            ))
            fig_rank.update_layout(
                **CHART_LAYOUT,
                height=350,
                xaxis=dict(title='Position Range' if lang == 'English' else '排名区间', tickfont=dict(size=13)),
                yaxis=dict(title='Keywords Count' if lang == 'English' else '关键词数量', tickfont=dict(size=12))
            )
            st.plotly_chart(fig_rank, use_container_width=True)
        
        # Top 关键词表格
        st.markdown(f'<p class="section-title">{"🏆 Top 20 关键词" if lang == "中文" else "🏆 Top 20 Keywords"}</p>', unsafe_allow_html=True)
        top_kw = df_q.nlargest(20, 'clicks')[['query', 'clicks', 'impressions', 'ctr', 'position']].copy()
        top_kw['ctr'] = (top_kw['ctr'] * 100).round(2)
        top_kw['position'] = top_kw['position'].round(1)
        top_kw.columns = ['Keyword', 'Clicks', 'Impressions', 'CTR(%)', 'Position']
        st.dataframe(top_kw, use_container_width=True, hide_index=True)
        
        # 机会关键词（高展示低点击）
        st.markdown(f'<p class="section-title">{"💡 机会关键词（高展示低CTR）" if lang == "中文" else "💡 Opportunity Keywords (High Impressions, Low CTR)"}</p>', unsafe_allow_html=True)
        if 'impressions' in df_q.columns and 'ctr' in df_q.columns:
            opportunity = df_q[(df_q['impressions'] > df_q['impressions'].median()) & (df_q['ctr'] < df_q['ctr'].median())].nlargest(15, 'impressions')
            if not opportunity.empty:
                opp_display = opportunity[['query', 'clicks', 'impressions', 'ctr', 'position']].copy()
                opp_display['ctr'] = (opp_display['ctr'] * 100).round(2)
                opp_display['position'] = opp_display['position'].round(1)
                opp_display.columns = ['Keyword', 'Clicks', 'Impressions', 'CTR(%)', 'Position']
                st.dataframe(opp_display, use_container_width=True, hide_index=True)
            else:
                st.info("暂无符合条件的机会关键词" if lang == '中文' else "No opportunity keywords found")
    else:
        st.info("未找到关键词数据，请确保 data/ 目录下有 cleaned_by_query.csv" if lang == '中文' else "Keyword data not found")

# ============================================================
# PAGE 5: Page Analysis
# ============================================================
elif page == '📄 Page Analysis':
    st.markdown('<p class="page-title">Page Performance Analysis</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-subtitle">{"页面效果分析与机会矩阵" if lang == "中文" else "Page performance analysis and opportunity matrix"}</p>', unsafe_allow_html=True)
    
    if 'by_page' in data:
        df_p = data['by_page'].copy()
        
        # 关键指标
        c1, c2, c3 = st.columns(3)
        total_pages = len(df_p)
        active_pages = len(df_p[df_p['clicks'] > 0]) if 'clicks' in df_p.columns else 0
        active_ratio = active_pages / max(total_pages, 1) * 100
        
        with c1:
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{'总页面数' if lang == '中文' else 'Total Pages'}</p>
                <p class="metric-value">{total_pages}</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{'活跃页面' if lang == '中文' else 'Active Pages'}</p>
                <p class="metric-value">{active_pages}</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card">
                <p class="metric-label">{'活跃率' if lang == '中文' else 'Active Rate'}</p>
                <p class="metric-value">{active_ratio:.1f}%</p>
            </div>""", unsafe_allow_html=True)
        
        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
        
        # 页面机会矩阵（气泡图）
        st.markdown(f'<p class="section-title">{"🎯 页面机会矩阵" if lang == "中文" else "🎯 Page Opportunity Matrix"}</p>', unsafe_allow_html=True)
        if all(col in df_p.columns for col in ['impressions', 'ctr', 'clicks']):
            df_bubble = df_p[df_p['impressions'] > 0].copy()
            df_bubble['ctr_pct'] = df_bubble['ctr'] * 100
            df_bubble['page_short'] = df_bubble['page'].str.replace('https?://[^/]+', '', regex=True).str[:50]
            
            fig_matrix = px.scatter(
                df_bubble.nlargest(50, 'impressions'),
                x='impressions', y='ctr_pct', size='clicks',
                hover_name='page_short',
                color='position' if 'position' in df_bubble.columns else None,
                color_continuous_scale='RdYlGn_r',
                size_max=40
            )
            fig_matrix.update_layout(
                **CHART_LAYOUT,
                height=450,
                xaxis=dict(title='Impressions' if lang == 'English' else '展示次数', tickfont=dict(size=12)),
                yaxis=dict(title='CTR (%)' if lang == 'English' else 'CTR (%)', tickfont=dict(size=12)),
                coloraxis_colorbar=dict(title='Position' if lang == 'English' else '排名')
            )
            # 添加参考线
            avg_ctr = df_bubble['ctr_pct'].mean()
            avg_imp = df_bubble['impressions'].mean()
            fig_matrix.add_hline(y=avg_ctr, line_dash='dash', line_color='#6B7280', opacity=0.5)
            fig_matrix.add_vline(x=avg_imp, line_dash='dash', line_color='#6B7280', opacity=0.5)
            st.plotly_chart(fig_matrix, use_container_width=True)
            
            st.caption("💡 " + ("右上角 = 明星页面 | 右下角 = 高曝光低转化（优化机会）" if lang == '中文' else "Top-right = Star pages | Bottom-right = High impression, low CTR (optimization opportunity)"))
        
        # Top 页面表格
        st.markdown(f'<p class="section-title">{"🏆 Top 20 页面" if lang == "中文" else "🏆 Top 20 Pages"}</p>', unsafe_allow_html=True)
        top_pages = df_p.nlargest(20, 'clicks')[['page', 'clicks', 'impressions', 'ctr', 'position']].copy()
        top_pages['ctr'] = (top_pages['ctr'] * 100).round(2)
        top_pages['position'] = top_pages['position'].round(1)
        top_pages['page'] = top_pages['page'].str.replace('https?://[^/]+', '', regex=True).str[:60]
        top_pages.columns = ['Page', 'Clicks', 'Impressions', 'CTR(%)', 'Position']
        st.dataframe(top_pages, use_container_width=True, hide_index=True)
    else:
        st.info("未找到页面数据，请确保 data/ 目录下有 cleaned_by_page.csv" if lang == '中文' else "Page data not found")

