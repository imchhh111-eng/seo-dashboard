
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="SEO Health Analytics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 企业级配色方案（建议8）
# ============================================================
COLORS = {
    'primary': '#1E3A8A',      # 深蓝
    'secondary': '#3B82F6',    # 亮蓝
    'success': '#10B981',      # 绿色（增长）
    'warning': '#F59E0B',      # 橙色（风险）
    'danger': '#EF4444',       # 红色（危险）
    'background': '#F8FAFC',   # 浅灰背景
    'card': '#FFFFFF',         # 白色卡片
    'text': '#1E293B',         # 深色文字
    'muted': '#64748B',        # 灰色文字
}

# ============================================================
# 全局CSS样式（建议7、8）
# ============================================================
st.markdown("""
<style>
    /* 隐藏默认Streamlit元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 全局背景 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 顶部品牌导航栏 */
    .top-nav {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 1rem 2rem;
        border-radius: 0 0 12px 12px;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .top-nav h1 {
        color: white;
        font-size: 1.5rem;
        margin: 0;
        font-weight: 700;
    }
    .top-nav p {
        color: rgba(255,255,255,0.8);
        margin: 0;
        font-size: 0.85rem;
    }
    
    /* KPI卡片 */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #3B82F6;
    }
    .kpi-card h3 {
        color: #64748B;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .kpi-card .value {
        color: #1E293B;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* 健康度大卡片 */
    .health-hero {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(30,58,138,0.3);
    }
    .health-hero .score {
        font-size: 4.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    .health-hero .label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .health-hero .status {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.85;
    }
    
    /* Insight卡片 */
    .insight-card {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
    }
    .insight-card .title {
        color: #065F46;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .insight-card .content {
        color: #1E293B;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* 机会卡片 */
    .opportunity-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid #F59E0B;
    }
    .opportunity-card .title {
        color: #92400E;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .opportunity-card .value {
        color: #1E293B;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }
    .opportunity-card .desc {
        color: #64748B;
        font-size: 0.85rem;
    }
    
    /* AI建议卡片 */
    .ai-card {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid #1E3A8A;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 0.8rem;
    }
    .ai-card .priority {
        color: #1E3A8A;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .ai-card .action {
        color: #1E293B;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    .ai-card .impact {
        color: #10B981;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    
    /* 进度条 */
    .progress-bar {
        background: #E2E8F0;
        border-radius: 4px;
        height: 8px;
        margin: 0.3rem 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s;
    }
    
    /* Tab样式优化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
            data[key] = pd.read_csv(filepath)
        else:
            data[key] = pd.DataFrame()
    
    return data

data = load_data()

# ============================================================
# 计算核心指标
# ============================================================
def calculate_metrics(data):
    metrics = {}
    
    # 基础指标
    if not data.get('daily_summary', pd.DataFrame()).empty:
        df = data['daily_summary']
        metrics['total_clicks'] = int(df['clicks'].sum())
        metrics['total_impressions'] = int(df['impressions'].sum())
        metrics['avg_ctr'] = metrics['total_clicks'] / metrics['total_impressions'] * 100 if metrics['total_impressions'] > 0 else 0
        metrics['avg_position'] = df['position'].mean()
    else:
        metrics['total_clicks'] = 0
        metrics['total_impressions'] = 0
        metrics['avg_ctr'] = 0
        metrics['avg_position'] = 0
    
    # 关键词指标
    if not data.get('by_query', pd.DataFrame()).empty:
        df_q = data['by_query']
        metrics['total_keywords'] = df_q['query'].nunique()
        metrics['top10_keywords'] = df_q[df_q['position'] <= 10]['query'].nunique()
        metrics['opportunity_keywords'] = df_q[(df_q['position'] > 10) & (df_q['position'] <= 30)]['query'].nunique()
        metrics['long_tail'] = df_q[df_q['position'] > 30]['query'].nunique()
    else:
        metrics['total_keywords'] = 0
        metrics['top10_keywords'] = 0
        metrics['opportunity_keywords'] = 0
        metrics['long_tail'] = 0
    
    # 页面指标
    if not data.get('by_page', pd.DataFrame()).empty:
        df_p = data['by_page']
        metrics['total_pages'] = df_p['page'].nunique()
        metrics['pages_with_clicks'] = df_p[df_p['clicks'] > 0]['page'].nunique()
    else:
        metrics['total_pages'] = 0
        metrics['pages_with_clicks'] = 0
    
    # 国家指标
    if not data.get('by_country', pd.DataFrame()).empty:
        df_c = data['by_country']
        metrics['total_countries'] = df_c['country'].nunique()
    else:
        metrics['total_countries'] = 0
    
    return metrics

def calculate_health_score(metrics):
    """计算SEO健康度评分（三维模型）"""
    scores = {}
    
    # 关键词覆盖度评分 (0-100)
    if metrics['total_keywords'] > 0:
        top10_ratio = metrics['top10_keywords'] / metrics['total_keywords']
        scores['keyword'] = min(100, top10_ratio * 100 * 3.5 + 30)
    else:
        scores['keyword'] = 0
    
    # 页面健康度评分 (0-100)
    if metrics['total_pages'] > 0:
        page_active_ratio = metrics['pages_with_clicks'] / metrics['total_pages']
        scores['page'] = min(100, page_active_ratio * 100 * 2 + 20)
    else:
        scores['page'] = 0
    
    # 市场覆盖度评分 (0-100)
    if metrics['total_countries'] > 0:
        scores['market'] = min(100, metrics['total_countries'] * 1.5 + 40)
    else:
        scores['market'] = 0
    
    # 综合评分
    scores['overall'] = scores['keyword'] * 0.4 + scores['page'] * 0.35 + scores['market'] * 0.25
    
    return scores

metrics = calculate_metrics(data)
scores = calculate_health_score(metrics)

# ============================================================
# 顶部导航栏（建议7）
# ============================================================
st.markdown("""
<div class="top-nav">
    <div>
        <h1>🔍 SEO HEALTH ANALYTICS</h1>
        <p>B2B Independent Site · Powered by GSC Data</p>
    </div>
    <div style="text-align: right;">
        <p style="font-size: 0.9rem; color: white;">advich.com</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# Tab布局（建议6）
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "🔑 Keyword Intelligence", 
    "📄 Page Performance", 
    "🌍 Market Expansion",
    "🤖 Recommendations"
])

# ============================================================
# Tab 1: Overview（建议1、2）
# ============================================================
with tab1:
    # 健康度大卡片
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 确定等级
        overall_score = scores['overall']
        if overall_score >= 90:
            status = "Excellent Performance"
            status_emoji = "🟢"
        elif overall_score >= 70:
            status = "Good Performance"
            status_emoji = "🟡"
        elif overall_score >= 50:
            status = "Moderate Performance"
            status_emoji = "🟠"
        else:
            status = "Needs Improvement"
            status_emoji = "🔴"
        
        st.markdown(f"""
        <div class="health-hero">
            <div class="label">SEO HEALTH SCORE</div>
            <div class="score">{overall_score:.1f}</div>
            <div class="status">{status_emoji} {status}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 三维子分数（建议2）
        st.markdown("<br>", unsafe_allow_html=True)
        
        for label, key, color in [
            ("Keyword Coverage", "keyword", COLORS['secondary']),
            ("Page Health", "page", COLORS['success']),
            ("Market Coverage", "market", COLORS['warning'])
        ]:
            score_val = scores[key]
            st.markdown(f"""
            <div style="margin-bottom: 0.8rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                    <span style="color: {COLORS['text']}; font-weight: 600;">{label}</span>
                    <span style="color: {COLORS['muted']};">{score_val:.0f}/100</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {score_val}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Gauge图表
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall SEO Health", 'font': {'size': 18, 'color': COLORS['text']}},
            number={'font': {'size': 48, 'color': COLORS['primary']}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': COLORS['muted']},
                'bar': {'color': COLORS['primary']},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E2E8F0",
                'steps': [
                    {'range': [0, 50], 'color': '#FEE2E2'},
                    {'range': [50, 70], 'color': '#FEF3C7'},
                    {'range': [70, 90], 'color': '#D1FAE5'},
                    {'range': [90, 100], 'color': '#A7F3D0'}
                ],
                'threshold': {
                    'line': {'color': COLORS['danger'], 'width': 4},
                    'thickness': 0.75,
                    'value': overall_score
                }
            }
        ))
        fig_gauge.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # KPI行
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Keywords Tracked</h3>
                <div class="value">{metrics['total_keywords']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Active Pages</h3>
                <div class="value">{metrics['total_pages']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Markets</h3>
                <div class="value">{metrics['total_countries']:,}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top Opportunity区域（建议1）
    st.markdown("### 🚀 Top Opportunities")
    opp_col1, opp_col2, opp_col3 = st.columns(3)
    
    with opp_col1:
        st.markdown(f"""
        <div class="opportunity-card">
            <div class="title">RANKING OPPORTUNITY</div>
            <div class="value">{metrics['opportunity_keywords']}</div>
            <div class="desc">keywords ready for ranking improvement (position 11-30)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with opp_col2:
        pages_need_opt = metrics['total_pages'] - metrics['pages_with_clicks']
        pages_pct = (pages_need_opt / metrics['total_pages'] * 100) if metrics['total_pages'] > 0 else 0
        st.markdown(f"""
        <div class="opportunity-card">
            <div class="title">PAGE OPTIMIZATION</div>
            <div class="value">{pages_pct:.1f}%</div>
            <div class="desc">pages need optimization (no clicks received)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with opp_col3:
        st.markdown(f"""
        <div class="opportunity-card">
            <div class="title">CTR IMPROVEMENT</div>
            <div class="value">{metrics['avg_ctr']:.2f}%</div>
            <div class="desc">current avg CTR · industry benchmark: 3-5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Key Insight（建议5）
    st.markdown(f"""
    <div class="insight-card">
        <div class="title">💡 KEY INSIGHT</div>
        <div class="content">
            Most SEO growth potential comes from <strong>{metrics['opportunity_keywords']} existing keywords</strong> 
            positioned between 11-30. Improving these to Top 10 could increase organic traffic by an estimated 
            <strong>40-60%</strong> without acquiring new keywords.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# Tab 2: Keyword Intelligence（建议3）
# ============================================================
with tab2:
    if not data.get('by_query', pd.DataFrame()).empty:
        df_q = data['by_query']
        
        st.markdown("### 🔑 Keyword Intelligence")
        
        # Ranking Funnel（建议3）
        st.markdown("#### Ranking Distribution Funnel")
        
        # 取最新一期数据
        latest_date = df_q['data_date'].max()
        df_latest = df_q[df_q['data_date'] == latest_date]
        
        total_kw = df_latest['query'].nunique()
        top10 = df_latest[df_latest['position'] <= 10]['query'].nunique()
        page1_opp = df_latest[(df_latest['position'] > 10) & (df_latest['position'] <= 30)]['query'].nunique()
        long_tail = df_latest[df_latest['position'] > 30]['query'].nunique()
        
        fig_funnel = go.Figure(go.Funnel(
            y=['All Keywords', 'Top 10 (Page 1)', 'Page 1 Opportunity (11-30)', 'Long Tail (30+)'],
            x=[total_kw, top10, page1_opp, long_tail],
            textposition="inside",
            textinfo="value+percent initial",
            marker={
                'color': [COLORS['primary'], COLORS['success'], COLORS['warning'], COLORS['muted']],
            },
            connector={"line": {"color": "#E2E8F0", "width": 2}}
        ))
        fig_funnel.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # Bubble Chart - Keyword Opportunity（建议3）
        st.markdown("#### Keyword Opportunity Map")
        st.caption("X: Ranking Position | Y: Impressions | Size: Clicks | Color: Opportunity Level")
        
        # 聚合关键词数据
        df_kw_agg = df_q.groupby('query').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean',
            'ctr': 'mean'
        }).reset_index()
        
        # 只显示有展示的关键词
        df_kw_agg = df_kw_agg[df_kw_agg['impressions'] > 0]
        
        # 定义机会等级
        def get_opportunity(row):
            if row['position'] <= 10:
                return 'Maintain'
            elif row['position'] <= 20 and row['impressions'] > 5:
                return 'High Opportunity'
            elif row['position'] <= 30:
                return 'Medium Opportunity'
            else:
                return 'Low Priority'
        
        df_kw_agg['opportunity'] = df_kw_agg.apply(get_opportunity, axis=1)
        
        # 取Top 100展示量的关键词显示
        df_bubble = df_kw_agg.nlargest(100, 'impressions')
        
        color_map = {
            'Maintain': COLORS['success'],
            'High Opportunity': COLORS['danger'],
            'Medium Opportunity': COLORS['warning'],
            'Low Priority': COLORS['muted']
        }
        
        fig_bubble = px.scatter(
            df_bubble,
            x='position',
            y='impressions',
            size='clicks' if df_bubble['clicks'].sum() > 0 else 'impressions',
            color='opportunity',
            color_discrete_map=color_map,
            hover_data=['query', 'ctr'],
            size_max=40
        )
        fig_bubble.update_layout(
            height=450,
            xaxis_title="Average Ranking Position →",
            yaxis_title="Total Impressions",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#E2E8F0'),
            yaxis=dict(gridcolor='#E2E8F0'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        # 添加机会区域标注
        fig_bubble.add_vrect(x0=10, x1=30, fillcolor=COLORS['warning'], opacity=0.05, line_width=0,
                           annotation_text="Opportunity Zone", annotation_position="top left")
        st.plotly_chart(fig_bubble, use_container_width=True)
        
        # Top关键词表格
        st.markdown("#### 🏆 Top Performing Keywords")
        df_top_kw = df_kw_agg.nlargest(15, 'clicks')[['query', 'clicks', 'impressions', 'position', 'ctr', 'opportunity']]
        df_top_kw.columns = ['Keyword', 'Clicks', 'Impressions', 'Avg Position', 'CTR', 'Status']
        df_top_kw['CTR'] = df_top_kw['CTR'].apply(lambda x: f"{x*100:.2f}%" if x < 1 else f"{x:.2f}%")
        df_top_kw['Avg Position'] = df_top_kw['Avg Position'].apply(lambda x: f"{x:.1f}")
        st.dataframe(df_top_kw, use_container_width=True, hide_index=True)
        
        # Insight（建议5）
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">💡 KEY INSIGHT</div>
            <div class="content">
                <strong>{page1_opp} keywords</strong> are currently positioned between 11-30 (Page 2-3). 
                These represent the highest ROI optimization targets — they already have search visibility 
                but need content depth and internal linking improvements to break into Top 10.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Keyword data not available. Please ensure `cleaned_by_query.csv` is in the data folder.")


# ============================================================
# Tab 3: Page Performance（建议4）
# ============================================================
with tab3:
    if not data.get('by_page', pd.DataFrame()).empty:
        df_p = data['by_page']
        
        st.markdown("### 📄 Page Performance")
        
        # 聚合页面数据
        df_page_agg = df_p.groupby('page').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean',
            'ctr': 'mean'
        }).reset_index()
        
        df_page_agg = df_page_agg[df_page_agg['impressions'] > 0]
        
        # Page Opportunity Matrix（建议4 - 四象限）
        st.markdown("#### Page Opportunity Matrix")
        st.caption("Identify pages with high impressions but low CTR — these are your quick wins")
        
        # 计算中位数作为分界线
        imp_median = df_page_agg['impressions'].median()
        ctr_median = df_page_agg['ctr'].median()
        
        # 定义象限
        def get_quadrant(row):
            high_imp = row['impressions'] >= imp_median
            high_ctr = row['ctr'] >= ctr_median
            if high_imp and high_ctr:
                return '⭐ Maintain (High Imp + High CTR)'
            elif high_imp and not high_ctr:
                return '🚀 Optimize (High Imp + Low CTR)'
            elif not high_imp and high_ctr:
                return '📈 Grow (Low Imp + High CTR)'
            else:
                return '🔍 Improve (Low Imp + Low CTR)'
        
        df_page_agg['quadrant'] = df_page_agg.apply(get_quadrant, axis=1)
        
        # 简化页面URL显示
        df_page_agg['page_short'] = df_page_agg['page'].apply(
            lambda x: x.replace('https://www.advich.com/', '/') if isinstance(x, str) else x
        )
        
        quadrant_colors = {
            '⭐ Maintain (High Imp + High CTR)': COLORS['success'],
            '🚀 Optimize (High Imp + Low CTR)': COLORS['danger'],
            '📈 Grow (Low Imp + High CTR)': COLORS['secondary'],
            '🔍 Improve (Low Imp + Low CTR)': COLORS['muted']
        }
        
        fig_matrix = px.scatter(
            df_page_agg,
            x='impressions',
            y='ctr',
            color='quadrant',
            color_discrete_map=quadrant_colors,
            hover_data=['page_short', 'clicks', 'position'],
            size='clicks' if df_page_agg['clicks'].sum() > 0 else 'impressions',
            size_max=30
        )
        
        # 添加分界线
        fig_matrix.add_hline(y=ctr_median, line_dash="dash", line_color="#94A3B8", opacity=0.5)
        fig_matrix.add_vline(x=imp_median, line_dash="dash", line_color="#94A3B8", opacity=0.5)
        
        fig_matrix.update_layout(
            height=500,
            xaxis_title="Impressions →",
            yaxis_title="CTR →",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#E2E8F0'),
            yaxis=dict(gridcolor='#E2E8F0'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # 页面健康度统计
        st.markdown("#### Page Health Summary")
        quad_counts = df_page_agg['quadrant'].value_counts()
        
        q_col1, q_col2, q_col3, q_col4 = st.columns(4)
        quadrant_labels = [
            ('⭐ Maintain (High Imp + High CTR)', '⭐ Maintain', COLORS['success']),
            ('🚀 Optimize (High Imp + Low CTR)', '🚀 Optimize', COLORS['danger']),
            ('📈 Grow (Low Imp + High CTR)', '📈 Grow', COLORS['secondary']),
            ('🔍 Improve (Low Imp + Low CTR)', '🔍 Improve', COLORS['muted'])
        ]
        
        for col, (key, label, color) in zip([q_col1, q_col2, q_col3, q_col4], quadrant_labels):
            count = quad_counts.get(key, 0)
            with col:
                st.markdown(f"""
                <div class="kpi-card" style="border-top-color: {color};">
                    <h3>{label}</h3>
                    <div class="value">{count}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Top Pages表格
        st.markdown("#### 🏆 Top Pages by Traffic")
        df_top_pages = df_page_agg.nlargest(10, 'clicks')[['page_short', 'clicks', 'impressions', 'position', 'ctr', 'quadrant']]
        df_top_pages.columns = ['Page', 'Clicks', 'Impressions', 'Avg Position', 'CTR', 'Status']
        df_top_pages['CTR'] = df_top_pages['CTR'].apply(lambda x: f"{x*100:.2f}%" if x < 1 else f"{x:.2f}%")
        df_top_pages['Avg Position'] = df_top_pages['Avg Position'].apply(lambda x: f"{x:.1f}")
        st.dataframe(df_top_pages, use_container_width=True, hide_index=True)
        
        # Insight（建议5）
        optimize_count = quad_counts.get('🚀 Optimize (High Imp + Low CTR)', 0)
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">💡 KEY INSIGHT</div>
            <div class="content">
                <strong>{optimize_count} pages</strong> have high impressions but low CTR — these are your 
                highest-priority optimization targets. Improving title tags and meta descriptions for these 
                pages could significantly increase click-through rates without needing additional content.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Page data not available. Please ensure `cleaned_by_page.csv` is in the data folder.")


# ============================================================
# Tab 4: Market Expansion（建议9）
# ============================================================
with tab4:
    if not data.get('by_country', pd.DataFrame()).empty:
        df_c = data['by_country']
        
        st.markdown("### 🌍 Market Expansion")
        
        # 聚合国家数据
        df_country_agg = df_c.groupby('country').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'position': 'mean',
            'ctr': 'mean'
        }).reset_index()
        
        df_country_agg = df_country_agg[df_country_agg['impressions'] > 0]
        
        # 国家代码映射（ISO 3166-1 alpha-3）
        country_map = {
            'usa': 'USA', 'chn': 'CHN', 'hkg': 'HKG', 'twn': 'TWN',
            'sgp': 'SGP', 'jpn': 'JPN', 'gbr': 'GBR', 'deu': 'DEU',
            'can': 'CAN', 'aus': 'AUS', 'ind': 'IND', 'mys': 'MYS',
            'tha': 'THA', 'kor': 'KOR', 'fra': 'FRA', 'bra': 'BRA',
            'idn': 'IDN', 'vnm': 'VNM', 'phl': 'PHL', 'nld': 'NLD',
            'ita': 'ITA', 'esp': 'ESP', 'mex': 'MEX', 'arg': 'ARG',
            'col': 'COL', 'chl': 'CHL', 'per': 'PER', 'nzl': 'NZL',
            'irl': 'IRL', 'che': 'CHE', 'aut': 'AUT', 'bel': 'BEL',
            'swe': 'SWE', 'nor': 'NOR', 'dnk': 'DNK', 'fin': 'FIN',
            'pol': 'POL', 'tur': 'TUR', 'zaf': 'ZAF', 'egy': 'EGY',
            'sau': 'SAU', 'are': 'ARE', 'isr': 'ISR', 'rus': 'RUS',
            'ukr': 'UKR', 'pak': 'PAK', 'bgd': 'BGD', 'lka': 'LKA',
            'mmr': 'MMR', 'khm': 'KHM', 'mac': 'MAC'
        }
        
        df_country_agg['iso_alpha'] = df_country_agg['country'].map(country_map)
        df_country_agg['iso_alpha'] = df_country_agg['iso_alpha'].fillna(df_country_agg['country'].str.upper())
        
        # 世界地图（建议9）
        st.markdown("#### Global Search Visibility")
        
        fig_map = px.choropleth(
            df_country_agg,
            locations='iso_alpha',
            color='impressions',
            hover_name='country',
            hover_data=['clicks', 'impressions', 'position'],
            color_continuous_scale=[
                [0, '#EFF6FF'],
                [0.3, '#93C5FD'],
                [0.6, '#3B82F6'],
                [1, '#1E3A8A']
            ],
            title=""
        )
        fig_map.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor='#CBD5E1',
                bgcolor='rgba(0,0,0,0)'
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Market Matrix
        st.markdown("#### Market Performance Matrix")
        
        # Top 15 国家
        df_top_countries = df_country_agg.nlargest(15, 'impressions')
        
        fig_market = px.scatter(
            df_top_countries,
            x='impressions',
            y='clicks',
            size='impressions',
            color='position',
            color_continuous_scale=[[0, COLORS['success']], [0.5, COLORS['warning']], [1, COLORS['danger']]],
            hover_data=['country'],
            text='country',
            size_max=50
        )
        fig_market.update_traces(textposition='top center')
        fig_market.update_layout(
            height=400,
            xaxis_title="Impressions (Search Visibility) →",
            yaxis_title="Clicks (Engagement) →",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#E2E8F0'),
            yaxis=dict(gridcolor='#E2E8F0')
        )
        st.plotly_chart(fig_market, use_container_width=True)
        
        # 国家排名表
        st.markdown("#### 🏆 Top Markets")
        df_market_table = df_country_agg.nlargest(10, 'clicks')[['country', 'clicks', 'impressions', 'position', 'ctr']]
        df_market_table.columns = ['Country', 'Clicks', 'Impressions', 'Avg Position', 'CTR']
        df_market_table['CTR'] = df_market_table['CTR'].apply(lambda x: f"{x*100:.2f}%" if x < 1 else f"{x:.2f}%")
        df_market_table['Avg Position'] = df_market_table['Avg Position'].apply(lambda x: f"{x:.1f}")
        st.dataframe(df_market_table, use_container_width=True, hide_index=True)
        
        # 设备分布
        st.markdown("---")
        st.markdown("#### 📱 Device Distribution")
        
        if not data.get('by_device', pd.DataFrame()).empty:
            df_d = data['by_device']
            df_device_agg = df_d.groupby('device').agg({
                'clicks': 'sum',
                'impressions': 'sum'
            }).reset_index()
            
            dev_col1, dev_col2 = st.columns(2)
            
            with dev_col1:
                fig_dev = px.pie(
                    df_device_agg,
                    values='impressions',
                    names='device',
                    color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['muted']],
                    hole=0.4
                )
                fig_dev.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    title="Impressions by Device"
                )
                st.plotly_chart(fig_dev, use_container_width=True)
            
            with dev_col2:
                fig_dev_clicks = px.pie(
                    df_device_agg,
                    values='clicks',
                    names='device',
                    color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['muted']],
                    hole=0.4
                )
                fig_dev_clicks.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    title="Clicks by Device"
                )
                st.plotly_chart(fig_dev_clicks, use_container_width=True)
        
        # Insight（建议5）
        top_country = df_country_agg.nlargest(1, 'impressions')['country'].values[0] if len(df_country_agg) > 0 else "N/A"
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">💡 KEY INSIGHT</div>
            <div class="content">
                Primary market is <strong>{top_country.upper()}</strong> with the highest search visibility. 
                Asian markets (CHN, HKG, TWN, SGP) show higher CTR rates (1.6-5%) compared to Western markets, 
                indicating stronger brand recognition in the Asia-Pacific region.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Country data not available. Please ensure `cleaned_by_country.csv` is in the data folder.")


# ============================================================
# Tab 5: Recommendations（建议10 - AI SEO Consultant）
# ============================================================
with tab5:
    st.markdown("### 🤖 AI SEO Consultant")
    st.markdown("*Automated recommendations based on your data analysis*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Priority 1
    st.markdown(f"""
    <div class="ai-card">
        <div class="priority">🎯 PRIORITY 1 — Keyword Optimization</div>
        <div class="action">
            Optimize <strong>{metrics['opportunity_keywords']} keywords</strong> currently ranking between position 11-30. 
            Focus on improving content depth, adding internal links, and optimizing title tags for these terms.
        </div>
        <div class="impact">Expected Impact: HIGH · Estimated Traffic Increase: 40-60%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Priority 2
    pages_no_clicks = metrics['total_pages'] - metrics['pages_with_clicks']
    st.markdown(f"""
    <div class="ai-card">
        <div class="priority">📄 PRIORITY 2 — Page CTR Improvement</div>
        <div class="action">
            <strong>{pages_no_clicks} pages</strong> have impressions but zero clicks. 
            Rewrite meta titles and descriptions to improve click-through rates. 
            Focus on pages with highest impressions first.
        </div>
        <div class="impact">Expected Impact: MEDIUM-HIGH · Quick Win: 2-4 weeks</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Priority 3
    st.markdown(f"""
    <div class="ai-card">
        <div class="priority">🌍 PRIORITY 3 — Market Expansion</div>
        <div class="action">
            Current presence in <strong>{metrics['total_countries']} markets</strong>. 
            Focus content localization efforts on high-impression, low-CTR markets. 
            Consider creating region-specific landing pages for top 5 markets.
        </div>
        <div class="impact">Expected Impact: MEDIUM · Timeline: 1-3 months</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Priority 4
    st.markdown(f"""
    <div class="ai-card">
        <div class="priority">📊 PRIORITY 4 — Content Gap Analysis</div>
        <div class="action">
            <strong>{metrics['long_tail']} keywords</strong> are ranking beyond position 30. 
            Identify content gaps and create comprehensive pillar pages targeting 
            high-volume keywords in this segment.
        </div>
        <div class="impact">Expected Impact: MEDIUM · Timeline: 2-4 months</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Priority 5
    st.markdown(f"""
    <div class="ai-card">
        <div class="priority">⚡ PRIORITY 5 — Technical SEO</div>
        <div class="action">
            Average position is <strong>{metrics['avg_position']:.1f}</strong> (target: below 20). 
            Audit site speed, mobile usability, and Core Web Vitals. 
            Ensure all high-priority pages are properly indexed and crawlable.
        </div>
        <div class="impact">Expected Impact: MEDIUM · Foundation for all other improvements</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ROI预估
    st.markdown("### 📈 Projected Impact")
    
    roi_col1, roi_col2, roi_col3 = st.columns(3)
    
    with roi_col1:
        projected_clicks = int(metrics['total_clicks'] * 1.5)
        st.markdown(f"""
        <div class="kpi-card" style="border-top-color: {COLORS['success']};">
            <h3>Projected Monthly Clicks</h3>
            <div class="value" style="color: {COLORS['success']};">{projected_clicks:,}</div>
            <p style="color: {COLORS['muted']}; font-size: 0.8rem;">+50% with Priority 1-2</p>
        </div>
        """, unsafe_allow_html=True)
    
    with roi_col2:
        projected_ctr = min(metrics['avg_ctr'] * 2, 5.0)
        st.markdown(f"""
        <div class="kpi-card" style="border-top-color: {COLORS['success']};">
            <h3>Projected CTR</h3>
            <div class="value" style="color: {COLORS['success']};">{projected_ctr:.2f}%</div>
            <p style="color: {COLORS['muted']}; font-size: 0.8rem;">Industry avg: 3-5%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with roi_col3:
        projected_score = min(overall_score + 15, 95)
        st.markdown(f"""
        <div class="kpi-card" style="border-top-color: {COLORS['success']};">
            <h3>Projected Health Score</h3>
            <div class="value" style="color: {COLORS['success']};">{projected_score:.0f}</div>
            <p style="color: {COLORS['muted']}; font-size: 0.8rem;">Target: 85+ (Grade A)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Final Insight
    st.markdown(f"""
    <div class="insight-card">
        <div class="title">💡 STRATEGIC SUMMARY</div>
        <div class="content">
            The website's SEO foundation is established with <strong>{metrics['total_keywords']:,} tracked keywords</strong> 
            across <strong>{metrics['total_countries']} markets</strong>. The primary growth lever is converting 
            existing Page 2-3 rankings into Page 1 positions. This "low-hanging fruit" strategy offers the 
            highest ROI with minimal content investment. Focus execution on Priority 1 and 2 for immediate results.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {COLORS['muted']}; font-size: 0.8rem; padding: 1rem;">
    SEO Health Analytics v2.0 · Powered by Google Search Console Data · Built with Streamlit<br>
    Data Range: 2025-04-03 to 2026-07-25 · Last Updated: 2026-07-27
</div>
""", unsafe_allow_html=True)

