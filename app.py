
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================
# 多语言配置
# ============================================================
LANGUAGES = {
    "中文": {
        "title": "B2B独立站 SEO 健康度诊断工具",
        "subtitle": "基于 Google Search Console 数据",
        "nav_overview": "📊 总览仪表盘",
        "nav_health": "🎯 SEO 健康度评分",
        "nav_trend": "📈 搜索表现趋势",
        "nav_keyword": "🔍 关键词洞察",
        "nav_page": "📄 页面效果分析",
        "nav_country": "🌍 国家/地区分析",
        "nav_device": "📱 设备分布",
        "nav_anomaly": "🚨 流量异常检测",
        "nav_recommend": "🚀 优化建议",
        "total_clicks": "总点击数",
        "total_impressions": "总展示次数",
        "avg_ctr": "平均CTR",
        "avg_position": "平均排名",
        "health_score": "SEO 健康度评分",
        "grade": "等级",
        "score": "分",
        "search_perf": "搜索表现",
        "content_eff": "内容效果",
        "tech_exp": "技术体验信号",
        "data_range": "数据范围",
        "daily_trend": "每日趋势",
        "monthly_summary": "月度汇总",
        "clicks": "点击数",
        "impressions": "展示次数",
        "position": "排名",
        "country": "国家/地区",
        "device": "设备",
        "anomaly_detection": "流量异常检测",
        "recommendations": "优化建议",
        "keyword_insight": "关键词洞察",
        "page_analysis": "页面效果分析",
    },
    "English": {
        "title": "B2B SEO Health Diagnostic Tool",
        "subtitle": "Based on Google Search Console Data",
        "nav_overview": "📊 Overview Dashboard",
        "nav_health": "🎯 SEO Health Score",
        "nav_trend": "📈 Search Performance Trends",
        "nav_keyword": "🔍 Keyword Insights",
        "nav_page": "📄 Page Performance",
        "nav_country": "🌍 Country/Region Analysis",
        "nav_device": "📱 Device Distribution",
        "nav_anomaly": "🚨 Traffic Anomaly Detection",
        "nav_recommend": "🚀 Recommendations",
        "total_clicks": "Total Clicks",
        "total_impressions": "Total Impressions",
        "avg_ctr": "Average CTR",
        "avg_position": "Average Position",
        "health_score": "SEO Health Score",
        "grade": "Grade",
        "score": "Score",
        "search_perf": "Search Performance",
        "content_eff": "Content Effectiveness",
        "tech_exp": "Technical Experience",
        "data_range": "Data Range",
        "daily_trend": "Daily Trend",
        "monthly_summary": "Monthly Summary",
        "clicks": "Clicks",
        "impressions": "Impressions",
        "position": "Position",
        "country": "Country/Region",
        "device": "Device",
        "anomaly_detection": "Traffic Anomaly Detection",
        "recommendations": "Recommendations",
        "keyword_insight": "Keyword Insights",
        "page_analysis": "Page Performance",
    }
}

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
# 自定义CSS样式
# ============================================================
st.markdown("""
<style>
    /* 主题色 */
    :root {
        --primary: #1a73e8;
        --success: #34a853;
        --warning: #fbbc04;
        --danger: #ea4335;
        --bg-card: #ffffff;
        --bg-page: #f8f9fa;
    }
    /* 卡片样式 */
    .metric-card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid var(--primary);
    }
    .metric-card h3 {
        color: #5f6368;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 700;
        color: #202124;
    }
    /* 健康度等级颜色 */
    .grade-A { color: #34a853; }
    .grade-B { color: #1a73e8; }
    .grade-C { color: #fbbc04; }
    .grade-D { color: #ea4335; }
    /* 侧边栏 */
    .css-1d391kg { background-color: #f8f9fa; }
    /* 标题 */
    .main-title {
        font-size: 24px;
        font-weight: 700;
        color: #202124;
        margin-bottom: 4px;
    }
    .sub-title {
        font-size: 14px;
        color: #5f6368;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
    """加载所有CSV数据文件"""
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
# SEO 健康度评分计算（三维加权模型 V2.0）
# ============================================================
def calculate_health_score(data):
    """
    三维加权评分模型：
    - 搜索表现 (40%): CTR评分 + 排名评分 + 点击趋势评分
    - 内容效果 (35%): 关键词覆盖度 + 页面活跃率 + 地理覆盖度
    - 技术体验信号 (25%): 设备覆盖度 + 移动端占比合理性 + 数据连续性
    """
    scores = {}
    
    # === 维度1：搜索表现 (40%) ===
    search_scores = []
    
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        # CTR评分 (B2B基准: 2-3% 为良好)
        avg_ctr = df['ctr'].mean()
        ctr_score = min(100, (avg_ctr / 0.03) * 100)
        search_scores.append(ctr_score)
        
        # 排名评分 (前10为优秀，前20为良好)
        avg_pos = df['position'].mean()
        if avg_pos <= 10:
            pos_score = 100
        elif avg_pos <= 20:
            pos_score = 80 - (avg_pos - 10) * 2
        elif avg_pos <= 50:
            pos_score = 60 - (avg_pos - 20) * 1
        else:
            pos_score = max(10, 30 - (avg_pos - 50) * 0.5)
        search_scores.append(pos_score)
        
        # 点击趋势评分
        df_sorted = df.sort_values('data_date')
        if len(df_sorted) >= 4:
            recent = df_sorted.tail(len(df_sorted)//3)['clicks'].mean()
            earlier = df_sorted.head(len(df_sorted)//3)['clicks'].mean()
            if earlier > 0:
                trend_ratio = recent / earlier
                if trend_ratio >= 1.2:
                    trend_score = 90
                elif trend_ratio >= 0.8:
                    trend_score = 70
                elif trend_ratio >= 0.5:
                    trend_score = 50
                else:
                    trend_score = 30
            else:
                trend_score = 50
        else:
            trend_score = 50
        search_scores.append(trend_score)
    
    search_dim = np.mean(search_scores) if search_scores else 50
    scores['search_performance'] = round(search_dim, 1)
    
    # === 维度2：内容效果 (35%) ===
    content_scores = []
    
    if data.get('by_query') is not None:
        df_q = data['by_query']
        unique_queries = df_q['query'].nunique()
        # 关键词覆盖度 (500+为优秀，100+为良好)
        if unique_queries >= 500:
            kw_score = 90
        elif unique_queries >= 200:
            kw_score = 70 + (unique_queries - 200) / 300 * 20
        elif unique_queries >= 50:
            kw_score = 50 + (unique_queries - 50) / 150 * 20
        else:
            kw_score = max(20, unique_queries)
        content_scores.append(kw_score)
    
    if data.get('by_page') is not None:
        df_p = data['by_page']
        total_pages = df_p['page'].nunique()
        active_pages = df_p[df_p['clicks'] > 0]['page'].nunique()
        # 页面活跃率
        if total_pages > 0:
            active_rate = active_pages / total_pages
            page_score = min(100, active_rate * 100 * 2)
        else:
            page_score = 0
        content_scores.append(page_score)
    
    if data.get('by_country') is not None:
        df_c = data['by_country']
        unique_countries = df_c['country'].nunique()
        # 地理覆盖度 (50+国家为优秀)
        geo_score = min(100, (unique_countries / 50) * 100)
        content_scores.append(geo_score)
    
    content_dim = np.mean(content_scores) if content_scores else 50
    scores['content_effectiveness'] = round(content_dim, 1)
    
    # === 维度3：技术体验信号 (25%) ===
    tech_scores = []
    
    if data.get('by_device') is not None:
        df_d = data['by_device']
        devices = df_d['device'].nunique()
        # 设备覆盖度 (3种设备=满分)
        device_score = min(100, (devices / 3) * 100)
        tech_scores.append(device_score)
        
        # 移动端占比合理性 (B2B: 15-35%为合理)
        total_imp = df_d['impressions'].sum()
        if total_imp > 0:
            mobile_imp = df_d[df_d['device'] == 'MOBILE']['impressions'].sum()
            mobile_ratio = mobile_imp / total_imp
            if 0.15 <= mobile_ratio <= 0.35:
                mobile_score = 90
            elif 0.10 <= mobile_ratio <= 0.45:
                mobile_score = 70
            else:
                mobile_score = 50
        else:
            mobile_score = 50
        tech_scores.append(mobile_score)
    
    if data.get('by_date') is not None:
        df_date = data['by_date']
        # 数据连续性
        total_days = (df_date['data_date'].max() - df_date['data_date'].min()).days
        actual_days = df_date['data_date'].nunique()
        if total_days > 0:
            continuity = actual_days / total_days
            continuity_score = min(100, continuity * 100)
        else:
            continuity_score = 50
        tech_scores.append(continuity_score)
    
    tech_dim = np.mean(tech_scores) if tech_scores else 50
    scores['technical_experience'] = round(tech_dim, 1)
    
    # === 综合评分 ===
    total_score = (scores['search_performance'] * 0.40 +
                   scores['content_effectiveness'] * 0.35 +
                   scores['technical_experience'] * 0.25)
    scores['total'] = round(total_score, 1)
    
    # 等级判定
    if total_score >= 90:
        scores['grade'] = 'A'
        scores['grade_label'] = '优秀'
        scores['grade_label_en'] = 'Excellent'
    elif total_score >= 70:
        scores['grade'] = 'B'
        scores['grade_label'] = '良好'
        scores['grade_label_en'] = 'Good'
    elif total_score >= 50:
        scores['grade'] = 'C'
        scores['grade_label'] = '一般'
        scores['grade_label_en'] = 'Average'
    else:
        scores['grade'] = 'D'
        scores['grade_label'] = '较差'
        scores['grade_label_en'] = 'Poor'
    
    return scores

health_scores = calculate_health_score(data)

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    # 语言选择
    lang = st.selectbox("🌐 Language / 语言", list(LANGUAGES.keys()))
    t = LANGUAGES[lang]
    
    st.markdown(f"### {t['title']}")
    st.caption(t['subtitle'])
    st.markdown("---")
    
    # 导航菜单
    page = st.radio(
        "导航菜单" if lang == "中文" else "Navigation",
        [
            t['nav_overview'],
            t['nav_health'],
            t['nav_trend'],
            t['nav_keyword'],
            t['nav_page'],
            t['nav_country'],
            t['nav_device'],
            t['nav_anomaly'],
            t['nav_recommend'],
        ]
    )
    
    st.markdown("---")
    # 数据范围信息
    if data.get('by_date') is not None:
        min_date = data['by_date']['data_date'].min().strftime('%Y-%m-%d')
        max_date = data['by_date']['data_date'].max().strftime('%Y-%m-%d')
        st.caption(f"{t['data_range']}: {min_date} → {max_date}")
    
    st.markdown("---")
    st.caption("B2B SEO 健康度诊断工具 v2.0 | 基于 GSC 数据")

# ============================================================
# 页面1：总览仪表盘
# ============================================================
if page == t['nav_overview']:
    st.markdown(f"## {t['nav_overview']}")
    
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        total_clicks = int(df['clicks'].sum())
        total_impressions = int(df['impressions'].sum())
        avg_ctr = df['ctr'].mean() * 100
        avg_position = df['position'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t['total_clicks'], f"{total_clicks:,}")
        with col2:
            st.metric(t['total_impressions'], f"{total_impressions:,}")
        with col3:
            st.metric(t['avg_ctr'], f"{avg_ctr:.2f}%")
        with col4:
            st.metric(t['avg_position'], f"{avg_position:.1f}")
        
        st.markdown("---")
        
        # 健康度概览卡片
        col_a, col_b = st.columns([1, 2])
        with col_a:
            grade_color = {'A': '#34a853', 'B': '#1a73e8', 'C': '#fbbc04', 'D': '#ea4335'}
            color = grade_color.get(health_scores['grade'], '#000')
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background:#fff; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                <h3>{t['health_score']}</h3>
                <div style="font-size:64px; font-weight:700; color:{color};">{health_scores['grade']}</div>
                <div style="font-size:14px; color:#5f6368;">{health_scores['grade_label'] if lang=='中文' else health_scores['grade_label_en']}</div>
                <div style="font-size:24px; font-weight:600; margin-top:8px;">{health_scores['total']} / 100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            # 雷达图
            categories = [t['search_perf'], t['content_eff'], t['tech_exp']]
            values = [
                health_scores['search_performance'],
                health_scores['content_effectiveness'],
                health_scores['technical_experience']
            ]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(26, 115, 232, 0.2)',
                line=dict(color='#1a73e8', width=2),
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=300,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("未找到数据文件，请检查 data/ 文件夹。")

# ============================================================
# 页面2：SEO 健康度评分
# ============================================================
elif page == t['nav_health']:
    st.markdown(f"## {t['nav_health']}")
    
    # 总分展示
    grade_color = {'A': '#34a853', 'B': '#1a73e8', 'C': '#fbbc04', 'D': '#ea4335'}
    color = grade_color.get(health_scores['grade'], '#000')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:30px; background:#fff; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size:72px; font-weight:700; color:{color};">{health_scores['grade']}</div>
            <div style="font-size:16px; color:#5f6368;">{health_scores['grade_label'] if lang=='中文' else health_scores['grade_label_en']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:30px; background:#fff; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size:48px; font-weight:700;">{health_scores['total']}</div>
            <div style="font-size:16px; color:#5f6368;">/ 100 {t['score']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="padding:15px; background:#fff; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <p><strong>{t['search_perf']} (40%)</strong>: {health_scores['search_performance']}</p>
            <p><strong>{t['content_eff']} (35%)</strong>: {health_scores['content_effectiveness']}</p>
            <p><strong>{t['tech_exp']} (25%)</strong>: {health_scores['technical_experience']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 雷达图
    categories = [t['search_perf'], t['content_eff'], t['tech_exp']]
    values = [
        health_scores['search_performance'],
        health_scores['content_effectiveness'],
        health_scores['technical_experience']
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(26, 115, 232, 0.2)',
        line=dict(color='#1a73e8', width=2),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=400,
        title="各维度得分" if lang == "中文" else "Dimension Scores"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 评分说明
    with st.expander("📖 评分方法说明" if lang == "中文" else "📖 Scoring Methodology"):
        st.markdown("""
        **三维加权评分模型 V2.0**
        
        | 维度 | 权重 | 二级指标 |
        |------|------|----------|
        | 搜索表现 | 40% | CTR评分、排名评分、点击趋势 |
        | 内容效果 | 35% | 关键词覆盖度、页面活跃率、地理覆盖度 |
        | 技术体验信号 | 25% | 设备覆盖度、移动端占比、数据连续性 |
        
        **等级标准**: A(90-100) 优秀 | B(70-89) 良好 | C(50-69) 一般 | D(0-49) 较差
        
        **外链权威维度**: 预留接口，待接入 Ahrefs/Moz API 后启用
        """)

# ============================================================
# 页面3：搜索表现趋势
# ============================================================
elif page == t['nav_trend']:
    st.markdown(f"## {t['nav_trend']}")
    
    if data.get('daily_summary') is not None:
        df = data['daily_summary'].copy()
        df = df.sort_values('data_date')
        
        # 日期范围选择
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "开始日期" if lang == "中文" else "Start Date",
                value=df['data_date'].min().date()
            )
        with col2:
            end_date = st.date_input(
                "结束日期" if lang == "中文" else "End Date",
                value=df['data_date'].max().date()
            )
        
        # 筛选数据
        mask = (df['data_date'].dt.date >= start_date) & (df['data_date'].dt.date <= end_date)
        df_filtered = df[mask]
        
        if len(df_filtered) > 0:
            # 点击数 & 展示次数双轴图
            st.subheader(f"{t['clicks']} & {t['impressions']}" + (" 趋势" if lang == "中文" else " Trend"))
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=df_filtered['data_date'], y=df_filtered['impressions'],
                       name=t['impressions'], marker_color='rgba(26,115,232,0.3)'),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=df_filtered['data_date'], y=df_filtered['clicks'],
                          name=t['clicks'], line=dict(color='#ea4335', width=2)),
                secondary_y=True
            )
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
            fig.update_yaxes(title_text=t['impressions'], secondary_y=False)
            fig.update_yaxes(title_text=t['clicks'], secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # CTR 和排名趋势
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("CTR" + (" 趋势" if lang == "中文" else " Trend"))
                fig_ctr = px.line(df_filtered, x='data_date', y='ctr',
                                 line_shape='spline')
                fig_ctr.update_traces(line_color='#34a853')
                fig_ctr.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=20))
                st.plotly_chart(fig_ctr, use_container_width=True)
            
            with col_b:
                st.subheader(t['position'] + (" 趋势" if lang == "中文" else " Trend"))
                fig_pos = px.line(df_filtered, x='data_date', y='position',
                                 line_shape='spline')
                fig_pos.update_traces(line_color='#fbbc04')
                fig_pos.update_yaxes(autorange="reversed")
                fig_pos.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=20))
                st.plotly_chart(fig_pos, use_container_width=True)
            
            # 月度汇总
            st.markdown("---")
            st.subheader(t['monthly_summary'])
            df_filtered['month'] = df_filtered['data_date'].dt.to_period('M').astype(str)
            monthly = df_filtered.groupby('month').agg({
                'clicks': 'sum',
                'impressions': 'sum',
                'ctr': 'mean',
                'position': 'mean'
            }).reset_index()
            
            fig_monthly = go.Figure()
            fig_monthly.add_trace(go.Bar(
                x=monthly['month'], y=monthly['clicks'],
                name=t['clicks'], marker_color='#1a73e8'
            ))
            fig_monthly.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.warning("所选日期范围内无数据" if lang == "中文" else "No data in selected date range")
    else:
        st.warning("未找到日期维度数据" if lang == "中文" else "Date dimension data not found")

# ============================================================
# 页面4：关键词洞察
# ============================================================
elif page == t['nav_keyword']:
    st.markdown(f"## {t['nav_keyword']}")
    
    if data.get('by_query') is not None:
        df_q = data['by_query'].copy()
        
        # 关键词概览指标
        total_keywords = df_q['query'].nunique()
        keywords_with_clicks = df_q[df_q['clicks'] > 0]['query'].nunique()
        avg_position_kw = df_q['position'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("关键词总数" if lang == "中文" else "Total Keywords", f"{total_keywords:,}")
        with col2:
            st.metric("有点击关键词" if lang == "中文" else "Keywords with Clicks", f"{keywords_with_clicks:,}")
        with col3:
            st.metric("平均排名" if lang == "中文" else "Avg Position", f"{avg_position_kw:.1f}")
        
        st.markdown("---")
        
        # 关键词排名分布
        st.subheader("关键词排名分布" if lang == "中文" else "Keyword Position Distribution")
        df_q['position_bucket'] = pd.cut(
            df_q['position'],
            bins=[0, 3, 10, 20, 50, 100],
            labels=['Top 3', '4-10', '11-20', '21-50', '50+']
        )
        pos_dist = df_q['position_bucket'].value_counts().sort_index().reset_index()
        pos_dist.columns = ['Position Range', 'Count']
        
        fig_pos = px.bar(pos_dist, x='Position Range', y='Count',
                        color='Position Range',
                        color_discrete_sequence=['#34a853', '#1a73e8', '#fbbc04', '#ff6d01', '#ea4335'])
        fig_pos.update_layout(height=300, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pos, use_container_width=True)
        
        # 机会关键词（高展示低点击）
        st.markdown("---")
        st.subheader("🎯 " + ("机会关键词（高展示 + 低CTR）" if lang == "中文" else "Opportunity Keywords (High Impressions + Low CTR)"))
        
        # 按关键词聚合
        kw_agg = df_q.groupby('query').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean'
        }).reset_index()
        kw_agg['ctr'] = kw_agg['clicks'] / kw_agg['impressions'].replace(0, 1)
        
        # 筛选机会关键词：展示>10, CTR<2%, 排名11-30
        opportunity_kw = kw_agg[
            (kw_agg['impressions'] >= 10) &
            (kw_agg['ctr'] < 0.02) &
            (kw_agg['position'] >= 11) &
            (kw_agg['position'] <= 30)
        ].sort_values('impressions', ascending=False).head(20)
        
        if len(opportunity_kw) > 0:
            opportunity_kw['ctr_pct'] = (opportunity_kw['ctr'] * 100).round(2)
            opportunity_kw['position'] = opportunity_kw['position'].round(1)
            st.dataframe(
                opportunity_kw[['query', 'clicks', 'impressions', 'ctr_pct', 'position']].rename(
                    columns={
                        'query': '关键词' if lang == "中文" else 'Keyword',
                        'clicks': '点击' if lang == "中文" else 'Clicks',
                        'impressions': '展示' if lang == "中文" else 'Impressions',
                        'ctr_pct': 'CTR%',
                        'position': '排名' if lang == "中文" else 'Position'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("未发现符合条件的机会关键词" if lang == "中文" else "No opportunity keywords found")
        
        # Top 关键词表格
        st.markdown("---")
        st.subheader("🏆 Top " + ("关键词（按点击量）" if lang == "中文" else "Keywords (by Clicks)"))
        top_kw = kw_agg.sort_values('clicks', ascending=False).head(20)
        top_kw['ctr_pct'] = (top_kw['ctr'] * 100).round(2)
        top_kw['position'] = top_kw['position'].round(1)
        st.dataframe(
            top_kw[['query', 'clicks', 'impressions', 'ctr_pct', 'position']].rename(
                columns={
                    'query': '关键词' if lang == "中文" else 'Keyword',
                    'clicks': '点击' if lang == "中文" else 'Clicks',
                    'impressions': '展示' if lang == "中文" else 'Impressions',
                    'ctr_pct': 'CTR%',
                    'position': '排名' if lang == "中文" else 'Position'
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("未找到关键词数据（cleaned_by_query.csv）" if lang == "中文" else "Keyword data not found")

# ============================================================
# 页面5：页面效果分析
# ============================================================
elif page == t['nav_page']:
    st.markdown(f"## {t['nav_page']}")
    
    if data.get('by_page') is not None:
        df_p = data['by_page'].copy()
        
        # 页面概览
        total_pages = df_p['page'].nunique()
        pages_with_clicks = df_p[df_p['clicks'] > 0]['page'].nunique()
        active_rate = pages_with_clicks / total_pages * 100 if total_pages > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总页面数" if lang == "中文" else "Total Pages", f"{total_pages:,}")
        with col2:
            st.metric("有点击页面" if lang == "中文" else "Pages with Clicks", f"{pages_with_clicks:,}")
        with col3:
            st.metric("页面活跃率" if lang == "中文" else "Active Rate", f"{active_rate:.1f}%")
        
        st.markdown("---")
        
        # 页面机会矩阵
        st.subheader("📊 " + ("页面机会矩阵" if lang == "中文" else "Page Opportunity Matrix"))
        
        page_agg = df_p.groupby('page').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean'
        }).reset_index()
        page_agg['ctr'] = page_agg['clicks'] / page_agg['impressions'].replace(0, 1)
        
        # 只显示有一定展示量的页面
        page_matrix = page_agg[page_agg['impressions'] >= 5].copy()
        
        if len(page_matrix) > 0:
            # 散点图：展示 vs 点击，颜色=排名
            fig_matrix = px.scatter(
                page_matrix,
                x='impressions',
                y='clicks',
                color='position',
                size='impressions',
                hover_data=['page'],
                color_continuous_scale='RdYlGn_r',
                labels={
                    'impressions': '展示次数' if lang == "中文" else 'Impressions',
                    'clicks': '点击数' if lang == "中文" else 'Clicks',
                    'position': '排名' if lang == "中文" else 'Position'
                }
            )
            fig_matrix.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_matrix, use_container_width=True)
        
        # 高展示低点击页面（优化机会）
        st.markdown("---")
        st.subheader("🎯 " + ("高展示低CTR页面（优化机会）" if lang == "中文" else "High Impression Low CTR Pages (Opportunities)"))
        
        opportunity_pages = page_agg[
            (page_agg['impressions'] >= 20) &
            (page_agg['ctr'] < 0.01)
        ].sort_values('impressions', ascending=False).head(15)
        
        if len(opportunity_pages) > 0:
            opportunity_pages['ctr_pct'] = (opportunity_pages['ctr'] * 100).round(2)
            opportunity_pages['position'] = opportunity_pages['position'].round(1)
            # 简化URL显示
            opportunity_pages['short_page'] = opportunity_pages['page'].str.replace('https://www.advich.com', '', regex=False)
            st.dataframe(
                opportunity_pages[['short_page', 'clicks', 'impressions', 'ctr_pct', 'position']].rename(
                    columns={
                        'short_page': '页面路径' if lang == "中文" else 'Page Path',
                        'clicks': '点击' if lang == "中文" else 'Clicks',
                        'impressions': '展示' if lang == "中文" else 'Impressions',
                        'ctr_pct': 'CTR%',
                        'position': '排名' if lang == "中文" else 'Position'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("未发现符合条件的优化机会页面" if lang == "中文" else "No opportunity pages found")
        
        # Top 页面
        st.markdown("---")
        st.subheader("🏆 Top " + ("页面（按点击量）" if lang == "中文" else "Pages (by Clicks)"))
        top_pages = page_agg.sort_values('clicks', ascending=False).head(15)
        top_pages['ctr_pct'] = (top_pages['ctr'] * 100).round(2)
        top_pages['position'] = top_pages['position'].round(1)
        top_pages['short_page'] = top_pages['page'].str.replace('https://www.advich.com', '', regex=False)
        st.dataframe(
            top_pages[['short_page', 'clicks', 'impressions', 'ctr_pct', 'position']].rename(
                columns={
                    'short_page': '页面路径' if lang == "中文" else 'Page Path',
                    'clicks': '点击' if lang == "中文" else 'Clicks',
                    'impressions': '展示' if lang == "中文" else 'Impressions',
                    'ctr_pct': 'CTR%',
                    'position': '排名' if lang == "中文" else 'Position'
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("未找到页面数据（cleaned_by_page.csv）" if lang == "中文" else "Page data not found")

# ============================================================
# 页面6：国家/地区分析
# ============================================================
elif page == t['nav_country']:
    st.markdown(f"## {t['nav_country']}")
    
    if data.get('by_country') is not None:
        df_c = data['by_country'].copy()
        
        # 国家概览
        total_countries = df_c['country'].nunique()
        st.metric("覆盖国家/地区数" if lang == "中文" else "Countries/Regions Covered", total_countries)
        
        st.markdown("---")
        
        # 按国家聚合
        country_agg = df_c.groupby('country').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean'
        }).reset_index()
        country_agg['ctr'] = country_agg['clicks'] / country_agg['impressions'].replace(0, 1)
        country_agg = country_agg.sort_values('clicks', ascending=False)
        
        # Top 国家柱状图
        st.subheader("Top 15 " + ("国家/地区（按点击量）" if lang == "中文" else "Countries (by Clicks)"))
        top_countries = country_agg.head(15)
        
        fig_country = px.bar(
            top_countries,
            x='country',
            y='clicks',
            color='ctr',
            color_continuous_scale='Blues',
            labels={
                'country': t['country'],
                'clicks': t['clicks'],
                'ctr': 'CTR'
            }
        )
        fig_country.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_country, use_container_width=True)
        
        # 国家详细表格
        st.markdown("---")
        st.subheader("📋 " + ("详细数据" if lang == "中文" else "Detailed Data"))
        country_display = country_agg.head(30).copy()
        country_display['ctr_pct'] = (country_display['ctr'] * 100).round(2)
        country_display['position'] = country_display['position'].round(1)
        st.dataframe(
            country_display[['country', 'clicks', 'impressions', 'ctr_pct', 'position']].rename(
                columns={
                    'country': t['country'],
                    'clicks': t['clicks'],
                    'impressions': t['impressions'],
                    'ctr_pct': 'CTR%',
                    'position': t['position']
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("未找到国家维度数据" if lang == "中文" else "Country data not found")

# ============================================================
# 页面7：设备分布
# ============================================================
elif page == t['nav_device']:
    st.markdown(f"## {t['nav_device']}")
    
    if data.get('by_device') is not None:
        df_d = data['by_device'].copy()
        
        # 按设备聚合
        device_agg = df_d.groupby('device').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 展示次数饼图
            st.subheader(t['impressions'] + (" 占比" if lang == "中文" else " Share"))
            fig_pie = px.pie(
                device_agg,
                values='impressions',
                names='device',
                color_discrete_sequence=['#1a73e8', '#34a853', '#fbbc04']
            )
            fig_pie.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 点击数饼图
            st.subheader(t['clicks'] + (" 占比" if lang == "中文" else " Share"))
            fig_pie2 = px.pie(
                device_agg,
                values='clicks',
                names='device',
                color_discrete_sequence=['#1a73e8', '#34a853', '#fbbc04']
            )
            fig_pie2.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie2, use_container_width=True)
        
        st.markdown("---")
        
        # 设备对比表格
        st.subheader("📋 " + ("设备对比详情" if lang == "中文" else "Device Comparison"))
        device_agg['ctr_pct'] = (device_agg['ctr'] * 100).round(2)
        device_agg['position'] = device_agg['position'].round(1)
        st.dataframe(
            device_agg[['device', 'clicks', 'impressions', 'ctr_pct', 'position']].rename(
                columns={
                    'device': t['device'],
                    'clicks': t['clicks'],
                    'impressions': t['impressions'],
                    'ctr_pct': 'CTR%',
                    'position': t['position']
                }
            ),
            use_container_width=True,
            hide_index=True
        )
        
        # 设备月度趋势
        st.markdown("---")
        st.subheader("📈 " + ("设备月度趋势" if lang == "中文" else "Device Monthly Trend"))
        df_d['month'] = df_d['data_date'].dt.to_period('M').astype(str)
        device_monthly = df_d.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
        
        fig_device_trend = px.line(
            device_monthly,
            x='month',
            y='clicks',
            color='device',
            markers=True,
            color_discrete_sequence=['#1a73e8', '#34a853', '#fbbc04']
        )
        fig_device_trend.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_device_trend, use_container_width=True)
    else:
        st.warning("未找到设备维度数据" if lang == "中文" else "Device data not found")

# ============================================================
# 页面8：流量异常检测
# ============================================================
elif page == t['nav_anomaly']:
    st.markdown(f"## {t['nav_anomaly']}")
    
    if data.get('daily_summary') is not None:
        df = data['daily_summary'].copy()
        df = df.sort_values('data_date')
        
        # 异常检测参数
        st.sidebar.markdown("---")
        sensitivity = st.sidebar.slider(
            "灵敏度" if lang == "中文" else "Sensitivity",
            min_value=1.0, max_value=3.0, value=2.0, step=0.1
        )
        
        # 选择检测指标
        metric_options = {
            t['clicks']: 'clicks',
            t['impressions']: 'impressions',
            'CTR': 'ctr',
            t['position']: 'position'
        }
        selected_metric_label = st.selectbox(
            "选择检测指标" if lang == "中文" else "Select Metric",
            list(metric_options.keys())
        )
        selected_metric = metric_options[selected_metric_label]
        
        # Z-Score 异常检测
        df['rolling_mean'] = df[selected_metric].rolling(window=7, min_periods=1).mean()
        df['rolling_std'] = df[selected_metric].rolling(window=7, min_periods=1).std()
        df['z_score'] = (df[selected_metric] - df['rolling_mean']) / df['rolling_std'].replace(0, 1)
        df['is_anomaly'] = abs(df['z_score']) > sensitivity
        
        anomaly_count = df['is_anomaly'].sum()
        
        # 异常统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("检测天数" if lang == "中文" else "Days Analyzed", len(df))
        with col2:
            st.metric("异常点数" if lang == "中文" else "Anomalies Found", anomaly_count)
        with col3:
            anomaly_rate = anomaly_count / len(df) * 100 if len(df) > 0 else 0
            st.metric("异常率" if lang == "中文" else "Anomaly Rate", f"{anomaly_rate:.1f}%")
        
        st.markdown("---")
        
        # 异常可视化
        fig_anomaly = go.Figure()
        
        # 正常数据点
        normal_df = df[~df['is_anomaly']]
        fig_anomaly.add_trace(go.Scatter(
            x=normal_df['data_date'],
            y=normal_df[selected_metric],
            mode='lines',
            name='正常' if lang == "中文" else 'Normal',
            line=dict(color='#1a73e8', width=1.5)
        ))
        
        # 异常数据点
        anomaly_df = df[df['is_anomaly']]
        fig_anomaly.add_trace(go.Scatter(
            x=anomaly_df['data_date'],
            y=anomaly_df[selected_metric],
            mode='markers',
            name='异常' if lang == "中文" else 'Anomaly',
            marker=dict(color='#ea4335', size=10, symbol='x')
        ))
        
        # 均值线
        fig_anomaly.add_trace(go.Scatter(
            x=df['data_date'],
            y=df['rolling_mean'],
            mode='lines',
            name='7日均值' if lang == "中文" else '7-day Mean',
            line=dict(color='#34a853', width=1, dash='dash')
        ))
        
        fig_anomaly.update_layout(
            height=400,
            title=f"{selected_metric_label} " + ("异常检测结果" if lang == "中文" else "Anomaly Detection"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_anomaly, use_container_width=True)
        
        # 异常事件列表
        if anomaly_count > 0:
            st.markdown("---")
            st.subheader("📋 " + ("异常事件列表" if lang == "中文" else "Anomaly Events"))
            anomaly_display = anomaly_df[['data_date', selected_metric, 'rolling_mean', 'z_score']].copy()
            anomaly_display['data_date'] = anomaly_display['data_date'].dt.strftime('%Y-%m-%d')
            anomaly_display['z_score'] = anomaly_display['z_score'].round(2)
            anomaly_display['rolling_mean'] = anomaly_display['rolling_mean'].round(2)
            anomaly_display.columns = [
                '日期' if lang == "中文" else 'Date',
                '实际值' if lang == "中文" else 'Actual',
                '期望值' if lang == "中文" else 'Expected',
                'Z-Score'
            ]
            st.dataframe(anomaly_display, use_container_width=True, hide_index=True)
    else:
        st.warning("未找到日期维度数据" if lang == "中文" else "Date data not found")

# ============================================================
# 页面9：优化建议
# ============================================================
elif page == t['nav_recommend']:
    st.markdown(f"## {t['nav_recommend']}")
    
    recommendations = []
    
    # 基于评分生成建议
    if health_scores['search_performance'] < 70:
        recommendations.append({
            'priority': 'P1',
            'category': '搜索表现' if lang == "中文" else 'Search Performance',
            'issue': '平均排名偏低（23.8），CTR不足2%' if lang == "中文" else 'Low avg position (23.8), CTR below 2%',
            'action': '优化Title/Meta Description，针对排名11-20的关键词重点优化内容' if lang == "中文" else 'Optimize Title/Meta Description, focus on keywords ranked 11-20',
            'impact': '高' if lang == "中文" else 'High',
            'color': '#ea4335'
        })
    
    if health_scores['content_effectiveness'] < 80:
        recommendations.append({
            'priority': 'P2',
            'category': '内容效果' if lang == "中文" else 'Content Effectiveness',
            'issue': '页面活跃率偏低，大量页面零点击' if lang == "中文" else 'Low page active rate, many zero-click pages',
            'action': '合并或优化低质量页面，提升内容深度和相关性' if lang == "中文" else 'Merge or optimize low-quality pages, improve content depth',
            'impact': '中' if lang == "中文" else 'Medium',
            'color': '#fbbc04'
        })
    
    if health_scores['technical_experience'] < 80:
        recommendations.append({
            'priority': 'P3',
            'category': '技术体验' if lang == "中文" else 'Technical Experience',
            'issue': '移动端体验可能需要优化' if lang == "中文" else 'Mobile experience may need optimization',
            'action': '检查移动端页面加载速度，确保响应式设计正常' if lang == "中文" else 'Check mobile page load speed, ensure responsive design',
            'impact': '中' if lang == "中文" else 'Medium',
            'color': '#fbbc04'
        })
    
    # 基于数据分析的额外建议
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        df_sorted = df.sort_values('data_date')
        if len(df_sorted) >= 6:
            recent_clicks = df_sorted.tail(len(df_sorted)//3)['clicks'].mean()
            earlier_clicks = df_sorted.head(len(df_sorted)//3)['clicks'].mean()
            if earlier_clicks > 0 and recent_clicks / earlier_clicks < 0.5:
                recommendations.append({
                    'priority': 'P0',
                    'category': '流量趋势' if lang == "中文" else 'Traffic Trend',
                    'issue': '点击量呈明显下降趋势（近期较早期下降超50%）' if lang == "中文" else 'Clicks showing significant decline (>50% drop)',
                    'action': '紧急排查：检查是否有Google算法更新影响、是否有技术问题导致索引丢失' if lang == "中文" else 'Urgent: Check for Google algorithm updates, technical indexing issues',
                    'impact': '紧急' if lang == "中文" else 'Critical',
                    'color': '#ea4335'
                })
    
    if data.get('by_query') is not None:
        df_q = data['by_query']
        kw_agg = df_q.groupby('query').agg({'clicks': 'sum', 'impressions': 'sum', 'position': 'mean'}).reset_index()
        # 检查是否有大量"差一点"的关键词
        almost_there = kw_agg[(kw_agg['position'] >= 11) & (kw_agg['position'] <= 20) & (kw_agg['impressions'] >= 10)]
        if len(almost_there) > 10:
            recommendations.append({
                'priority': 'P1',
                'category': '快速见效机会' if lang == "中文" else 'Quick Win Opportunity',
                'issue': f'发现 {len(almost_there)} 个排名11-20的关键词，提升至首页即可获得显著流量' if lang == "中文" else f'Found {len(almost_there)} keywords ranked 11-20, pushing to page 1 will drive significant traffic',
                'action': '针对这些关键词优化对应页面内容、增加内链、优化标题标签' if lang == "中文" else 'Optimize corresponding pages, add internal links, improve title tags',
                'impact': '高' if lang == "中文" else 'High',
                'color': '#34a853'
            })
    
    # 显示建议
    if recommendations:
        # 按优先级排序
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))
        
        for i, rec in enumerate(recommendations):
            st.markdown(f"""
            <div style="padding:16px; margin-bottom:12px; background:#fff; border-radius:8px; 
                        border-left:4px solid {rec['color']}; box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:{rec['color']};">[{rec['priority']}] {rec['category']}</span>
                    <span style="font-size:12px; background:{rec['color']}20; color:{rec['color']}; 
                           padding:2px 8px; border-radius:4px;">{rec['impact']}</span>
                </div>
                <p style="margin:8px 0 4px 0; color:#202124;"><strong>{'问题' if lang=='中文' else 'Issue'}:</strong> {rec['issue']}</p>
                <p style="margin:0; color:#5f6368;"><strong>{'建议' if lang=='中文' else 'Action'}:</strong> {rec['action']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 " + ("当前SEO状况良好，暂无紧急优化建议！" if lang == "中文" else "Current SEO status is good, no urgent recommendations!"))
    
    # 外链权威预留说明
    st.markdown("---")
    with st.expander("🔗 " + ("外链权威维度（待接入）" if lang == "中文" else "Backlink Authority (Coming Soon)")):
        st.info(
            "外链权威维度已预留接口，待接入 Ahrefs/Moz API 后将自动纳入评分体系。届时权重将调整为：搜索表现35% + 内容效果30% + 技术体验20% + 外链权威15%"
            if lang == "中文" else
            "Backlink authority dimension is reserved. Once Ahrefs/Moz API is integrated, weights will adjust to: Search 35% + Content 30% + Technical 20% + Backlinks 15%"
        )
