
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="B2B SEO Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 多语言配置 ====================
TRANSLATIONS = {
    '中文': {
        'title': 'B2B独立站 SEO 健康度诊断',
        'nav_overview': '📊 总览仪表盘',
        'nav_health': '🎯 SEO 健康度评分',
        'nav_trends': '📈 搜索表现趋势',
        'nav_keywords': '🔍 关键词洞察',
        'nav_pages': '📄 页面效果分析',
        'nav_country': '🌍 国家/地区分析',
        'nav_device': '📱 设备分布',
        'nav_anomaly': '🚨 流量异常检测',
        'nav_recommend': '🚀 优化建议',
        'total_clicks': '总点击数',
        'total_impressions': '总展示次数',
        'avg_ctr': '平均CTR',
        'avg_position': '平均排名',
        'health_score': 'SEO 健康度评分',
        'grade': '等级',
        'search_perf': '搜索表现',
        'content_eff': '内容效果',
        'tech_exp': '技术体验',
        'data_range': '数据范围',
        'no_data': '未找到数据，请检查数据文件。',
        'lang_label': '语言 / Language'
    },
    'English': {
        'title': 'B2B SEO Health Dashboard',
        'nav_overview': '📊 Overview',
        'nav_health': '🎯 SEO Health Score',
        'nav_trends': '📈 Search Trends',
        'nav_keywords': '🔍 Keyword Insights',
        'nav_pages': '📄 Page Analysis',
        'nav_country': '🌍 Country/Region',
        'nav_device': '📱 Device Distribution',
        'nav_anomaly': '🚨 Anomaly Detection',
        'nav_recommend': '🚀 Recommendations',
        'total_clicks': 'Total Clicks',
        'total_impressions': 'Total Impressions',
        'avg_ctr': 'Avg CTR',
        'avg_position': 'Avg Position',
        'health_score': 'SEO Health Score',
        'grade': 'Grade',
        'search_perf': 'Search Performance',
        'content_eff': 'Content Effectiveness',
        'tech_exp': 'Technical Experience',
        'data_range': 'Data Range',
        'no_data': 'No data found. Please check data files.',
        'lang_label': '语言 / Language'
    }
}

# ==================== 自定义CSS ====================
st.markdown("""
<style>
    /* 全局字体 */
    html, body, [class*="css"] {
        font-size: 14px;
    }
    /* 侧边栏 */
    .css-1d391kg { padding-top: 1rem; }
    /* 指标卡片 */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .metric-card h3 {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
    }
    /* 评分卡片 */
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .score-card .grade {
        font-size: 64px;
        font-weight: 800;
    }
    .score-card .score-num {
        font-size: 24px;
        opacity: 0.9;
    }
    /* 节标题 */
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    /* 间距 */
    .spacer { margin-top: 24px; }
    .spacer-sm { margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

# ==================== 数据加载 ====================
@st.cache_data
def load_data():
    """加载所有CSV数据文件"""
    data = {}
    base_path = "data/"
    
    file_mapping = {
        'by_date': 'cleaned_by_date.csv',
        'by_country': 'cleaned_by_country.csv',
        'by_device': 'cleaned_by_device.csv',
        'by_query': 'cleaned_by_query.csv',
        'by_page': 'cleaned_by_page.csv',
        'daily_summary': 'cleaned_daily_summary.csv',
        'date_query': 'cleaned_date_query.csv',
        'date_page': 'cleaned_date_page.csv',
        'query_country': 'cleaned_query_country.csv',
        'query_device': 'cleaned_query_device.csv',
        'query_page': 'cleaned_query_page.csv',
        'page_country': 'cleaned_page_country.csv',
        'page_device': 'cleaned_page_device.csv'
    }
    
    for key, filename in file_mapping.items():
        try:
            df = pd.read_csv(base_path + filename)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            if 'month' in df.columns:
                df['month'] = pd.to_datetime(df['month'], errors='coerce')
            data[key] = df
        except FileNotFoundError:
            data[key] = pd.DataFrame()
    
    return data

# ==================== 评分模型 ====================
def calculate_seo_score(data, lang='中文'):
    """计算SEO健康度评分 - V3.0 三维加权模型（纯加权，无惩罚因子）"""
    scores = {}
    
    # ===== 维度1：搜索表现 (40%) =====
    sp_scores = []
    
    if 'daily_summary' in data and not data['daily_summary'].empty:
        ds = data['daily_summary']
        
        # 1. CTR评分 (目标: >3% 满分)
        avg_ctr = ds['ctr'].mean() * 100 if ds['ctr'].mean() < 1 else ds['ctr'].mean()
        ctr_score = min(100, (avg_ctr / 3.0) * 100)
        sp_scores.append(ctr_score)
        
        # 2. 排名评分 (目标: <10 满分)
        avg_position = ds['position'].mean()
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
        sp_scores.append(position_score)
        
        # 3. 点击趋势评分
        if len(ds) >= 2:
            first_half = ds.head(len(ds)//2)['clicks'].mean()
            second_half = ds.tail(len(ds)//2)['clicks'].mean()
            if first_half > 0:
                trend_ratio = second_half / first_half
                trend_score = min(100, trend_ratio * 100)
            else:
                trend_score = 50
        else:
            trend_score = 50
        sp_scores.append(trend_score)
    
    search_performance = np.mean(sp_scores) if sp_scores else 50
    scores['search_performance'] = round(search_performance, 1)
    
    # ===== 维度2：内容效果 (35%) =====
    ce_scores = []
    
    if 'by_query' in data and not data['by_query'].empty:
        keyword_count = data['by_query']['query'].nunique() if 'query' in data['by_query'].columns else len(data['by_query'])
        keyword_score = min(100, (keyword_count / 500) * 100)
        ce_scores.append(keyword_score)
    
    if 'by_country' in data and not data['by_country'].empty:
        country_col = 'country' if 'country' in data['by_country'].columns else data['by_country'].columns[0]
        country_count = data['by_country'][country_col].nunique()
        geo_score = min(100, (country_count / 50) * 100)
        ce_scores.append(geo_score)
        
        if 'clicks' in data['by_country'].columns:
            active_countries = data['by_country'][data['by_country']['clicks'] > 0][country_col].nunique()
            total_countries = data['by_country'][country_col].nunique()
            active_rate = (active_countries / total_countries * 100) if total_countries > 0 else 0
            active_score = min(100, active_rate * 1.3)
            ce_scores.append(active_score)
    
    content_effectiveness = np.mean(ce_scores) if ce_scores else 50
    scores['content_effectiveness'] = round(content_effectiveness, 1)
    
    # ===== 维度3：技术体验信号 (25%) =====
    te_scores = []
    
    if 'by_device' in data and not data['by_device'].empty:
        device_col = 'device' if 'device' in data['by_device'].columns else data['by_device'].columns[0]
        device_count = data['by_device'][device_col].nunique()
        device_score = min(100, (device_count / 3) * 100)
        te_scores.append(device_score)
        
        if 'clicks' in data['by_device'].columns:
            total_clicks = data['by_device']['clicks'].sum()
            if total_clicks > 0:
                mobile_data = data['by_device'][data['by_device'][device_col].str.lower().str.contains('mobile', na=False)]
                mobile_ratio = mobile_data['clicks'].sum() / total_clicks * 100
                if 15 <= mobile_ratio <= 30:
                    mobile_score = 100
                elif 10 <= mobile_ratio < 15 or 30 < mobile_ratio <= 40:
                    mobile_score = 80
                else:
                    mobile_score = 60
            else:
                mobile_score = 50
        else:
            mobile_score = 50
        te_scores.append(mobile_score)
        
        if 'ctr' in data['by_device'].columns:
            device_ctrs = data['by_device'].groupby(device_col)['ctr'].mean()
            if len(device_ctrs) > 1:
                ctr_std = device_ctrs.std()
                consistency_score = max(0, 100 - ctr_std * 1000)
            else:
                consistency_score = 70
        else:
            consistency_score = 70
        te_scores.append(consistency_score)
    
    technical_experience = np.mean(te_scores) if te_scores else 50
    scores['technical_experience'] = round(technical_experience, 1)
    
    # ===== 最终加权评分（纯加权平均，无惩罚因子）=====
    final_score = (
        scores['search_performance'] * 0.40 +
        scores['content_effectiveness'] * 0.35 +
        scores['technical_experience'] * 0.25
    )
    final_score = round(final_score, 2)
    
    # 等级判定
    if final_score >= 90:
        grade, grade_label = 'A', ('优秀' if lang == '中文' else 'Excellent')
        grade_color = '#10b981'
    elif final_score >= 70:
        grade, grade_label = 'B', ('良好' if lang == '中文' else 'Good')
        grade_color = '#3b82f6'
    elif final_score >= 50:
        grade, grade_label = 'C', ('一般' if lang == '中文' else 'Average')
        grade_color = '#f59e0b'
    else:
        grade, grade_label = 'D', ('较差' if lang == '中文' else 'Poor')
        grade_color = '#ef4444'
    
    return {
        'total_score': final_score,
        'grade': grade,
        'grade_label': grade_label,
        'grade_color': grade_color,
        'dimensions': scores,
        'weights': {'search_performance': 40, 'content_effectiveness': 35, 'technical_experience': 25}
    }

# ==================== 加载数据 ====================
data = load_data()

# ==================== 侧边栏 ====================
with st.sidebar:
    lang = st.selectbox(
        '语言 / Language',
        ['中文', 'English'],
        key='lang_selector'
    )
    t = TRANSLATIONS[lang]
    
    st.markdown(f"### {t['title']}")
    st.markdown("---")
    
    page = st.radio(
        "导航菜单" if lang == '中文' else "Navigation",
        [
            t['nav_overview'],
            t['nav_health'],
            t['nav_trends'],
            t['nav_keywords'],
            t['nav_pages'],
            t['nav_country'],
            t['nav_device'],
            t['nav_anomaly'],
            t['nav_recommend']
        ],
        key='nav_radio'
    )
    
    st.markdown("---")
    if 'by_date' in data and not data['by_date'].empty and 'date' in data['by_date'].columns:
        date_col = data['by_date']['date'].dropna()
        if not date_col.empty:
            st.caption(f"{t['data_range']}: {date_col.min().strftime('%Y-%m-%d')} ~ {date_col.max().strftime('%Y-%m-%d')}")
    
    st.caption("B2B SEO Health Dashboard v3.0 | Based on GSC Data")

# ==================== 页面1：总览仪表盘 ====================
if page == t['nav_overview']:
    st.markdown(f"## {t['nav_overview']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    # 核心指标卡片
    if 'daily_summary' in data and not data['daily_summary'].empty:
        ds = data['daily_summary']
        total_clicks = int(ds['clicks'].sum())
        total_impressions = int(ds['impressions'].sum())
        avg_ctr = ds['ctr'].mean() * 100 if ds['ctr'].mean() < 1 else ds['ctr'].mean()
        avg_position = ds['position'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['total_clicks']}</h3>
                <div class="value">{total_clicks:,}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['total_impressions']}</h3>
                <div class="value">{total_impressions:,}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['avg_ctr']}</h3>
                <div class="value">{avg_ctr:.2f}%</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['avg_position']}</h3>
                <div class="value">{avg_position:.1f}</div>
            </div>""", unsafe_allow_html=True)
        
        # 健康度评分摘要
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        score_result = calculate_seo_score(data, lang)
        
        col_score, col_radar = st.columns([1, 2])
        with col_score:
            st.markdown(f"""
            <div class="score-card">
                <div class="grade">{score_result['grade']}</div>
                <div class="score-num">{score_result['total_score']} / 100</div>
                <div style="margin-top:8px;opacity:0.8;">{score_result['grade_label']}</div>
            </div>""", unsafe_allow_html=True)
        
        with col_radar:
            dims = score_result['dimensions']
            labels = [t['search_perf'], t['content_eff'], t['tech_exp']]
            values = [dims['search_performance'], dims['content_effectiveness'], dims['technical_experience']]
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=labels + [labels[0]],
                fill='toself',
                fillcolor='rgba(99,102,241,0.2)',
                line=dict(color='#6366f1', width=2),
                marker=dict(size=8)
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=11))),
                showlegend=False,
                margin=dict(t=30, b=30, l=60, r=60),
                height=300,
                font=dict(size=13)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # 趋势概览
        st.markdown(f'<div class="section-title">{"📈 近期趋势" if lang == "中文" else "📈 Recent Trends"}</div>', unsafe_allow_html=True)
        
        if 'date' in ds.columns:
            ds_sorted = ds.sort_values('date')
            fig_overview = make_subplots(specs=[[{"secondary_y": True}]])
            fig_overview.add_trace(
                go.Bar(x=ds_sorted['date'], y=ds_sorted['impressions'], name='Impressions', marker_color='#e2e8f0', opacity=0.7),
                secondary_y=False
            )
            fig_overview.add_trace(
                go.Scatter(x=ds_sorted['date'], y=ds_sorted['clicks'], name='Clicks', line=dict(color='#6366f1', width=2.5), mode='lines'),
                secondary_y=True
            )
            fig_overview.update_layout(
                height=300,
                margin=dict(t=20, b=40, l=50, r=50),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12)),
                font=dict(size=12),
                hovermode='x unified'
            )
            fig_overview.update_xaxes(tickfont=dict(size=11))
            fig_overview.update_yaxes(title_text="Impressions", tickfont=dict(size=11), secondary_y=False)
            fig_overview.update_yaxes(title_text="Clicks", tickfont=dict(size=11), secondary_y=True)
            st.plotly_chart(fig_overview, use_container_width=True)
    else:
        st.warning(t['no_data'])

# ==================== 页面2：SEO 健康度评分 ====================
elif page == t['nav_health']:
    st.markdown(f"## {t['nav_health']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score(data, lang)
    
    # 评分卡片
    st.markdown(f"""
    <div class="score-card">
        <div class="grade">{score_result['grade']}</div>
        <div class="score-num">{score_result['total_score']} / 100</div>
        <div style="margin-top:8px;opacity:0.8;">{score_result['grade_label']}</div>
    </div>""", unsafe_allow_html=True)
    
    # 维度详情
    dims = score_result['dimensions']
    weights = score_result['weights']
    
    col1, col2, col3 = st.columns(3)
    dim_items = [
        (col1, t['search_perf'], dims['search_performance'], weights['search_performance'], '#6366f1'),
        (col2, t['content_eff'], dims['content_effectiveness'], weights['content_effectiveness'], '#10b981'),
        (col3, t['tech_exp'], dims['technical_experience'], weights['technical_experience'], '#f59e0b')
    ]
    
    for col, name, score, weight, color in dim_items:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{name} ({weight}%)</h3>
                <div class="value" style="color:{color};">{score}</div>
            </div>""", unsafe_allow_html=True)
    
    # 雷达图
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    labels = [t['search_perf'], t['content_eff'], t['tech_exp']]
    values = [dims['search_performance'], dims['content_effectiveness'], dims['technical_experience']]
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(99,102,241,0.2)',
        line=dict(color='#6366f1', width=2.5),
        marker=dict(size=8)
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=12))),
        showlegend=False,
        height=400,
        margin=dict(t=40, b=40, l=80, r=80),
        font=dict(size=13)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # 评分说明
    st.markdown(f'<div class="section-title">{"📋 评分说明" if lang == "中文" else "📋 Scoring Details"}</div>', unsafe_allow_html=True)
    scoring_df = pd.DataFrame({
        ('维度' if lang == '中文' else 'Dimension'): [t['search_perf'], t['content_eff'], t['tech_exp']],
        ('权重' if lang == '中文' else 'Weight'): ['40%', '35%', '25%'],
        ('得分' if lang == '中文' else 'Score'): [dims['search_performance'], dims['content_effectiveness'], dims['technical_experience']],
        ('加权得分' if lang == '中文' else 'Weighted'): [
            round(dims['search_performance'] * 0.4, 1),
            round(dims['content_effectiveness'] * 0.35, 1),
            round(dims['technical_experience'] * 0.25, 1)
        ]
    })
    st.dataframe(scoring_df, use_container_width=True, hide_index=True)

# ==================== 页面3：搜索表现趋势 ====================
elif page == t['nav_trends']:
    st.markdown(f"## {t['nav_trends']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    if 'by_date' in data and not data['by_date'].empty:
        df = data['by_date'].copy()
        if 'date' in df.columns:
            df = df.sort_values('date')
            
            # 日期筛选
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input(
                    "开始日期" if lang == '中文' else "Start Date",
                    value=df['date'].min(),
                    key='trend_start'
                )
            with col_end:
                end_date = st.date_input(
                    "结束日期" if lang == '中文' else "End Date",
                    value=df['date'].max(),
                    key='trend_end'
                )
            
            mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
            df_filtered = df[mask]
            
            if not df_filtered.empty:
                # 股市风格趋势图：点击量 + 7日均线
                df_filtered = df_filtered.copy()
                df_filtered['clicks_ma7'] = df_filtered['clicks'].rolling(window=7, min_periods=1).mean()
                df_filtered['impressions_ma7'] = df_filtered['impressions'].rolling(window=7, min_periods=1).mean()
                
                # 点击趋势（股市风格）
                st.markdown(f'<div class="section-title">{"📈 点击量趋势（含7日均线）" if lang == "中文" else "📈 Clicks Trend (with 7-day MA)"}</div>', unsafe_allow_html=True)
                
                fig_clicks = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
                
                # 上图：点击量K线风格
                fig_clicks.add_trace(
                    go.Bar(x=df_filtered['date'], y=df_filtered['clicks'], name='Clicks', marker_color='rgba(99,102,241,0.4)'),
                    row=1, col=1
                )
                fig_clicks.add_trace(
                    go.Scatter(x=df_filtered['date'], y=df_filtered['clicks_ma7'], name='MA7',
                              line=dict(color='#6366f1', width=2.5), mode='lines'),
                    row=1, col=1
                )
                
                # 下图：成交量风格（展示次数）
                fig_clicks.add_trace(
                    go.Bar(x=df_filtered['date'], y=df_filtered['impressions'], name='Impressions', marker_color='rgba(148,163,184,0.5)'),
                    row=2, col=1
                )
                
                fig_clicks.update_layout(
                    height=450,
                    margin=dict(t=20, b=40, l=50, r=30),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12)),
                    font=dict(size=12),
                    hovermode='x unified',
                    showlegend=True
                )
                fig_clicks.update_xaxes(tickfont=dict(size=11))
                fig_clicks.update_yaxes(title_text="Clicks", tickfont=dict(size=11), row=1, col=1)
                fig_clicks.update_yaxes(title_text="Impressions", tickfont=dict(size=11), row=2, col=1)
                st.plotly_chart(fig_clicks, use_container_width=True)
                
                # CTR & Position 趋势
                st.markdown(f'<div class="section-title">{"📊 CTR & 排名趋势" if lang == "中文" else "📊 CTR & Position Trend"}</div>', unsafe_allow_html=True)
                
                fig_ctr = make_subplots(specs=[[{"secondary_y": True}]])
                fig_ctr.add_trace(
                    go.Scatter(x=df_filtered['date'], y=df_filtered['ctr'] * 100 if df_filtered['ctr'].max() < 1 else df_filtered['ctr'],
                              name='CTR %', line=dict(color='#10b981', width=2), mode='lines'),
                    secondary_y=False
                )
                fig_ctr.add_trace(
                    go.Scatter(x=df_filtered['date'], y=df_filtered['position'],
                              name='Position', line=dict(color='#f59e0b', width=2, dash='dot'), mode='lines'),
                    secondary_y=True
                )
                fig_ctr.update_layout(
                    height=300,
                    margin=dict(t=20, b=40, l=50, r=50),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12)),
                    font=dict(size=12),
                    hovermode='x unified'
                )
                fig_ctr.update_yaxes(title_text="CTR (%)", tickfont=dict(size=11), secondary_y=False)
                fig_ctr.update_yaxes(title_text="Position", tickfont=dict(size=11), autorange="reversed", secondary_y=True)
                st.plotly_chart(fig_ctr, use_container_width=True)
    else:
        st.warning(t['no_data'])

# ==================== 页面4：关键词洞察 ====================
elif page == t['nav_keywords']:
    st.markdown(f"## {t['nav_keywords']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    if 'by_query' in data and not data['by_query'].empty:
        df_query = data['by_query'].copy()
        
        # 关键词概览
        total_keywords = len(df_query)
        avg_clicks = df_query['clicks'].mean() if 'clicks' in df_query.columns else 0
        avg_impressions = df_query['impressions'].mean() if 'impressions' in df_query.columns else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"关键词总数" if lang == "中文" else "Total Keywords"}</h3>
                <div class="value">{total_keywords:,}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"平均点击" if lang == "中文" else "Avg Clicks"}</h3>
                <div class="value">{avg_clicks:.1f}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"平均展示" if lang == "中文" else "Avg Impressions"}</h3>
                <div class="value">{avg_impressions:.0f}</div>
            </div>""", unsafe_allow_html=True)
        
        # Top 关键词表格
        st.markdown(f'<div class="section-title">{"🏆 Top 20 关键词" if lang == "中文" else "🏆 Top 20 Keywords"}</div>', unsafe_allow_html=True)
        top_queries = df_query.nlargest(20, 'clicks') if 'clicks' in df_query.columns else df_query.head(20)
        display_cols = [c for c in ['query', 'clicks', 'impressions', 'ctr', 'position'] if c in top_queries.columns]
        st.dataframe(top_queries[display_cols], use_container_width=True, hide_index=True)
        
        # 关键词分布散点图
        st.markdown(f'<div class="section-title">{"📊 关键词机会矩阵" if lang == "中文" else "📊 Keyword Opportunity Matrix"}</div>', unsafe_allow_html=True)
        
        if 'impressions' in df_query.columns and 'position' in df_query.columns:
            df_plot = df_query[df_query['impressions'] > 0].copy()
            if not df_plot.empty:
                fig_scatter = px.scatter(
                    df_plot.head(200),
                    x='impressions',
                    y='position',
                    size='clicks' if 'clicks' in df_plot.columns else None,
                    hover_data=['query'] if 'query' in df_plot.columns else None,
                    color='ctr' if 'ctr' in df_plot.columns else None,
                    color_continuous_scale='Viridis'
                )
                fig_scatter.update_yaxes(autorange="reversed")
                fig_scatter.update_layout(
                    height=400,
                    margin=dict(t=20, b=40, l=50, r=30),
                    font=dict(size=12),
                    xaxis=dict(title="Impressions", tickfont=dict(size=11)),
                    yaxis=dict(title="Position", tickfont=dict(size=11))
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # 机会提示
                if 'position' in df_plot.columns and 'impressions' in df_plot.columns:
                    opportunities = df_plot[(df_plot['position'] > 10) & (df_plot['position'] <= 20) & (df_plot['impressions'] > 50)]
                    if not opportunities.empty:
                        st.info(f"{'🎯 发现' if lang == '中文' else '🎯 Found'} **{len(opportunities)}** {'个高潜力关键词（排名11-20，展示>50）' if lang == '中文' else ' high-potential keywords (position 11-20, impressions > 50)'}")
    else:
        st.info("📂 " + ("需要 cleaned_by_query.csv 数据文件" if lang == '中文' else "Requires cleaned_by_query.csv data file"))


# ==================== 页面5：页面效果分析 ====================
elif page == t['nav_pages']:
    st.markdown(f"## {t['nav_pages']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    if 'by_page' in data and not data['by_page'].empty:
        df_page = data['by_page'].copy()
        
        # 页面概览
        total_pages = len(df_page)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"收录页面数" if lang == "中文" else "Indexed Pages"}</h3>
                <div class="value">{total_pages:,}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            avg_page_clicks = df_page['clicks'].mean() if 'clicks' in df_page.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"页均点击" if lang == "中文" else "Avg Clicks/Page"}</h3>
                <div class="value">{avg_page_clicks:.1f}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            avg_page_ctr = df_page['ctr'].mean() * 100 if 'ctr' in df_page.columns and df_page['ctr'].mean() < 1 else df_page['ctr'].mean() if 'ctr' in df_page.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"页均CTR" if lang == "中文" else "Avg CTR/Page"}</h3>
                <div class="value">{avg_page_ctr:.2f}%</div>
            </div>""", unsafe_allow_html=True)
        
        # Top 页面
        st.markdown(f'<div class="section-title">{"🏆 Top 15 页面" if lang == "中文" else "🏆 Top 15 Pages"}</div>', unsafe_allow_html=True)
        top_pages = df_page.nlargest(15, 'clicks') if 'clicks' in df_page.columns else df_page.head(15)
        display_cols = [c for c in ['page', 'clicks', 'impressions', 'ctr', 'position'] if c in top_pages.columns]
        st.dataframe(top_pages[display_cols], use_container_width=True, hide_index=True)
        
        # 页面机会矩阵
        st.markdown(f'<div class="section-title">{"📊 页面机会矩阵" if lang == "中文" else "📊 Page Opportunity Matrix"}</div>', unsafe_allow_html=True)
        if 'impressions' in df_page.columns and 'ctr' in df_page.columns:
            df_plot = df_page[df_page['impressions'] > 10].copy()
            if not df_plot.empty:
                df_plot['ctr_pct'] = df_plot['ctr'] * 100 if df_plot['ctr'].max() < 1 else df_plot['ctr']
                fig_page = px.scatter(
                    df_plot.head(100),
                    x='impressions',
                    y='ctr_pct',
                    size='clicks' if 'clicks' in df_plot.columns else None,
                    color='position' if 'position' in df_plot.columns else None,
                    color_continuous_scale='RdYlGn_r',
                    hover_data=['page'] if 'page' in df_plot.columns else None
                )
                fig_page.update_layout(
                    height=400,
                    margin=dict(t=20, b=40, l=50, r=30),
                    font=dict(size=12),
                    xaxis=dict(title="Impressions", tickfont=dict(size=11)),
                    yaxis=dict(title="CTR (%)", tickfont=dict(size=11))
                )
                st.plotly_chart(fig_page, use_container_width=True)
                
                # 高展示低CTR页面提示
                high_imp_low_ctr = df_plot[(df_plot['impressions'] > 100) & (df_plot['ctr_pct'] < 1.5)]
                if not high_imp_low_ctr.empty:
                    st.warning(f"{'⚠️ 发现' if lang == '中文' else '⚠️ Found'} **{len(high_imp_low_ctr)}** {'个高展示低CTR页面，建议优化标题和描述' if lang == '中文' else ' high-impression low-CTR pages, consider optimizing titles and descriptions'}")
    else:
        st.info("📂 " + ("需要 cleaned_by_page.csv 数据文件" if lang == '中文' else "Requires cleaned_by_page.csv data file"))

# ==================== 页面6：国家/地区分析 ====================
elif page == t['nav_country']:
    st.markdown(f"## {t['nav_country']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    if 'by_country' in data and not data['by_country'].empty:
        df_country = data['by_country'].copy()
        country_col = 'country' if 'country' in df_country.columns else df_country.columns[0]
        
        # 国家概览
        total_countries = df_country[country_col].nunique()
        active_countries = df_country[df_country['clicks'] > 0][country_col].nunique() if 'clicks' in df_country.columns else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"覆盖国家数" if lang == "中文" else "Countries Covered"}</h3>
                <div class="value">{total_countries}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"活跃市场" if lang == "中文" else "Active Markets"}</h3>
                <div class="value">{active_countries}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            active_rate = round(active_countries / total_countries * 100, 1) if total_countries > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>{"活跃率" if lang == "中文" else "Active Rate"}</h3>
                <div class="value">{active_rate}%</div>
            </div>""", unsafe_allow_html=True)
        
        # 世界地图（对数色阶 + 国家代码大写）
        st.markdown(f'<div class="section-title">{"🗺️ 全球流量分布" if lang == "中文" else "🗺️ Global Traffic Distribution"}</div>', unsafe_allow_html=True)
        
        if 'clicks' in df_country.columns:
            # 按国家汇总
            map_data = df_country.groupby(country_col).agg({'clicks': 'sum', 'impressions': 'sum'}).reset_index()
            map_data = map_data[map_data['clicks'] > 0]
            # 国家代码转大写
            map_data[country_col] = map_data[country_col].str.upper()
            # 对数变换解决数据偏斜
            map_data['clicks_log'] = np.log1p(map_data['clicks'])
            
            fig_map = px.choropleth(
                map_data,
                locations=country_col,
                locationmode='ISO-3',
                color='clicks_log',
                hover_name=country_col,
                hover_data={'clicks': True, 'clicks_log': False},
                color_continuous_scale='Blues',
                labels={'clicks_log': 'Log(Clicks)', 'clicks': 'Clicks'}
            )
            fig_map.update_layout(
                height=450,
                margin=dict(t=20, b=20, l=0, r=0),
                font=dict(size=12),
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    coastlinecolor='#e2e8f0',
                    projection_type='natural earth',
                    bgcolor='rgba(0,0,0,0)'
                ),
                coloraxis_colorbar=dict(
                    title="Clicks (log)",
                    tickfont=dict(size=11),
                    titlefont=dict(size=12)
                )
            )
            st.plotly_chart(fig_map, use_container_width=True)
        
        # Top 国家柱状图
        st.markdown(f'<div class="section-title">{"📊 Top 10 国家/地区" if lang == "中文" else "📊 Top 10 Countries"}</div>', unsafe_allow_html=True)
        
        top_countries = df_country.groupby(country_col).agg({'clicks': 'sum', 'impressions': 'sum'}).reset_index()
        top_countries = top_countries.nlargest(10, 'clicks')
        
        fig_bar = px.bar(
            top_countries,
            x=country_col,
            y='clicks',
            color='impressions',
            color_continuous_scale='Blues',
            text='clicks'
        )
        fig_bar.update_traces(textposition='outside', textfont_size=12)
        fig_bar.update_layout(
            height=350,
            margin=dict(t=20, b=40, l=50, r=30),
            font=dict(size=12),
            xaxis=dict(title="", tickfont=dict(size=12)),
            yaxis=dict(title="Clicks", tickfont=dict(size=11)),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # 国家分布饼图（带旋转动画）
        st.markdown(f'<div class="section-title">{"🥧 流量占比" if lang == "中文" else "🥧 Traffic Share"}</div>', unsafe_allow_html=True)
        
        fig_country_pie = px.pie(
            top_countries,
            values='clicks',
            names=country_col,
            hole=0.4
        )
        fig_country_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12,
            rotation=120,
            pull=[0.05, 0.03, 0.02, 0.01, 0.01, 0, 0, 0, 0, 0][:len(top_countries)]
        )
        fig_country_pie.update_layout(
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
            font=dict(size=12),
            showlegend=True,
            legend=dict(font=dict(size=11))
        )
        st.plotly_chart(fig_country_pie, use_container_width=True)
    else:
        st.warning(t['no_data'])

# ==================== 页面7：设备分布 ====================
elif page == t['nav_device']:
    st.markdown(f"## {t['nav_device']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    if 'by_device' in data and not data['by_device'].empty:
        df_device = data['by_device'].copy()
        device_col = 'device' if 'device' in df_device.columns else df_device.columns[0]
        
        # 设备汇总
        device_summary = df_device.groupby(device_col).agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        }).reset_index()
        
        # 设备指标卡片
        cols = st.columns(len(device_summary))
        for i, (_, row) in enumerate(device_summary.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{row[device_col]}</h3>
                    <div class="value">{int(row['clicks']):,}</div>
                    <div style="color:#64748b;font-size:12px;">clicks</div>
                </div>""", unsafe_allow_html=True)
        
        # 设备分布饼图（带旋转动画）
        st.markdown(f'<div class="section-title">{"📊 设备流量占比" if lang == "中文" else "📊 Device Traffic Share"}</div>', unsafe_allow_html=True)
        
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            fig_pie = px.pie(
                device_summary,
                values='clicks',
                names=device_col,
                hole=0.4,
                color_discrete_sequence=['#6366f1', '#10b981', '#f59e0b']
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=13,
                rotation=90,
                pull=[0.05, 0.02, 0.02][:len(device_summary)]
            )
            fig_pie.update_layout(
                height=320,
                margin=dict(t=20, b=20, l=20, r=20),
                font=dict(size=12),
                showlegend=True,
                legend=dict(font=dict(size=12))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_bar:
            # CTR对比柱状图
            fig_ctr_bar = px.bar(
                device_summary,
                x=device_col,
                y='ctr',
                color=device_col,
                color_discrete_sequence=['#6366f1', '#10b981', '#f59e0b'],
                text=device_summary['ctr'].apply(lambda x: f"{x*100:.2f}%" if x < 1 else f"{x:.2f}%")
            )
            fig_ctr_bar.update_traces(textposition='outside', textfont_size=12)
            fig_ctr_bar.update_layout(
                height=320,
                margin=dict(t=20, b=40, l=50, r=30),
                font=dict(size=12),
                xaxis=dict(title="", tickfont=dict(size=12)),
                yaxis=dict(title="CTR", tickfont=dict(size=11)),
                showlegend=False
            )
            st.plotly_chart(fig_ctr_bar, use_container_width=True)
        
        # 设备趋势（按月）
        if 'month' in df_device.columns:
            st.markdown(f'<div class="section-title">{"📈 设备趋势变化" if lang == "中文" else "📈 Device Trend"}</div>', unsafe_allow_html=True)
            
            device_trend = df_device.groupby([df_device['month'].dt.to_period('M').astype(str), device_col])['clicks'].sum().reset_index()
            device_trend.columns = ['month', 'device', 'clicks']
            
            fig_device_trend = px.line(
                device_trend,
                x='month',
                y='clicks',
                color='device',
                markers=True,
                color_discrete_sequence=['#6366f1', '#10b981', '#f59e0b']
            )
            fig_device_trend.update_layout(
                height=300,
                margin=dict(t=20, b=40, l=50, r=30),
                font=dict(size=12),
                xaxis=dict(title="", tickfont=dict(size=11)),
                yaxis=dict(title="Clicks", tickfont=dict(size=11)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12))
            )
            st.plotly_chart(fig_device_trend, use_container_width=True)
    else:
        st.warning(t['no_data'])

# ==================== 页面8：流量异常检测 ====================
elif page == t['nav_anomaly']:
    st.markdown(f"## {t['nav_anomaly']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    if 'by_date' in data and not data['by_date'].empty:
        df = data['by_date'].copy()
        
        if 'date' in df.columns:
            df = df.sort_values('date')
            
            # 选择检测指标
            metric_options = {'clicks': '点击数' if lang == '中文' else 'Clicks',
                           'impressions': '展示数' if lang == '中文' else 'Impressions'}
            selected_metric = st.selectbox(
                "选择检测指标" if lang == '中文' else "Select Metric",
                list(metric_options.keys()),
                format_func=lambda x: metric_options[x],
                key='anomaly_metric'
            )
            
            # 选择检测灵敏度
            sensitivity = st.slider(
                "检测灵敏度（标准差倍数）" if lang == '中文' else "Sensitivity (std multiplier)",
                min_value=1.0, max_value=3.0, value=2.0, step=0.5,
                key='anomaly_sensitivity'
            )
            
            # Z-Score 异常检测
            df['rolling_mean'] = df[selected_metric].rolling(window=7, min_periods=1).mean()
            df['rolling_std'] = df[selected_metric].rolling(window=7, min_periods=1).std()
            df['z_score'] = (df[selected_metric] - df['rolling_mean']) / df['rolling_std'].replace(0, 1)
            df['is_anomaly'] = abs(df['z_score']) > sensitivity
            
            anomaly_count = df['is_anomaly'].sum()
            
            # 异常统计
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"检测天数" if lang == "中文" else "Days Analyzed"}</h3>
                    <div class="value">{len(df)}</div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"异常点数" if lang == "中文" else "Anomalies Found"}</h3>
                    <div class="value" style="color:#ef4444;">{anomaly_count}</div>
                </div>""", unsafe_allow_html=True)
            with col3:
                anomaly_rate = round(anomaly_count / len(df) * 100, 1) if len(df) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"异常率" if lang == "中文" else "Anomaly Rate"}</h3>
                    <div class="value">{anomaly_rate}%</div>
                </div>""", unsafe_allow_html=True)
            
            # 异常可视化
            st.markdown(f'<div class="section-title">{"📊 异常检测结果" if lang == "中文" else "📊 Anomaly Detection Results"}</div>', unsafe_allow_html=True)
            
            fig_anomaly = go.Figure()
            
            # 正常数据点
            normal_df = df[~df['is_anomaly']]
            fig_anomaly.add_trace(go.Scatter(
                x=normal_df['date'], y=normal_df[selected_metric],
                mode='lines', name='Normal',
                line=dict(color='#6366f1', width=1.5)
            ))
            
            # 异常数据点
            anomaly_df = df[df['is_anomaly']]
            fig_anomaly.add_trace(go.Scatter(
                x=anomaly_df['date'], y=anomaly_df[selected_metric],
                mode='markers', name='Anomaly',
                marker=dict(color='#ef4444', size=10, symbol='x')
            ))
            
            # 均线和置信区间
            fig_anomaly.add_trace(go.Scatter(
                x=df['date'], y=df['rolling_mean'],
                mode='lines', name='MA7',
                line=dict(color='#10b981', width=2, dash='dash')
            ))
            
            upper_bound = df['rolling_mean'] + sensitivity * df['rolling_std']
            lower_bound = df['rolling_mean'] - sensitivity * df['rolling_std']
            
            fig_anomaly.add_trace(go.Scatter(
                x=pd.concat([df['date'], df['date'][::-1]]),
                y=pd.concat([upper_bound, lower_bound[::-1]]),
                fill='toself',
                fillcolor='rgba(99,102,241,0.1)',
                line=dict(color='rgba(0,0,0,0)'),
                name='Confidence Band',
                showlegend=True
            ))
            
            fig_anomaly.update_layout(
                height=400,
                margin=dict(t=20, b=40, l=50, r=30),
                font=dict(size=12),
                xaxis=dict(title="", tickfont=dict(size=11)),
                yaxis=dict(title=metric_options[selected_metric], tickfont=dict(size=11)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12)),
                hovermode='x unified'
            )
            st.plotly_chart(fig_anomaly, use_container_width=True)
            
            # 异常事件列表
            if anomaly_count > 0:
                st.markdown(f'<div class="section-title">{"🚨 异常事件列表" if lang == "中文" else "🚨 Anomaly Events"}</div>', unsafe_allow_html=True)
                anomaly_display = anomaly_df[['date', selected_metric, 'rolling_mean', 'z_score']].copy()
                anomaly_display.columns = ['Date', metric_options[selected_metric], 'Expected (MA7)', 'Z-Score']
                anomaly_display['Z-Score'] = anomaly_display['Z-Score'].round(2)
                st.dataframe(anomaly_display, use_container_width=True, hide_index=True)
    else:
        st.warning(t['no_data'])

# ==================== 页面9：优化建议 ====================
elif page == t['nav_recommend']:
    st.markdown(f"## {t['nav_recommend']}")
    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score(data, lang)
    dims = score_result['dimensions']
    
    # 优先级排序
    dim_names = {
        'search_performance': t['search_perf'],
        'content_effectiveness': t['content_eff'],
        'technical_experience': t['tech_exp']
    }
    
    sorted_dims = sorted(dims.items(), key=lambda x: x[1])
    
    st.markdown(f"""
    <div class="metric-card" style="text-align:left;">
        <h3>{"🎯 当前评分" if lang == "中文" else "🎯 Current Score"}: {score_result['total_score']} ({score_result['grade']} - {score_result['grade_label']})</h3>
        <div style="color:#64748b;font-size:13px;margin-top:8px;">
            {"以下建议按优先级排序，优先改善得分最低的维度" if lang == "中文" else "Recommendations sorted by priority, focusing on lowest-scoring dimensions"}
        </div>
    </div>""", unsafe_allow_html=True)
    
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    
    # 按维度生成建议
    for i, (dim_key, dim_score) in enumerate(sorted_dims):
        priority = f"P{i}" if lang == 'English' else f"优先级{i}"
        dim_name = dim_names[dim_key]
        
        if dim_score >= 80:
            status = "✅"
            status_text = "表现良好" if lang == '中文' else "Good"
        elif dim_score >= 60:
            status = "⚠️"
            status_text = "需要改善" if lang == '中文' else "Needs Improvement"
        else:
            status = "🚨"
            status_text = "急需优化" if lang == '中文' else "Critical"
        
        st.markdown(f'<div class="section-title">{status} {dim_name} — {dim_score}分 ({status_text})</div>', unsafe_allow_html=True)
        
        if dim_key == 'search_performance':
            if lang == '中文':
                recommendations = [
                    "**关键词排名优化**：当前平均排名23.8，目标进入前10。建议针对排名11-20的高展示关键词进行内容优化。",
                    "**CTR提升**：当前CTR 1.53%，行业基准2-3%。建议优化Title和Meta Description，加入数字、年份、行动号召词。",
                    "**点击趋势逆转**：近期点击量呈下降趋势，建议排查是否有页面被降权或索引问题。"
                ]
            else:
                recommendations = [
                    "**Keyword Ranking**: Average position 23.8, target top 10. Focus on optimizing content for keywords ranked 11-20 with high impressions.",
                    "**CTR Improvement**: Current CTR 1.53%, benchmark 2-3%. Optimize titles and meta descriptions with numbers, dates, and CTAs.",
                    "**Click Trend Reversal**: Recent declining trend in clicks. Investigate potential deindexing or ranking drops."
                ]
        elif dim_key == 'content_effectiveness':
            if lang == '中文':
                recommendations = [
                    "**关键词覆盖扩展**：当前覆盖关键词数量良好，建议继续拓展长尾关键词内容。",
                    "**地理市场深耕**：覆盖201个国家，但活跃市场集中在中国、香港、美国。建议针对高潜力市场（新加坡、台湾）创建本地化内容。",
                    "**内容更新频率**：定期更新高流量页面内容，保持搜索引擎新鲜度信号。"
                ]
            else:
                recommendations = [
                    "**Keyword Coverage**: Good coverage, continue expanding long-tail keyword content.",
                    "**Geographic Expansion**: Covering 201 countries but active in few. Create localized content for high-potential markets (Singapore, Taiwan).",
                    "**Content Freshness**: Regularly update high-traffic pages to maintain freshness signals."
                ]
        else:
            if lang == '中文':
                recommendations = [
                    "**移动端体验**：移动端占比17.9%，符合B2B特征。确保移动端页面加载速度和交互体验。",
                    "**设备CTR一致性**：各设备CTR存在差异，建议检查移动端和桌面端的展示效果是否一致。",
                    "**Core Web Vitals**：建议通过PageSpeed Insights检测并优化LCP、FID、CLS指标。"
                ]
            else:
                recommendations = [
                    "**Mobile Experience**: Mobile share 17.9%, typical for B2B. Ensure mobile page speed and interaction quality.",
                    "**Device CTR Consistency**: CTR varies across devices. Check if mobile and desktop display quality is consistent.",
                    "**Core Web Vitals**: Use PageSpeed Insights to optimize LCP, FID, and CLS metrics."
                ]
        
        for rec in recommendations:
            st.markdown(f"- {rec}")
        st.markdown("")
    
    # 外链权威（预留）
    st.markdown(f'<div class="section-title">{"🔗 外链权威（待启用）" if lang == "中文" else "🔗 Backlink Authority (Coming Soon)"}</div>', unsafe_allow_html=True)
    st.info("💡 " + ("该维度预留15%权重，待接入Ahrefs/Moz API后自动启用。届时评分模型将升级为四维加权。" if lang == '中文' else "This dimension reserves 15% weight. Will be activated after integrating Ahrefs/Moz API, upgrading to a 4-dimension model."))

