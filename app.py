
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# 多语言翻译字典
# ============================================================
TRANSLATIONS = {
    "zh": {
        # 全局
        "app_title": "B2B独立站 SEO 健康度诊断工具",
        "app_subtitle": "基于 Google Search Console 数据 | v2.0",
        "language_label": "🌐 Language / 语言",
        "nav_title": "导航菜单",
        "data_range": "数据范围",
        "to": "至",
        # 导航
        "nav_overview": "📊 总览仪表盘",
        "nav_health": "🏥 SEO Health Score",
        "nav_search": "📈 搜索表现趋势",
        "nav_page": "📄 页面效果分析",
        "nav_country": "🌍 国家/地区分析",
        "nav_device": "📱 设备分布",
        "nav_anomaly": "🚨 流量异常检测",
        # 总览
        "overview_title": "B2B独立站 SEO 总览仪表盘",
        "total_clicks": "总点击数",
        "total_impressions": "总展示次数",
        "avg_ctr": "平均CTR",
        "avg_position": "平均排名",
        "active_pages": "活跃页面数",
        "total_queries": "关键词数",
        "total_countries": "覆盖国家数",
        "data_period": "数据周期（天）",
        "select_module": "请从左侧导航菜单选择具体分析模块，查看详细诊断报告。",
        # 健康度
        "health_title": "SEO Health Score",
        "health_subtitle": "三维加权评分模型",
        "overall_score": "综合评分",
        "grade": "等级",
        "grade_excellent": "优秀",
        "grade_good": "良好",
        "grade_average": "一般",
        "grade_poor": "较差",
        "dimension_scores": "各维度得分",
        "search_performance": "Search Performance",
        "page_effectiveness": "Page Effectiveness",
        "tech_experience": "Technical Experience Signals",
        "weight": "权重",
        "score_detail": "评分明细",
        "indicator": "指标",
        "value": "实际值",
        "score": "得分",
        "benchmark": "基准",
        "methodology": "评分方法论",
        "methodology_desc": "本评分基于 GSC 真实数据，采用三维加权模型。各维度权重根据数据可得性和业务重要性分配。",
        "expansion_note": "扩展说明",
        "expansion_desc": "当前评分基于 GSC 可用数据。未来可接入 Ahrefs/SEMrush API 补充外链权威维度（建议权重15-20%），届时现有维度权重将等比缩减。",
        # 搜索趋势
        "search_title": "搜索表现趋势",
        "click_impression_trend": "点击数 & 展示次数趋势",
        "ctr_position_trend": "CTR & 平均排名趋势",
        "date_range": "选择日期范围",
        "granularity": "时间粒度",
        "daily": "日",
        "weekly": "周",
        "monthly": "月",
        "clicks": "点击数",
        "impressions": "展示次数",
        "ctr": "CTR",
        "position": "平均排名",
        # 页面效果
        "page_title": "页面效果分析",
        "page_opportunity": "页面机会矩阵",
        "high_imp_low_click": "⚡ 高曝光低点击（优先优化）",
        "high_imp_high_click": "⭐ 高曝光高点击（保持增长）",
        "low_imp_low_click": "💤 低曝光低点击（低优先级）",
        "low_imp_high_click": "🌱 低曝光高点击（内容扩展）",
        "top_pages": "Top 页面表现",
        "page_url": "页面URL",
        "opportunity_type": "机会类型",
        "recommendation": "优化建议",
        # 国家
        "country_title": "国家/地区分析",
        "top_countries_clicks": "Top 国家（按点击）",
        "top_countries_impressions": "Top 国家（按展示）",
        "country_distribution": "国家分布地图",
        "country_detail": "国家详细数据",
        # 设备
        "device_title": "设备分布分析",
        "device_clicks": "各设备点击占比",
        "device_impressions": "各设备展示占比",
        "device_ctr_compare": "各设备CTR对比",
        "device_trend": "设备趋势变化",
        # 异常检测
        "anomaly_title": "流量异常检测",
        "anomaly_method": "检测方法",
        "zscore": "Z-Score 检测",
        "iqr": "IQR 四分位检测",
        "rolling": "滚动均值偏离",
        "sensitivity": "灵敏度",
        "anomaly_results": "异常检测结果",
        "anomaly_count": "检测到异常点数",
        "anomaly_detail": "异常详情",
        "no_data": "未找到相关数据，请检查数据文件。",
    },
    "en": {
        # Global
        "app_title": "B2B Website SEO Health Diagnostic Tool",
        "app_subtitle": "Based on Google Search Console Data | v2.0",
        "language_label": "🌐 Language / 语言",
        "nav_title": "Navigation",
        "data_range": "Data Range",
        "to": "to",
        # Navigation
        "nav_overview": "📊 Overview Dashboard",
        "nav_health": "🏥 SEO Health Score",
        "nav_search": "📈 Search Performance Trends",
        "nav_page": "📄 Page Effectiveness",
        "nav_country": "🌍 Country/Region Analysis",
        "nav_device": "📱 Device Distribution",
        "nav_anomaly": "🚨 Traffic Anomaly Detection",
        # Overview
        "overview_title": "B2B Website SEO Overview Dashboard",
        "total_clicks": "Total Clicks",
        "total_impressions": "Total Impressions",
        "avg_ctr": "Average CTR",
        "avg_position": "Average Position",
        "active_pages": "Active Pages",
        "total_queries": "Total Keywords",
        "total_countries": "Countries Covered",
        "data_period": "Data Period (Days)",
        "select_module": "Select a module from the left navigation menu for detailed diagnostic reports.",
        # Health Score
        "health_title": "SEO Health Score",
        "health_subtitle": "Three-Dimensional Weighted Scoring Model",
        "overall_score": "Overall Score",
        "grade": "Grade",
        "grade_excellent": "Excellent",
        "grade_good": "Good",
        "grade_average": "Average",
        "grade_poor": "Poor",
        "dimension_scores": "Dimension Scores",
        "search_performance": "Search Performance",
        "page_effectiveness": "Page Effectiveness",
        "tech_experience": "Technical Experience Signals",
        "weight": "Weight",
        "score_detail": "Score Details",
        "indicator": "Indicator",
        "value": "Actual Value",
        "score": "Score",
        "benchmark": "Benchmark",
        "methodology": "Scoring Methodology",
        "methodology_desc": "This score is based on real GSC data using a three-dimensional weighted model. Dimension weights are allocated based on data availability and business importance.",
        "expansion_note": "Expansion Note",
        "expansion_desc": "Current scoring is based on available GSC data. Future integration with Ahrefs/SEMrush APIs can add a Backlink Authority dimension (suggested weight: 15-20%), with existing dimension weights proportionally reduced.",
        # Search Trends
        "search_title": "Search Performance Trends",
        "click_impression_trend": "Clicks & Impressions Trend",
        "ctr_position_trend": "CTR & Average Position Trend",
        "date_range": "Select Date Range",
        "granularity": "Time Granularity",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "clicks": "Clicks",
        "impressions": "Impressions",
        "ctr": "CTR",
        "position": "Avg Position",
        # Page Effectiveness
        "page_title": "Page Effectiveness Analysis",
        "page_opportunity": "Page Opportunity Matrix",
        "high_imp_low_click": "⚡ High Impression, Low Click (Priority Optimization)",
        "high_imp_high_click": "⭐ High Impression, High Click (Maintain Growth)",
        "low_imp_low_click": "💤 Low Impression, Low Click (Low Priority)",
        "low_imp_high_click": "🌱 Low Impression, High Click (Content Expansion)",
        "top_pages": "Top Pages Performance",
        "page_url": "Page URL",
        "opportunity_type": "Opportunity Type",
        "recommendation": "Recommendation",
        # Country
        "country_title": "Country/Region Analysis",
        "top_countries_clicks": "Top Countries (by Clicks)",
        "top_countries_impressions": "Top Countries (by Impressions)",
        "country_distribution": "Country Distribution Map",
        "country_detail": "Country Detail Data",
        # Device
        "device_title": "Device Distribution Analysis",
        "device_clicks": "Click Share by Device",
        "device_impressions": "Impression Share by Device",
        "device_ctr_compare": "CTR Comparison by Device",
        "device_trend": "Device Trend Changes",
        # Anomaly
        "anomaly_title": "Traffic Anomaly Detection",
        "anomaly_method": "Detection Method",
        "zscore": "Z-Score Detection",
        "iqr": "IQR Quartile Detection",
        "rolling": "Rolling Mean Deviation",
        "sensitivity": "Sensitivity",
        "anomaly_results": "Anomaly Detection Results",
        "anomaly_count": "Anomalies Detected",
        "anomaly_detail": "Anomaly Details",
        "no_data": "No relevant data found. Please check data files.",
    }
}

def t(key):
    """获取当前语言的翻译文本"""
    lang = st.session_state.get("language", "zh")
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)

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
# 自定义样式
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .metric-card h3 {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    .metric-card h1 {
        font-size: 2rem;
        margin: 0;
    }
    .score-card {
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .grade-A { background: linear-gradient(135deg, #00b09b, #96c93d); color: white; }
    .grade-B { background: linear-gradient(135deg, #2196F3, #21CBF3); color: white; }
    .grade-C { background: linear-gradient(135deg, #FF9800, #FF5722); color: white; }
    .grade-D { background: linear-gradient(135deg, #f44336, #e91e63); color: white; }
    .info-box {
        background: #f0f7ff;
        border-left: 4px solid #2196F3;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff8e1;
        border-left: 4px solid #FF9800;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
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
        'by_device': 'cleaned_by_device.csv',
        'by_country': 'cleaned_by_country.csv',
        'by_query': 'cleaned_by_query.csv',
        'by_page': 'cleaned_by_page.csv',
        'daily_summary': 'cleaned_daily_summary.csv',
        'query_page': 'cleaned_query_page.csv',
        'date_query': 'cleaned_date_query.csv',
        'date_page': 'cleaned_date_page.csv',
    }
    
    for key, filename in file_mapping.items():
        try:
            df = pd.read_csv(f"{base_path}{filename}")
            if 'data_date' in df.columns:
                df['data_date'] = pd.to_datetime(df['data_date'])
            data[key] = df
        except FileNotFoundError:
            data[key] = None
    
    return data

data = load_data()

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    # 语言切换
    lang_options = {"中文": "zh", "English": "en"}
    selected_lang = st.selectbox(
        "🌐 Language / 语言",
        options=list(lang_options.keys()),
        index=0
    )
    st.session_state["language"] = lang_options[selected_lang]
    
    st.markdown("---")
    st.markdown(f"### {t('app_title')}")
    st.caption(t('app_subtitle'))
    st.markdown("---")
    
    # 导航菜单
    st.markdown(f"#### {t('nav_title')}")
    page = st.radio(
        "",
        [t('nav_overview'), t('nav_health'), t('nav_search'), 
         t('nav_page'), t('nav_country'), t('nav_device'), t('nav_anomaly')],
        label_visibility="collapsed"
    )
    
    # 数据范围
    st.markdown("---")
    if data.get('by_date') is not None:
        date_min = data['by_date']['data_date'].min()
        date_max = data['by_date']['data_date'].max()
        st.caption(f"📅 {t('data_range')}: {date_min.strftime('%Y-%m-%d')} {t('to')} {date_max.strftime('%Y-%m-%d')}")

# ============================================================
# SEO Health Score 计算引擎（新三维模型）
# ============================================================
def calculate_health_score(data):
    """
    三维加权评分模型:
    - Search Performance (40%): ClickScore×30% + ImpressionScore×30% + CTRScore×20% + RankingScore×20%
    - Page Effectiveness (35%): PageCTR×40% + PageTraffic×30% + QueryCoverage×30%
    - Technical Experience Signals (25%): MobileShare×40% + DeviceCoverage×30% + PositionStability×30%
    """
    scores = {}
    details = {}
    
    # === Search Performance (40%) ===
    sp_scores = {}
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        avg_ctr = df['ctr'].mean()
        avg_position = df['position'].mean()
        
        # Click Score: 基于B2B行业基准（月均100-500点击为良好）
        click_monthly = total_clicks / max(len(df), 1) * 30
        if click_monthly >= 500: sp_scores['clicks'] = 95
        elif click_monthly >= 200: sp_scores['clicks'] = 80
        elif click_monthly >= 50: sp_scores['clicks'] = 65
        elif click_monthly >= 10: sp_scores['clicks'] = 45
        else: sp_scores['clicks'] = 25
        
        # Impression Score: 基于B2B行业基准（月均5000-20000展示为良好）
        imp_monthly = total_impressions / max(len(df), 1) * 30
        if imp_monthly >= 20000: sp_scores['impressions'] = 95
        elif imp_monthly >= 5000: sp_scores['impressions'] = 80
        elif imp_monthly >= 1000: sp_scores['impressions'] = 65
        elif imp_monthly >= 200: sp_scores['impressions'] = 45
        else: sp_scores['impressions'] = 25
        
        # CTR Score: B2B行业平均CTR约2-3%
        avg_ctr_pct = avg_ctr * 100 if avg_ctr < 1 else avg_ctr
        if avg_ctr_pct >= 5: sp_scores['ctr'] = 95
        elif avg_ctr_pct >= 3: sp_scores['ctr'] = 80
        elif avg_ctr_pct >= 1.5: sp_scores['ctr'] = 65
        elif avg_ctr_pct >= 0.5: sp_scores['ctr'] = 45
        else: sp_scores['ctr'] = 25
        
        # Ranking Score: 平均排名越低越好
        if avg_position <= 10: sp_scores['position'] = 95
        elif avg_position <= 20: sp_scores['position'] = 80
        elif avg_position <= 30: sp_scores['position'] = 65
        elif avg_position <= 50: sp_scores['position'] = 45
        else: sp_scores['position'] = 25
        
        details['search_performance'] = {
            'click_monthly': round(click_monthly, 1),
            'imp_monthly': round(imp_monthly, 1),
            'avg_ctr': round(avg_ctr_pct, 2),
            'avg_position': round(avg_position, 1),
            'scores': sp_scores
        }
    
    sp_total = (sp_scores.get('clicks', 50) * 0.30 + 
                sp_scores.get('impressions', 50) * 0.30 + 
                sp_scores.get('ctr', 50) * 0.20 + 
                sp_scores.get('position', 50) * 0.20)
    scores['search_performance'] = round(sp_total, 1)
    
    # === Page Effectiveness (35%) ===
    pe_scores = {}
    if data.get('by_query') is not None and data.get('query_page') is not None:
        df_query = data['by_query']
        df_qp = data['query_page']
        
        # Query Coverage: 关键词覆盖度
        unique_queries = df_query['query'].nunique() if 'query' in df_query.columns else 0
        if unique_queries >= 500: pe_scores['query_coverage'] = 90
        elif unique_queries >= 200: pe_scores['query_coverage'] = 75
        elif unique_queries >= 50: pe_scores['query_coverage'] = 60
        elif unique_queries >= 10: pe_scores['query_coverage'] = 40
        else: pe_scores['query_coverage'] = 20
        
        # Page Traffic: 有流量的页面占比
        if 'page' in df_qp.columns:
            pages_with_clicks = df_qp[df_qp['clicks'] > 0]['page'].nunique()
            total_pages = df_qp['page'].nunique()
            page_traffic_rate = pages_with_clicks / max(total_pages, 1)
            if page_traffic_rate >= 0.5: pe_scores['page_traffic'] = 90
            elif page_traffic_rate >= 0.3: pe_scores['page_traffic'] = 75
            elif page_traffic_rate >= 0.15: pe_scores['page_traffic'] = 60
            elif page_traffic_rate >= 0.05: pe_scores['page_traffic'] = 40
            else: pe_scores['page_traffic'] = 20
        else:
            pe_scores['page_traffic'] = 50
            page_traffic_rate = 0
        
        # Page CTR: 页面平均CTR
        if 'ctr' in df_qp.columns:
            page_avg_ctr = df_qp['ctr'].mean()
            page_avg_ctr_pct = page_avg_ctr * 100 if page_avg_ctr < 1 else page_avg_ctr
            if page_avg_ctr_pct >= 5: pe_scores['page_ctr'] = 90
            elif page_avg_ctr_pct >= 3: pe_scores['page_ctr'] = 75
            elif page_avg_ctr_pct >= 1.5: pe_scores['page_ctr'] = 60
            elif page_avg_ctr_pct >= 0.5: pe_scores['page_ctr'] = 40
            else: pe_scores['page_ctr'] = 20
        else:
            pe_scores['page_ctr'] = 50
            page_avg_ctr_pct = 0
        
        details['page_effectiveness'] = {
            'unique_queries': unique_queries,
            'page_traffic_rate': round(page_traffic_rate * 100, 1) if 'page_traffic_rate' in dir() else 0,
            'page_avg_ctr': round(page_avg_ctr_pct, 2) if 'page_avg_ctr_pct' in dir() else 0,
            'scores': pe_scores
        }
    elif data.get('by_query') is not None:
        df_query = data['by_query']
        unique_queries = df_query['query'].nunique() if 'query' in df_query.columns else 0
        if unique_queries >= 500: pe_scores['query_coverage'] = 90
        elif unique_queries >= 200: pe_scores['query_coverage'] = 75
        elif unique_queries >= 50: pe_scores['query_coverage'] = 60
        else: pe_scores['query_coverage'] = 40
        pe_scores['page_traffic'] = 50
        pe_scores['page_ctr'] = 50
        details['page_effectiveness'] = {
            'unique_queries': unique_queries,
            'page_traffic_rate': 0,
            'page_avg_ctr': 0,
            'scores': pe_scores
        }
    
    pe_total = (pe_scores.get('page_ctr', 50) * 0.40 + 
                pe_scores.get('page_traffic', 50) * 0.30 + 
                pe_scores.get('query_coverage', 50) * 0.30)
    scores['page_effectiveness'] = round(pe_total, 1)
    
    # === Technical Experience Signals (25%) ===
    te_scores = {}
    if data.get('by_device') is not None:
        df_device = data['by_device']
        
        # Mobile Share: 移动端展示占比
        total_imp = df_device['impressions'].sum()
        mobile_imp = df_device[df_device['device'].str.upper() == 'MOBILE']['impressions'].sum()
        mobile_share = mobile_imp / max(total_imp, 1)
        
        # 移动端占比在30-60%为健康
        if 0.3 <= mobile_share <= 0.6: te_scores['mobile_share'] = 90
        elif 0.2 <= mobile_share <= 0.7: te_scores['mobile_share'] = 70
        elif 0.1 <= mobile_share <= 0.8: te_scores['mobile_share'] = 50
        else: te_scores['mobile_share'] = 30
        
        # Device Coverage: 设备覆盖度（3种设备都有数据）
        device_count = df_device['device'].nunique()
        if device_count >= 3: te_scores['device_coverage'] = 90
        elif device_count >= 2: te_scores['device_coverage'] = 65
        else: te_scores['device_coverage'] = 35
        
        # Position Stability: 排名稳定性（用变异系数衡量）
        if 'position' in df_device.columns:
            pos_std = df_device['position'].std()
            pos_mean = df_device['position'].mean()
            cv = pos_std / max(pos_mean, 1)
            if cv <= 0.3: te_scores['position_stability'] = 90
            elif cv <= 0.5: te_scores['position_stability'] = 70
            elif cv <= 0.8: te_scores['position_stability'] = 50
            else: te_scores['position_stability'] = 30
        else:
            te_scores['position_stability'] = 50
            cv = 0
        
        details['tech_experience'] = {
            'mobile_share': round(mobile_share * 100, 1),
            'device_count': device_count,
            'position_cv': round(cv, 2) if 'cv' in dir() else 0,
            'scores': te_scores
        }
    
    te_total = (te_scores.get('mobile_share', 50) * 0.40 + 
                te_scores.get('device_coverage', 50) * 0.30 + 
                te_scores.get('position_stability', 50) * 0.30)
    scores['tech_experience'] = round(te_total, 1)
    
    # === 综合评分 ===
    overall = (scores.get('search_performance', 50) * 0.40 + 
               scores.get('page_effectiveness', 50) * 0.35 + 
               scores.get('tech_experience', 50) * 0.25)
    scores['overall'] = round(overall, 1)
    
    # 等级判定
    if overall >= 90: grade = 'A'
    elif overall >= 70: grade = 'B'
    elif overall >= 50: grade = 'C'
    else: grade = 'D'
    scores['grade'] = grade
    
    return scores, details

# ============================================================
# 页面渲染函数
# ============================================================

def render_overview():
    """总览仪表盘"""
    st.markdown(f'<div class="main-header">{t("overview_title")}</div>', unsafe_allow_html=True)
    
    # 核心指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    if data.get('daily_summary') is not None:
        df = data['daily_summary']
        total_clicks = int(df['clicks'].sum())
        total_impressions = int(df['impressions'].sum())
        avg_ctr = df['ctr'].mean()
        avg_ctr_display = f"{avg_ctr*100:.2f}%" if avg_ctr < 1 else f"{avg_ctr:.2f}%"
        avg_pos = df['position'].mean()
    elif data.get('by_date') is not None:
        df = data['by_date']
        total_clicks = int(df['clicks'].sum())
        total_impressions = int(df['impressions'].sum())
        avg_ctr = df['ctr'].mean()
        avg_ctr_display = f"{avg_ctr*100:.2f}%" if avg_ctr < 1 else f"{avg_ctr:.2f}%"
        avg_pos = df['position'].mean()
    else:
        total_clicks = total_impressions = 0
        avg_ctr_display = "N/A"
        avg_pos = 0
    
    with col1:
        st.metric(t("total_clicks"), f"{total_clicks:,}")
    with col2:
        st.metric(t("total_impressions"), f"{total_impressions:,}")
    with col3:
        st.metric(t("avg_ctr"), avg_ctr_display)
    with col4:
        st.metric(t("avg_position"), f"{avg_pos:.1f}")
    
    # 第二行指标
    col5, col6, col7, col8 = st.columns(4)
    
    active_pages = data['query_page']['page'].nunique() if data.get('query_page') is not None and 'page' in data['query_page'].columns else 0
    total_queries = data['by_query']['query'].nunique() if data.get('by_query') is not None and 'query' in data['by_query'].columns else 0
    total_countries = data['by_country']['country'].nunique() if data.get('by_country') is not None else 0
    data_days = (data['by_date']['data_date'].max() - data['by_date']['data_date'].min()).days if data.get('by_date') is not None else 0
    
    with col5:
        st.metric(t("active_pages"), f"{active_pages}")
    with col6:
        st.metric(t("total_queries"), f"{total_queries:,}")
    with col7:
        st.metric(t("total_countries"), f"{total_countries}")
    with col8:
        st.metric(t("data_period"), f"{data_days}")
    
    st.markdown(f'<div class="info-box">{t("select_module")}</div>', unsafe_allow_html=True)


def render_health_score():
    """SEO Health Score 页面"""
    st.markdown(f'<div class="main-header">{t("health_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{t("health_subtitle")}</div>', unsafe_allow_html=True)
    
    scores, details = calculate_health_score(data)
    
    # 综合评分展示
    grade = scores['grade']
    overall = scores['overall']
    grade_labels = {'A': t('grade_excellent'), 'B': t('grade_good'), 'C': t('grade_average'), 'D': t('grade_poor')}
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="score-card grade-{grade}">
            <h2 style="margin:0; font-size:3rem;">{grade}</h2>
            <p style="margin:0.5rem 0; font-size:1.2rem;">{grade_labels.get(grade, '')}</p>
            <h1 style="margin:0; font-size:2.5rem;">{overall} / 100</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 三维度得分
    st.subheader(t("dimension_scores"))
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sp = scores.get('search_performance', 0)
        st.metric(f"🔍 {t('search_performance')}", f"{sp}/100")
        st.caption(f"{t('weight')}: 40%")
        st.progress(sp / 100)
    
    with col2:
        pe = scores.get('page_effectiveness', 0)
        st.metric(f"📄 {t('page_effectiveness')}", f"{pe}/100")
        st.caption(f"{t('weight')}: 35%")
        st.progress(pe / 100)
    
    with col3:
        te = scores.get('tech_experience', 0)
        st.metric(f"⚙️ {t('tech_experience')}", f"{te}/100")
        st.caption(f"{t('weight')}: 25%")
        st.progress(te / 100)
    
    # 雷达图
    fig = go.Figure()
    categories = [t('search_performance'), t('page_effectiveness'), t('tech_experience')]
    values = [sp, pe, te]
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=2),
        name=t('dimension_scores')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 评分明细
    st.markdown("---")
    st.subheader(t("score_detail"))
    
    if 'search_performance' in details:
        sp_detail = details['search_performance']
        with st.expander(f"🔍 {t('search_performance')} — {t('score')}: {sp}/100"):
            detail_data = {
                t('indicator'): [t('clicks') + '/月', t('impressions') + '/月', 'CTR', t('position')],
                t('value'): [sp_detail['click_monthly'], sp_detail['imp_monthly'], f"{sp_detail['avg_ctr']}%", sp_detail['avg_position']],
                t('score'): [sp_detail['scores'].get('clicks', 0), sp_detail['scores'].get('impressions', 0), sp_detail['scores'].get('ctr', 0), sp_detail['scores'].get('position', 0)],
                t('weight'): ['30%', '30%', '20%', '20%']
            }
            st.dataframe(pd.DataFrame(detail_data), use_container_width=True, hide_index=True)
    
    if 'page_effectiveness' in details:
        pe_detail = details['page_effectiveness']
        with st.expander(f"📄 {t('page_effectiveness')} — {t('score')}: {pe}/100"):
            detail_data = {
                t('indicator'): ['Page CTR', 'Page Traffic Rate', 'Query Coverage'],
                t('value'): [f"{pe_detail.get('page_avg_ctr', 0)}%", f"{pe_detail.get('page_traffic_rate', 0)}%", pe_detail.get('unique_queries', 0)],
                t('score'): [pe_detail['scores'].get('page_ctr', 0), pe_detail['scores'].get('page_traffic', 0), pe_detail['scores'].get('query_coverage', 0)],
                t('weight'): ['40%', '30%', '30%']
            }
            st.dataframe(pd.DataFrame(detail_data), use_container_width=True, hide_index=True)
    
    if 'tech_experience' in details:
        te_detail = details['tech_experience']
        with st.expander(f"⚙️ {t('tech_experience')} — {t('score')}: {te}/100"):
            detail_data = {
                t('indicator'): ['Mobile Share', 'Device Coverage', 'Position Stability (CV)'],
                t('value'): [f"{te_detail.get('mobile_share', 0)}%", te_detail.get('device_count', 0), te_detail.get('position_cv', 0)],
                t('score'): [te_detail['scores'].get('mobile_share', 0), te_detail['scores'].get('device_coverage', 0), te_detail['scores'].get('position_stability', 0)],
                t('weight'): ['40%', '30%', '30%']
            }
            st.dataframe(pd.DataFrame(detail_data), use_container_width=True, hide_index=True)
    
    # 方法论说明
    st.markdown("---")
    st.markdown(f'<div class="info-box"><b>{t("methodology")}</b><br>{t("methodology_desc")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="warning-box"><b>{t("expansion_note")}</b><br>{t("expansion_desc")}</div>', unsafe_allow_html=True)


def render_search_trends():
    """搜索表现趋势"""
    st.markdown(f'<div class="main-header">{t("search_title")}</div>', unsafe_allow_html=True)
    
    df = data.get('by_date')
    if df is None:
        st.warning(t("no_data"))
        return
    
    df = df.sort_values('data_date')
    
    # 日期范围选择
    col1, col2 = st.columns(2)
    with col1:
        date_range = st.date_input(
            t("date_range"),
            value=(df['data_date'].min().date(), df['data_date'].max().date()),
            min_value=df['data_date'].min().date(),
            max_value=df['data_date'].max().date()
        )
    with col2:
        granularity = st.selectbox(t("granularity"), [t("daily"), t("weekly"), t("monthly")])
    
    # 过滤数据
    if len(date_range) == 2:
        mask = (df['data_date'].dt.date >= date_range[0]) & (df['data_date'].dt.date <= date_range[1])
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    # 按粒度聚合
    if granularity == t("weekly"):
        df_filtered['period'] = df_filtered['data_date'].dt.to_period('W').apply(lambda r: r.start_time)
        df_agg = df_filtered.groupby('period').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()
        df_agg.rename(columns={'period': 'data_date'}, inplace=True)
    elif granularity == t("monthly"):
        df_filtered['period'] = df_filtered['data_date'].dt.to_period('M').apply(lambda r: r.start_time)
        df_agg = df_filtered.groupby('period').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()
        df_agg.rename(columns={'period': 'data_date'}, inplace=True)
    else:
        df_agg = df_filtered
    
    # 点击 & 展示趋势图
    st.subheader(t("click_impression_trend"))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=df_agg['data_date'], y=df_agg['impressions'], name=t('impressions'), marker_color='rgba(102, 126, 234, 0.6)'),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=df_agg['data_date'], y=df_agg['clicks'], name=t('clicks'), line=dict(color='#e74c3c', width=2), mode='lines+markers'),
        secondary_y=True
    )
    fig.update_layout(height=400, hovermode='x unified')
    fig.update_yaxes(title_text=t('impressions'), secondary_y=False)
    fig.update_yaxes(title_text=t('clicks'), secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # CTR & 排名趋势
    st.subheader(t("ctr_position_trend"))
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    ctr_display = df_agg['ctr'] * 100 if df_agg['ctr'].max() < 1 else df_agg['ctr']
    fig2.add_trace(
        go.Scatter(x=df_agg['data_date'], y=ctr_display, name='CTR (%)', line=dict(color='#2ecc71', width=2), mode='lines+markers'),
        secondary_y=False
    )
    fig2.add_trace(
        go.Scatter(x=df_agg['data_date'], y=df_agg['position'], name=t('position'), line=dict(color='#9b59b6', width=2), mode='lines+markers'),
        secondary_y=True
    )
    fig2.update_layout(height=400, hovermode='x unified')
    fig2.update_yaxes(title_text='CTR (%)', secondary_y=False)
    fig2.update_yaxes(title_text=t('position'), autorange='reversed', secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)


def render_page_effectiveness():
    """页面效果分析"""
    st.markdown(f'<div class="main-header">{t("page_title")}</div>', unsafe_allow_html=True)
    
    df = data.get('query_page')
    if df is None:
        df = data.get('by_page')
    
    if df is None or 'page' not in df.columns:
        st.warning(t("no_data"))
        return
    
    # 按页面聚合
    page_stats = df.groupby('page').agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'position': 'mean'
    }).reset_index()
    
    # 页面机会矩阵
    st.subheader(t("page_opportunity"))
    
    imp_median = page_stats['impressions'].median()
    click_median = page_stats['clicks'].median()
    
    def classify_page(row):
        high_imp = row['impressions'] > imp_median
        high_click = row['clicks'] > click_median
        if high_imp and not high_click:
            return t('high_imp_low_click')
        elif high_imp and high_click:
            return t('high_imp_high_click')
        elif not high_imp and high_click:
            return t('low_imp_high_click')
        else:
            return t('low_imp_low_click')
    
    page_stats['opportunity'] = page_stats.apply(classify_page, axis=1)
    
    # 散点图
    fig = px.scatter(
        page_stats,
        x='impressions',
        y='clicks',
        color='opportunity',
        hover_data=['page', 'ctr', 'position'],
        size='impressions',
        size_max=30,
        height=500
    )
    fig.update_layout(xaxis_title=t('impressions'), yaxis_title=t('clicks'))
    st.plotly_chart(fig, use_container_width=True)
    
    # 机会分类统计
    col1, col2, col3, col4 = st.columns(4)
    opportunity_counts = page_stats['opportunity'].value_counts()
    
    with col1:
        count = opportunity_counts.get(t('high_imp_low_click'), 0)
        st.metric(t('high_imp_low_click'), count)
    with col2:
        count = opportunity_counts.get(t('high_imp_high_click'), 0)
        st.metric(t('high_imp_high_click'), count)
    with col3:
        count = opportunity_counts.get(t('low_imp_high_click'), 0)
        st.metric(t('low_imp_high_click'), count)
    with col4:
        count = opportunity_counts.get(t('low_imp_low_click'), 0)
        st.metric(t('low_imp_low_click'), count)
    
    # Top 页面表格
    st.markdown("---")
    st.subheader(t("top_pages"))
    top_pages = page_stats.nlargest(20, 'impressions')[['page', 'clicks', 'impressions', 'ctr', 'position', 'opportunity']]
    top_pages.columns = [t('page_url'), t('clicks'), t('impressions'), 'CTR', t('position'), t('opportunity_type')]
    st.dataframe(top_pages, use_container_width=True, hide_index=True)


def render_country():
    """国家/地区分析"""
    st.markdown(f'<div class="main-header">{t("country_title")}</div>', unsafe_allow_html=True)
    
    df = data.get('by_country')
    if df is None:
        st.warning(t("no_data"))
        return
    
    # 按国家聚合
    country_stats = df.groupby('country').agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'position': 'mean'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t("top_countries_clicks"))
        top_clicks = country_stats.nlargest(15, 'clicks')
        fig = px.bar(top_clicks, x='country', y='clicks', color='clicks',
                     color_continuous_scale='Viridis', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(t("top_countries_impressions"))
        top_imp = country_stats.nlargest(15, 'impressions')
        fig = px.bar(top_imp, x='country', y='impressions', color='impressions',
                     color_continuous_scale='Plasma', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # 详细数据表
    st.markdown("---")
    st.subheader(t("country_detail"))
    display_df = country_stats.nlargest(30, 'impressions').round(3)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_device():
    """设备分布"""
    st.markdown(f'<div class="main-header">{t("device_title")}</div>', unsafe_allow_html=True)
    
    df = data.get('by_device')
    if df is None:
        st.warning(t("no_data"))
        return
    
    # 按设备聚合
    device_stats = df.groupby('device').agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'position': 'mean'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t("device_clicks"))
        fig = px.pie(device_stats, values='clicks', names='device', 
                     color_discrete_sequence=['#667eea', '#764ba2', '#f093fb'],
                     height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(t("device_impressions"))
        fig = px.pie(device_stats, values='impressions', names='device',
                     color_discrete_sequence=['#4facfe', '#00f2fe', '#43e97b'],
                     height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # CTR 对比
    st.subheader(t("device_ctr_compare"))
    ctr_display = device_stats.copy()
    ctr_display['ctr_pct'] = ctr_display['ctr'] * 100 if ctr_display['ctr'].max() < 1 else ctr_display['ctr']
    fig = px.bar(ctr_display, x='device', y='ctr_pct', color='device',
                 color_discrete_sequence=['#667eea', '#764ba2', '#f093fb'],
                 height=350)
    fig.update_yaxes(title_text='CTR (%)')
    st.plotly_chart(fig, use_container_width=True)
    
    # 设备趋势
    st.subheader(t("device_trend"))
    df_sorted = df.sort_values('data_date')
    fig = px.line(df_sorted, x='data_date', y='impressions', color='device',
                  markers=True, height=400)
    fig.update_layout(xaxis_title='', yaxis_title=t('impressions'))
    st.plotly_chart(fig, use_container_width=True)


def render_anomaly():
    """流量异常检测"""
    st.markdown(f'<div class="main-header">{t("anomaly_title")}</div>', unsafe_allow_html=True)
    
    df = data.get('by_date')
    if df is None:
        st.warning(t("no_data"))
        return
    
    df = df.sort_values('data_date').copy()
    
    # 检测参数
    col1, col2 = st.columns(2)
    with col1:
        method = st.selectbox(t("anomaly_method"), [t("zscore"), t("iqr"), t("rolling")])
    with col2:
        sensitivity = st.slider(t("sensitivity"), 1.0, 3.0, 2.0, 0.1)
    
    # 异常检测算法
    if method == t("zscore"):
        mean_val = df['clicks'].mean()
        std_val = df['clicks'].std()
        df['is_anomaly'] = abs(df['clicks'] - mean_val) > sensitivity * std_val
    elif method == t("iqr"):
        Q1 = df['clicks'].quantile(0.25)
        Q3 = df['clicks'].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - sensitivity * IQR
        upper = Q3 + sensitivity * IQR
        df['is_anomaly'] = (df['clicks'] < lower) | (df['clicks'] > upper)
    else:  # rolling
        window = 7
        rolling_mean = df['clicks'].rolling(window=window, center=True).mean()
        rolling_std = df['clicks'].rolling(window=window, center=True).std()
        df['is_anomaly'] = abs(df['clicks'] - rolling_mean) > sensitivity * rolling_std
        df['is_anomaly'] = df['is_anomaly'].fillna(False)
    
    anomaly_count = df['is_anomaly'].sum()
    st.metric(t("anomaly_count"), int(anomaly_count))
    
    # 可视化
    st.subheader(t("anomaly_results"))
    fig = go.Figure()
    
    # 正常点
    normal = df[~df['is_anomaly']]
    fig.add_trace(go.Scatter(
        x=normal['data_date'], y=normal['clicks'],
        mode='lines+markers', name=t('clicks'),
        line=dict(color='#667eea'), marker=dict(size=4)
    ))
    
    # 异常点
    anomalies = df[df['is_anomaly']]
    fig.add_trace(go.Scatter(
        x=anomalies['data_date'], y=anomalies['clicks'],
        mode='markers', name='Anomaly',
        marker=dict(color='red', size=12, symbol='x')
    ))
    
    fig.update_layout(height=450, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # 异常详情
    if anomaly_count > 0:
        st.subheader(t("anomaly_detail"))
        anomaly_df = anomalies[['data_date', 'clicks', 'impressions', 'ctr', 'position']].copy()
        anomaly_df.columns = ['Date', t('clicks'), t('impressions'), 'CTR', t('position')]
        st.dataframe(anomaly_df, use_container_width=True, hide_index=True)


# ============================================================
# 主路由
# ============================================================
if page == t('nav_overview'):
    render_overview()
elif page == t('nav_health'):
    render_health_score()
elif page == t('nav_search'):
    render_search_trends()
elif page == t('nav_page'):
    render_page_effectiveness()
elif page == t('nav_country'):
    render_country()
elif page == t('nav_device'):
    render_device()
elif page == t('nav_anomaly'):
    render_anomaly()

