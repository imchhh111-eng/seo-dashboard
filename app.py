
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="B2B SEO 健康度诊断",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义CSS样式 ====================
st.markdown("""
<style>
    /* 全局字体和背景 */
    .main {
        background-color: #f8f9fa;
    }
    
    /* 侧边栏美化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
    }
    
    /* 指标卡片样式 */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid #4ECDC4;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* 健康度评分卡片 */
    .health-card {
        background: white;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align: center;
        margin: 20px 0;
    }
    .grade-display {
        font-size: 80px;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
    .grade-text {
        font-size: 18px;
        color: #666;
        margin-top: 8px;
    }
    .score-display {
        font-size: 28px;
        font-weight: 600;
        color: #333;
        margin-top: 12px;
    }
    
    /* 页面标题样式 */
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 5px;
        padding-bottom: 10px;
        border-bottom: 3px solid #4ECDC4;
        display: inline-block;
    }
    .page-subtitle {
        font-size: 14px;
        color: #888;
        margin-bottom: 25px;
    }
    
    /* 分隔线 */
    .section-divider {
        height: 1px;
        background: linear-gradient(to right, #4ECDC4, transparent);
        margin: 30px 0;
    }
    
    /* 异常标签 */
    .anomaly-high {
        background-color: #ffe0e0;
        color: #d32f2f;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .anomaly-low {
        background-color: #fff3e0;
        color: #f57c00;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 表格美化 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 统一配色方案 ====================
COLORS = {
    'primary': '#4ECDC4',       # 主色 - 青绿
    'secondary': '#FF6B6B',     # 辅色 - 珊瑚红
    'accent': '#45B7D1',        # 强调色 - 天蓝
    'warning': '#FFA500',       # 警告 - 橙色
    'success': '#2ECC71',       # 成功 - 绿色
    'dark': '#1a1a2e',          # 深色
    'light': '#f8f9fa',         # 浅色
    'text': '#333333',          # 文字
    'muted': '#888888',         # 次要文字
    'chart_palette': ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
}

# 统一图表模板
CHART_TEMPLATE = dict(
    font=dict(family="Arial, sans-serif", size=12, color=COLORS['text']),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11)
    )
)


# ==================== 数据加载 ====================
@st.cache_data
def load_data():
    """加载所有CSV数据文件"""
    base_path = "data/"
    data = {}

    try:
        data['by_date'] = pd.read_csv(f"{base_path}cleaned_by_date.csv")
        data['by_date']['data_date'] = pd.to_datetime(data['by_date']['data_date'])
    except:
        data['by_date'] = pd.DataFrame()

    try:
        data['daily_summary'] = pd.read_csv(f"{base_path}cleaned_daily_summary.csv")
        data['daily_summary']['data_date'] = pd.to_datetime(data['daily_summary']['data_date'])
    except:
        data['daily_summary'] = pd.DataFrame()

    try:
        data['by_device'] = pd.read_csv(f"{base_path}cleaned_by_device.csv")
        data['by_device']['data_date'] = pd.to_datetime(data['by_device']['data_date'])
    except:
        data['by_device'] = pd.DataFrame()

    try:
        data['by_country'] = pd.read_csv(f"{base_path}cleaned_by_country.csv")
        data['by_country']['data_date'] = pd.to_datetime(data['by_country']['data_date'])
    except:
        data['by_country'] = pd.DataFrame()

    try:
        data['by_query'] = pd.read_csv(f"{base_path}cleaned_by_query.csv")
        data['by_query']['data_date'] = pd.to_datetime(data['by_query']['data_date'])
    except:
        data['by_query'] = pd.DataFrame()

    try:
        data['by_page'] = pd.read_csv(f"{base_path}cleaned_by_page.csv")
        data['by_page']['data_date'] = pd.to_datetime(data['by_page']['data_date'])
    except:
        data['by_page'] = pd.DataFrame()

    return data


data = load_data()


# ==================== 侧边栏导航 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #4ECDC4; font-size: 24px; margin: 0;">🔍 SEO 健康度诊断</h1>
        <p style="color: #aaa; font-size: 12px; margin-top: 5px;">B2B Independent Site Diagnostic</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "导航菜单",
        ["📊 总览仪表盘", "🏥 SEO 健康度评分", "📈 搜索表现趋势",
         "🌍 国家/地区分析", "📱 设备分布", "🚨 流量异常检测"],
        label_visibility="collapsed"
    )

    # 数据范围信息
    if not data['by_date'].empty:
        min_date = data['by_date']['data_date'].min().strftime('%Y-%m-%d')
        max_date = data['by_date']['data_date'].max().strftime('%Y-%m-%d')
        st.markdown("---")
        st.markdown(f"""
        <div style="background: rgba(78,205,196,0.1); border-radius: 8px; padding: 12px; margin-top: 10px;">
            <p style="color: #4ECDC4; font-size: 11px; margin: 0; font-weight: 600;">📅 数据范围</p>
            <p style="color: #ccc; font-size: 11px; margin: 4px 0 0 0;">{min_date} 至 {max_date}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <p style="color: #666; font-size: 10px; margin: 0;">B2B SEO 健康度诊断工具 v1.0</p>
        <p style="color: #555; font-size: 10px; margin: 2px 0 0 0;">基于 GSC 数据</p>
    </div>
    """, unsafe_allow_html=True)


# ==================== 辅助函数 ====================
def render_metric_card(label, value, icon="📊", color="#4ECDC4"):
    """渲染美化的指标卡片"""
    return f"""
    <div class="metric-card" style="border-left-color: {color};">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """


def apply_chart_style(fig, height=400):
    """统一图表样式"""
    fig.update_layout(
        **CHART_TEMPLATE,
        height=height,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False)
    )
    return fig


# ==================== 页面1：总览仪表盘 ====================
if page == "📊 总览仪表盘":
    st.markdown('<p class="page-title">B2B独立站 SEO 总览仪表盘</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">基于 Google Search Console 数据的综合表现概览</p>', unsafe_allow_html=True)

    if not data['by_date'].empty:
        df = data['by_date']
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        avg_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        avg_position = df['position'].mean()

        # 指标卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(render_metric_card("总点击数", f"{total_clicks:,}", "🖱️", "#FF6B6B"), unsafe_allow_html=True)
        with col2:
            st.markdown(render_metric_card("总展示次数", f"{total_impressions:,}", "👁️", "#4ECDC4"), unsafe_allow_html=True)
        with col3:
            st.markdown(render_metric_card("平均CTR", f"{avg_ctr:.2f}%", "📈", "#45B7D1"), unsafe_allow_html=True)
        with col4:
            st.markdown(render_metric_card("平均排名", f"{avg_position:.1f}", "🏆", "#96CEB4"), unsafe_allow_html=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # 快速趋势预览
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📈 近期点击趋势")
            recent = df.sort_values('data_date').tail(30)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=recent['data_date'], y=recent['clicks'],
                mode='lines+markers',
                line=dict(color=COLORS['secondary'], width=2),
                marker=dict(size=4),
                fill='tozeroy',
                fillcolor='rgba(255,107,107,0.1)'
            ))
            fig = apply_chart_style(fig, height=250)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 👁️ 近期展示趋势")
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=recent['data_date'], y=recent['impressions'],
                mode='lines+markers',
                line=dict(color=COLORS['primary'], width=2),
                marker=dict(size=4),
                fill='tozeroy',
                fillcolor='rgba(78,205,196,0.1)'
            ))
            fig2 = apply_chart_style(fig2, height=250)
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.info("💡 请从左侧导航菜单选择具体分析模块，深入了解各维度表现")
    else:
        st.error("❌ 未找到数据文件，请检查 data/ 文件夹中是否包含 CSV 文件。")

# ==================== 页面2：SEO 健康度评分 ====================
elif page == "🏥 SEO 健康度评分":
    st.markdown('<p class="page-title">SEO 健康度评分</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">基于四维加权模型的综合健康度评估</p>', unsafe_allow_html=True)

    if not data['by_date'].empty and not data['by_query'].empty:
        df_date = data['by_date']
        df_query = data['by_query']

        # --- 搜索表现维度 (40%) ---
        total_clicks = df_date['clicks'].sum()
        total_impressions = df_date['impressions'].sum()
        avg_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        avg_position = df_date['position'].mean()

        ctr_score = min(100, (avg_ctr / 3.0) * 100)

        if avg_position <= 10:
            position_score = 100
        elif avg_position <= 20:
            position_score = 80
        elif avg_position <= 30:
            position_score = 60
        elif avg_position <= 50:
            position_score = 40
        else:
            position_score = 20

        days_count = (df_date['data_date'].max() - df_date['data_date'].min()).days + 1
        daily_clicks = total_clicks / days_count if days_count > 0 else 0
        click_score = min(100, (daily_clicks / 10) * 100)

        search_performance_score = (ctr_score * 0.4 + position_score * 0.35 + click_score * 0.25)

        # --- 内容质量维度 (30%) ---
        unique_queries = df_query['query'].nunique() if 'query' in df_query.columns else 0
        keyword_coverage_score = min(100, (unique_queries / 100) * 100)

        if not data['by_page'].empty and 'page' in data['by_page'].columns:
            unique_pages = data['by_page']['page'].nunique()
        else:
            unique_pages = 0
        page_coverage_score = min(100, (unique_pages / 20) * 100)

        if not df_query.empty and 'clicks' in df_query.columns:
            clicked_queries = df_query[df_query['clicks'] > 0]['query'].nunique()
            content_depth_score = min(100, (clicked_queries / max(unique_queries, 1)) * 100)
        else:
            content_depth_score = 50

        content_quality_score = (keyword_coverage_score * 0.4 + page_coverage_score * 0.3 + content_depth_score * 0.3)

        # --- 技术SEO维度 (15%) ---
        if not data['by_device'].empty:
            mobile_data = data['by_device'][data['by_device']['device'] == 'MOBILE']
            desktop_data = data['by_device'][data['by_device']['device'] == 'DESKTOP']

            if not mobile_data.empty and not desktop_data.empty:
                mobile_ctr = mobile_data['clicks'].sum() / mobile_data['impressions'].sum() * 100 if mobile_data['impressions'].sum() > 0 else 0
                desktop_ctr = desktop_data['clicks'].sum() / desktop_data['impressions'].sum() * 100 if desktop_data['impressions'].sum() > 0 else 0
                ctr_gap = abs(mobile_ctr - desktop_ctr)
                device_compat_score = max(0, 100 - ctr_gap * 20)
            else:
                device_compat_score = 50
        else:
            device_compat_score = 50

        technical_seo_score = device_compat_score

        # --- 用户体验维度 (15%) ---
        if len(df_date) >= 30:
            recent_30 = df_date.nlargest(30, 'data_date')
            older_30 = df_date.nsmallest(30, 'data_date')

            recent_ctr = recent_30['clicks'].sum() / recent_30['impressions'].sum() * 100 if recent_30['impressions'].sum() > 0 else 0
            older_ctr = older_30['clicks'].sum() / older_30['impressions'].sum() * 100 if older_30['impressions'].sum() > 0 else 0

            if older_ctr > 0:
                ctr_trend = (recent_ctr - older_ctr) / older_ctr * 100
            else:
                ctr_trend = 0

            trend_score = min(100, max(0, 50 + ctr_trend * 2))
        else:
            trend_score = 50

        position_std = df_date['position'].std()
        stability_score = max(0, 100 - position_std * 2)

        user_experience_score = (trend_score * 0.5 + stability_score * 0.5)

        # --- 综合评分 ---
        total_score = (
                search_performance_score * 0.40 +
                content_quality_score * 0.30 +
                technical_seo_score * 0.15 +
                user_experience_score * 0.15
        )

        if total_score >= 90:
            grade, grade_text, grade_color = "A", "优秀", "#2ECC71"
        elif total_score >= 70:
            grade, grade_text, grade_color = "B", "良好", "#45B7D1"
        elif total_score >= 50:
            grade, grade_text, grade_color = "C", "一般", "#FFA500"
        else:
            grade, grade_text, grade_color = "D", "严重", "#FF6B6B"

        # 显示评分
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="health-card">
                <p class="grade-display" style="color: {grade_color};">{grade}</p>
                <p class="grade-text">{grade_text}</p>
                <p class="score-display">{total_score:.1f} / 100</p>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                    <span style="font-size: 12px; color: #999;">基于 GSC 数据四维加权评估模型</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # 雷达图
        st.markdown("#### 🎯 各维度得分")
        categories = ['搜索表现', '内容质量', '技术SEO', '用户体验']
        scores = [search_performance_score, content_quality_score, technical_seo_score, user_experience_score]

        fig = go.Figure(data=go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(78,205,196,0.2)',
            line_color=COLORS['primary'],
            line_width=2
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=True, tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=13, color=COLORS['text']))
            ),
            showlegend=False,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        # 详细得分 - 进度条形式
        st.markdown("#### 📋 评分明细")

        dimensions = [
            ("搜索表现", search_performance_score, "40%", f"CTR={avg_ctr:.2f}% | 平均排名={avg_position:.1f} | 日均点击={daily_clicks:.1f}"),
            ("内容质量", content_quality_score, "30%", f"关键词覆盖={unique_queries}个 | 页面覆盖={unique_pages}个"),
            ("技术SEO", technical_seo_score, "15%", f"设备兼容性评分={device_compat_score:.1f}"),
            ("用户体验", user_experience_score, "15%", f"趋势评分={trend_score:.1f} | 稳定性={stability_score:.1f}")
        ]

        for dim_name, dim_score, weight, detail in dimensions:
            col1, col2 = st.columns([3, 1])
            with col1:
                bar_color = COLORS['success'] if dim_score >= 70 else (COLORS['warning'] if dim_score >= 50 else COLORS['secondary'])
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-weight: 600; color: #333;">{dim_name} ({weight})</span>
                        <span style="font-weight: 700; color: {bar_color};">{dim_score:.1f}</span>
                    </div>
                    <div style="background: #e9ecef; border-radius: 10px; height: 10px; overflow: hidden;">
                        <div style="background: {bar_color}; width: {min(dim_score, 100)}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                    <span style="font-size: 11px; color: #999;">{detail}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("数据不足，无法计算健康度评分。")

# ==================== 页面3：搜索表现趋势 ====================
elif page == "📈 搜索表现趋势":
    st.markdown('<p class="page-title">搜索表现趋势</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">追踪点击、展示、CTR 和排名的时间变化</p>', unsafe_allow_html=True)

    if not data['by_date'].empty:
        df = data['by_date'].sort_values('data_date')

        # 日期范围和粒度选择
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            start_date = st.date_input("开始日期", df['data_date'].min())
        with col2:
            end_date = st.date_input("结束日期", df['data_date'].max())
        with col3:
            granularity = st.selectbox("时间粒度", ["日", "周", "月"])

        # 筛选日期范围
        mask = (df['data_date'] >= pd.Timestamp(start_date)) & (df['data_date'] <= pd.Timestamp(end_date))
        df_filtered = df[mask].copy()

        if granularity == "周":
            df_filtered['period'] = df_filtered['data_date'].dt.to_period('W').apply(lambda r: r.start_time)
            df_agg = df_filtered.groupby('period').agg(
                {'clicks': 'sum', 'impressions': 'sum', 'position': 'mean', 'ctr': 'mean'}).reset_index()
            df_agg.rename(columns={'period': 'data_date'}, inplace=True)
        elif granularity == "月":
            df_filtered['period'] = df_filtered['data_date'].dt.to_period('M').apply(lambda r: r.start_time)
            df_agg = df_filtered.groupby('period').agg(
                {'clicks': 'sum', 'impressions': 'sum', 'position': 'mean', 'ctr': 'mean'}).reset_index()
            df_agg.rename(columns={'period': 'data_date'}, inplace=True)
        else:
            df_agg = df_filtered

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # 点击 & 展示双轴图
        st.markdown("#### 🖱️ 点击数 & 展示次数趋势")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=df_agg['data_date'], y=df_agg['impressions'], name="展示次数",
                   marker_color=COLORS['primary'], opacity=0.6),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=df_agg['data_date'], y=df_agg['clicks'], name="点击数",
                       line=dict(color=COLORS['secondary'], width=2.5),
                       mode='lines+markers', marker=dict(size=4)),
            secondary_y=True
        )
        fig = apply_chart_style(fig, height=400)
        fig.update_yaxes(title_text="展示次数", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(title_text="点击数", secondary_y=True, showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

        # CTR和排名趋势
        st.markdown("#### 📊 CTR & 平均排名趋势")
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(
            go.Scatter(x=df_agg['data_date'],
                       y=df_agg['ctr'] * 100 if df_agg['ctr'].max() <= 1 else df_agg['ctr'],
                       name="CTR (%)", line=dict(color=COLORS['accent'], width=2.5),
                       mode='lines+markers', marker=dict(size=4)),
            secondary_y=False
        )
        fig2.add_trace(
            go.Scatter(x=df_agg['data_date'], y=df_agg['position'], name="平均排名",
                       line=dict(color=COLORS['chart_palette'][3], width=2, dash='dash')),
            secondary_y=True
        )
        fig2 = apply_chart_style(fig2, height=350)
        fig2.update_yaxes(title_text="CTR (%)", secondary_y=False, showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        fig2.update_yaxes(title_text="平均排名", autorange="reversed", secondary_y=True, showgrid=False)
        st.plotly_chart(fig2, use_container_width=True)

        # 数据摘要
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 📋 期间数据摘要")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("期间总点击", f"{df_filtered['clicks'].sum():,}")
        col2.metric("期间总展示", f"{df_filtered['impressions'].sum():,}")
        period_ctr = df_filtered['clicks'].sum() / df_filtered['impressions'].sum() * 100 if df_filtered['impressions'].sum() > 0 else 0
        col3.metric("期间平均CTR", f"{period_ctr:.2f}%")
        col4.metric("期间平均排名", f"{df_filtered['position'].mean():.1f}")
    else:
        st.warning("未找到日期维度数据，请检查数据文件。")

# ==================== 页面4：国家/地区分析 ====================
elif page == "🌍 国家/地区分析":
    st.markdown('<p class="page-title">国家/地区分析</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">分析不同国家和地区的搜索表现差异</p>', unsafe_allow_html=True)

    if not data['by_country'].empty:
        df = data['by_country']

        # 按国家汇总
        country_summary = df.groupby('country').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean'
        }).reset_index()
        country_summary['ctr'] = country_summary['clicks'] / country_summary['impressions'] * 100
        country_summary = country_summary.sort_values('clicks', ascending=False)

        # 核心指标
        col1, col2, col3 = st.columns(3)
        col1.metric("覆盖国家数", f"{len(country_summary)}")
        col2.metric("有点击国家", f"{len(country_summary[country_summary['clicks'] > 0])}")
        top_country = country_summary.iloc[0]['country'] if len(country_summary) > 0 else "N/A"
        col3.metric("最大流量来源", top_country)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Top 10 国家
        st.markdown("#### 🏆 Top 10 流量来源国家")
        top10 = country_summary.head(10)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top10['country'], y=top10['clicks'],
            name='点击数', marker_color=COLORS['secondary'],
            marker_line_color=COLORS['secondary'], marker_line_width=0,
            opacity=0.85
        ))
        fig.add_trace(go.Bar(
            x=top10['country'], y=top10['impressions'] / 100,
            name='展示次数 (÷100)', marker_color=COLORS['primary'],
            marker_line_color=COLORS['primary'], marker_line_width=0,
            opacity=0.85
        ))
        fig.update_layout(barmode='group')
        fig = apply_chart_style(fig, height=400)
        st.plotly_chart(fig, use_container_width=True)

        # 地理分布图
        st.markdown("#### 🗺️ 全球流量分布")
        fig_map = px.choropleth(
            country_summary,
            locations='country',
            color='clicks',
            hover_name='country',
            color_continuous_scale='Tealgrn',
            title=''
        )
        fig_map.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False)
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # 国家详细数据表
        st.markdown("#### 📋 各国家详细数据")
        display_df = country_summary.head(20).copy()
        display_df['ctr'] = display_df['ctr'].apply(lambda x: f"{x:.2f}%")
        display_df['position'] = display_df['position'].apply(lambda x: f"{x:.1f}")
        display_df.columns = ['国家', '点击数', '展示次数', '平均排名', 'CTR']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("未找到国家维度数据，请检查数据文件。")

# ==================== 页面5：设备分布 ====================
elif page == "📱 设备分布":
    st.markdown('<p class="page-title">设备分布分析</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">了解不同设备类型的流量构成和表现差异</p>', unsafe_allow_html=True)

    if not data['by_device'].empty:
        df = data['by_device']

        # 按设备汇总
        device_summary = df.groupby('device').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean'
        }).reset_index()
        device_summary['ctr'] = device_summary['clicks'] / device_summary['impressions'] * 100

        # 设备占比饼图
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🖱️ 点击量占比")
            fig_pie1 = px.pie(device_summary, values='clicks', names='device',
                              color_discrete_sequence=COLORS['chart_palette'],
                              hole=0.4)
            fig_pie1.update_traces(textposition='inside', textinfo='percent+label',
                                   textfont_size=12)
            fig_pie1.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                                   showlegend=False)
            st.plotly_chart(fig_pie1, use_container_width=True)

        with col2:
            st.markdown("#### 👁️ 展示量占比")
            fig_pie2 = px.pie(device_summary, values='impressions', names='device',
                              color_discrete_sequence=COLORS['chart_palette'],
                              hole=0.4)
            fig_pie2.update_traces(textposition='inside', textinfo='percent+label',
                                   textfont_size=12)
            fig_pie2.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                                   showlegend=False)
            st.plotly_chart(fig_pie2, use_container_width=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # 各设备CTR对比
        st.markdown("#### 📊 各设备 CTR & 排名对比")
        col1, col2 = st.columns(2)
        with col1:
            fig_ctr = go.Figure()
            fig_ctr.add_trace(go.Bar(
                x=device_summary['device'], y=device_summary['ctr'],
                marker_color=[COLORS['secondary'], COLORS['primary'], COLORS['accent']],
                text=device_summary['ctr'].apply(lambda x: f"{x:.2f}%"),
                textposition='outside'
            ))
            fig_ctr = apply_chart_style(fig_ctr, height=300)
            fig_ctr.update_layout(title="CTR 对比 (%)", yaxis_title="CTR (%)")
            st.plotly_chart(fig_ctr, use_container_width=True)

        with col2:
            fig_pos = go.Figure()
            fig_pos.add_trace(go.Bar(
                x=device_summary['device'], y=device_summary['position'],
                marker_color=[COLORS['chart_palette'][3], COLORS['chart_palette'][4], COLORS['chart_palette'][5]],
                text=device_summary['position'].apply(lambda x: f"{x:.1f}"),
                textposition='outside'
            ))
            fig_pos = apply_chart_style(fig_pos, height=300)
            fig_pos.update_layout(title="平均排名对比", yaxis_title="平均排名")
            st.plotly_chart(fig_pos, use_container_width=True)

        # 设备趋势
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 📈 各设备月度点击趋势")
        df['month'] = df['data_date'].dt.to_period('M').apply(lambda r: r.start_time)
        device_trend = df.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
        fig_trend = px.line(device_trend, x='month', y='clicks', color='device',
                            color_discrete_sequence=COLORS['chart_palette'],
                            markers=True)
        fig_trend = apply_chart_style(fig_trend, height=350)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("未找到设备维度数据，请检查数据文件。")

# ==================== 页面6：流量异常检测 ====================
elif page == "🚨 流量异常检测":
    st.markdown('<p class="page-title">流量异常检测</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">基于统计方法自动识别流量异常波动，帮助快速定位问题</p>', unsafe_allow_html=True)

    if not data['by_date'].empty:
        df = data['by_date'].sort_values('data_date').copy()

        # 参数设置
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <p style="color: #4ECDC4; font-weight: 600; font-size: 13px;">⚙️ 异常检测参数</p>
        """, unsafe_allow_html=True)

        detection_method = st.sidebar.selectbox(
            "检测方法",
            ["Z-Score (标准差法)", "IQR (四分位距法)", "移动平均偏离法"]
        )

        metric_choice = st.sidebar.selectbox(
            "检测指标",
            ["impressions", "clicks", "ctr", "position"],
            format_func=lambda x: {"impressions": "展示次数", "clicks": "点击数", "ctr": "CTR", "position": "平均排名"}[x]
        )

        if detection_method == "Z-Score (标准差法)":
            threshold = st.sidebar.slider("Z-Score 阈值", 1.0, 4.0, 2.0, 0.1)
        elif detection_method == "IQR (四分位距法)":
            threshold = st.sidebar.slider("IQR 倍数", 1.0, 3.0, 1.5, 0.1)
        else:
            window_size = st.sidebar.slider("移动窗口大小 (天)", 3, 30, 7)
            threshold = st.sidebar.slider("偏离倍数", 1.0, 4.0, 2.0, 0.1)

        # 异常检测算法
        metric_data = df[metric_choice].values
        anomalies = np.zeros(len(metric_data), dtype=bool)
        anomaly_type = [''] * len(metric_data)

        if detection_method == "Z-Score (标准差法)":
            mean = np.mean(metric_data)
            std = np.std(metric_data)
            if std > 0:
                z_scores = (metric_data - mean) / std
                for i in range(len(z_scores)):
                    if abs(z_scores[i]) > threshold:
                        anomalies[i] = True
                        anomaly_type[i] = 'high' if z_scores[i] > 0 else 'low'

        elif detection_method == "IQR (四分位距法)":
            q1 = np.percentile(metric_data, 25)
            q3 = np.percentile(metric_data, 75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            for i in range(len(metric_data)):
                if metric_data[i] < lower_bound or metric_data[i] > upper_bound:
                    anomalies[i] = True
                    anomaly_type[i] = 'high' if metric_data[i] > upper_bound else 'low'

        else:
            for i in range(len(metric_data)):
                start_idx = max(0, i - window_size)
                window = metric_data[start_idx:i] if i > 0 else metric_data[0:1]
                if len(window) > 0:
                    window_mean = np.mean(window)
                    window_std = np.std(window) if len(window) > 1 else 1
                    if window_std > 0:
                        deviation = abs(metric_data[i] - window_mean) / window_std
                        if deviation > threshold:
                            anomalies[i] = True
                            anomaly_type[i] = 'high' if metric_data[i] > window_mean else 'low'

        df['is_anomaly'] = anomalies
        df['anomaly_type'] = anomaly_type

        # 异常统计概览
        total_anomalies = anomalies.sum()
        high_anomalies = sum(1 for t in anomaly_type if t == 'high')
        low_anomalies = sum(1 for t in anomaly_type if t == 'low')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(render_metric_card("总数据点", f"{len(df)}", "📊", COLORS['primary']), unsafe_allow_html=True)
        with col2:
            st.markdown(render_metric_card("异常点", f"{total_anomalies}", "⚠️", COLORS['warning']), unsafe_allow_html=True)
        with col3:
            st.markdown(render_metric_card("异常高值", f"{high_anomalies}", "🔺", COLORS['secondary']), unsafe_allow_html=True)
        with col4:
            st.markdown(render_metric_card("异常低值", f"{low_anomalies}", "🔻", "#FFA500"), unsafe_allow_html=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # 异常可视化
        st.markdown("#### 📈 异常点可视化")
        metric_labels = {"impressions": "展示次数", "clicks": "点击数", "ctr": "CTR", "position": "平均排名"}

        fig = go.Figure()

        # 正常数据
        normal_mask = ~df['is_anomaly']
        fig.add_trace(go.Scatter(
            x=df[normal_mask]['data_date'], y=df[normal_mask][metric_choice],
            mode='lines', name='正常数据',
            line=dict(color=COLORS['primary'], width=1.5)
        ))

        # 异常高值
        high_mask = df['anomaly_type'] == 'high'
        if high_mask.any():
            fig.add_trace(go.Scatter(
                x=df[high_mask]['data_date'], y=df[high_mask][metric_choice],
                mode='markers', name='异常高值 ↑',
                marker=dict(color=COLORS['secondary'], size=12, symbol='triangle-up',
                            line=dict(width=1, color='white'))
            ))

        # 异常低值
        low_mask = df['anomaly_type'] == 'low'
        if low_mask.any():
            fig.add_trace(go.Scatter(
                x=df[low_mask]['data_date'], y=df[low_mask][metric_choice],
                mode='markers', name='异常低值 ↓',
                marker=dict(color=COLORS['warning'], size=12, symbol='triangle-down',
                            line=dict(width=1, color='white'))
            ))

        # 阈值线
        if detection_method == "Z-Score (标准差法)":
            mean = np.mean(metric_data)
            std = np.std(metric_data)
            fig.add_hline(y=mean + threshold * std, line_dash="dash", line_color=COLORS['secondary'],
                          annotation_text=f"上界 (μ+{threshold}σ)", annotation_font_size=10)
            fig.add_hline(y=mean - threshold * std, line_dash="dash", line_color=COLORS['warning'],
                          annotation_text=f"下界 (μ-{threshold}σ)", annotation_font_size=10)
            fig.add_hline(y=mean, line_dash="dot", line_color="#999",
                          annotation_text="均值", annotation_font_size=10)
        elif detection_method == "IQR (四分位距法)":
            fig.add_hline(y=upper_bound, line_dash="dash", line_color=COLORS['secondary'],
                          annotation_text=f"上界 (Q3+{threshold}×IQR)", annotation_font_size=10)
            fig.add_hline(y=lower_bound, line_dash="dash", line_color=COLORS['warning'],
                          annotation_text=f"下界 (Q1-{threshold}×IQR)", annotation_font_size=10)

        fig = apply_chart_style(fig, height=450)
        fig.update_layout(
            xaxis_title="日期",
            yaxis_title=metric_labels[metric_choice]
        )
        st.plotly_chart(fig, use_container_width=True)

        # 异常事件列表
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 🚨 异常事件明细")

        if total_anomalies > 0:
            anomaly_df = df[df['is_anomaly']].copy()
            anomaly_df['日期'] = anomaly_df['data_date'].dt.strftime('%Y-%m-%d')
            anomaly_df['类型'] = anomaly_df['anomaly_type'].map({'high': '🔴 异常高值', 'low': '🟡 异常低值'})
            anomaly_df['指标值'] = anomaly_df[metric_choice].apply(
                lambda x: f"{x:.2f}" if metric_choice == 'ctr' else f"{int(x)}")

            def analyze_cause(row):
                if row['anomaly_type'] == 'high':
                    if metric_choice == 'impressions':
                        return "内容被推荐/热点关键词排名提升/季节性高峰"
                    elif metric_choice == 'clicks':
                        return "标题优化效果/排名大幅提升/外部引流"
                    elif metric_choice == 'position':
                        return "排名突然下降/算法更新影响"
                    else:
                        return "展示量下降但点击不变/标题吸引力提升"
                else:
                    if metric_choice == 'impressions':
                        return "算法更新/关键词排名下降/技术问题"
                    elif metric_choice == 'clicks':
                        return "排名下降/竞争对手优化/搜索意图变化"
                    elif metric_choice == 'position':
                        return "排名突然提升/竞争对手退出"
                    else:
                        return "展示量增加但点击未跟上/标题与意图不匹配"

            anomaly_df['可能原因'] = anomaly_df.apply(analyze_cause, axis=1)

            display_cols = ['日期', '类型', '指标值', '可能原因']
            st.dataframe(
                anomaly_df[display_cols].sort_values('日期', ascending=False),
                use_container_width=True, hide_index=True
            )

            # 异常分布统计
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("#### 📊 异常分布统计")

            col1, col2 = st.columns(2)
            with col1:
                anomaly_df['month'] = pd.to_datetime(anomaly_df['日期']).dt.to_period('M').astype(str)
                monthly_anomalies = anomaly_df.groupby('month').size().reset_index(name='异常数量')
                fig_monthly = px.bar(monthly_anomalies, x='month', y='异常数量',
                                     color_discrete_sequence=[COLORS['secondary']])
                fig_monthly = apply_chart_style(fig_monthly, height=300)
                fig_monthly.update_layout(title="月度异常数量")
                st.plotly_chart(fig_monthly, use_container_width=True)

            with col2:
                type_counts = anomaly_df['anomaly_type'].value_counts()
                fig_type = px.pie(values=type_counts.values,
                                  names=['异常高值' if n == 'high' else '异常低值' for n in type_counts.index],
                                  color_discrete_sequence=[COLORS['secondary'], COLORS['warning']],
                                  hole=0.4)
                fig_type.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', title="异常类型占比")
                st.plotly_chart(fig_type, use_container_width=True)
        else:
            st.success("✅ 未检测到异常数据点！当前数据表现稳定。")
            st.info("💡 提示：可以尝试降低检测阈值来发现更细微的波动。")

        # 检测方法说明
        with st.expander("📖 检测方法说明"):
            st.markdown("""
            | 方法 | 原理 | 适用场景 | 建议阈值 |
            |------|------|----------|----------|
            | **Z-Score** | 数据点偏离均值的标准差倍数 | 数据近似正态分布 | 2.0-2.5 |
            | **IQR** | 基于四分位距确定正常范围 | 有偏态分布的数据 | 1.5 |
            | **移动平均** | 与近期趋势对比偏离程度 | 有明显趋势的时序数据 | 2.0 |
            """)
    else:
        st.warning("未找到日期维度数据，请检查数据文件。")

