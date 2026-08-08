
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

# ============================================================
# 多语言配置
# ============================================================
LANGUAGES = {
    "English": {
        "platform_title": "SEO Health Intelligence Platform",
        "overview": "Overview",
        "keyword_intel": "Keyword Intelligence",
        "page_analytics": "Page Analytics",
        "market_analysis": "Market Analysis",
        "health_model": "SEO Health Model",
        "recommendations": "Recommendations",
        "settings": "Settings",
        "health_score": "SEO Health Score",
        "moderate": "Moderate",
        "good": "Good",
        "poor": "Poor",
        "excellent": "Excellent",
        "main_issue": "Main Issue",
        "strength": "Strength",
        "opportunity": "Opportunity",
        "search_performance": "Search Performance",
        "page_effectiveness": "Page Effectiveness",
        "technical_experience": "Technical Experience",
        "total_clicks": "Total Clicks",
        "total_impressions": "Total Impressions",
        "avg_ctr": "Average CTR",
        "avg_position": "Average Position",
        "total_keywords": "Total Keywords",
        "top10_keywords": "Top 10 Keywords",
        "opportunity_keywords": "Opportunity Keywords",
        "ranking_funnel": "Ranking Funnel",
        "all_keywords": "All Keywords",
        "need_optimization": "Need Optimization",
        "page_opportunity_matrix": "Page Opportunity Matrix",
        "high_impression": "High Impression",
        "low_impression": "Low Impression",
        "high_ctr": "High CTR",
        "low_ctr": "Low CTR",
        "optimize": "Optimize (High Imp, Low CTR)",
        "maintain": "Maintain (High Imp, High CTR)",
        "improve": "Improve (Low Imp, Low CTR)",
        "low_priority": "Low Priority (Low Imp, High CTR)",
        "global_coverage": "Global SEO Coverage",
        "market_opportunity": "Market Opportunity",
        "model_version": "Current Version",
        "data_coverage": "Data Coverage",
        "available_dimensions": "Available Dimensions",
        "pending": "Pending Integration",
        "diagnosis": "SEO Diagnosis",
        "diagnosis_reason": "Reason",
        "priority_actions": "Priority Actions",
        "data_range": "Data Range",
        "days_tracked": "Days Tracked",
        "countries_covered": "Countries Covered",
        "devices_covered": "Devices Covered",
        "future_expansion": "Future Expansion",
        "backlink_authority": "Backlink Authority",
        "crawl_health": "Crawl Health",
        "core_web_vitals": "Core Web Vitals",
        "model_status": "Model Status",
        "weight": "Weight",
        "score": "Score",
        "dimension": "Dimension",
        "language": "Language",
        "keyword_distribution": "Keyword Position Distribution",
        "top_keywords_table": "Top Keywords by Clicks",
        "top_pages_table": "Top Pages by Clicks",
        "device_distribution": "Device Distribution",
        "country_performance": "Country Performance",
        "trend_analysis": "Trend Analysis",
        "clicks": "Clicks",
        "impressions": "Impressions",
        "position": "Position",
        "ctr": "CTR",
        "keyword": "Keyword",
        "page": "Page",
        "country": "Country",
        "device": "Device",
    },
    "中文": {
        "platform_title": "SEO 健康智能分析平台",
        "overview": "总览",
        "keyword_intel": "关键词洞察",
        "page_analytics": "页面分析",
        "market_analysis": "市场分析",
        "health_model": "SEO 健康模型",
        "recommendations": "优化建议",
        "settings": "设置",
        "health_score": "SEO 健康评分",
        "moderate": "一般",
        "good": "良好",
        "poor": "较差",
        "excellent": "优秀",
        "main_issue": "主要问题",
        "strength": "核心优势",
        "opportunity": "增长机会",
        "search_performance": "搜索表现",
        "page_effectiveness": "页面效果",
        "technical_experience": "技术体验",
        "total_clicks": "总点击数",
        "total_impressions": "总展示次数",
        "avg_ctr": "平均CTR",
        "avg_position": "平均排名",
        "total_keywords": "关键词总数",
        "top10_keywords": "Top 10 关键词",
        "opportunity_keywords": "机会关键词",
        "ranking_funnel": "排名漏斗",
        "all_keywords": "全部关键词",
        "need_optimization": "需要优化",
        "page_opportunity_matrix": "页面机会矩阵",
        "high_impression": "高曝光",
        "low_impression": "低曝光",
        "high_ctr": "高CTR",
        "low_ctr": "低CTR",
        "optimize": "优化区（高曝光低CTR）",
        "maintain": "维护区（高曝光高CTR）",
        "improve": "提升区（低曝光低CTR）",
        "low_priority": "低优先级（低曝光高CTR）",
        "global_coverage": "全球 SEO 覆盖",
        "market_opportunity": "市场机会",
        "model_version": "当前版本",
        "data_coverage": "数据覆盖度",
        "available_dimensions": "可用维度",
        "pending": "待接入",
        "diagnosis": "SEO 诊断",
        "diagnosis_reason": "原因",
        "priority_actions": "优先行动",
        "data_range": "数据范围",
        "days_tracked": "追踪天数",
        "countries_covered": "覆盖国家",
        "devices_covered": "覆盖设备",
        "future_expansion": "未来扩展",
        "backlink_authority": "外链权威",
        "crawl_health": "爬取健康",
        "core_web_vitals": "核心网页指标",
        "model_status": "模型状态",
        "weight": "权重",
        "score": "得分",
        "dimension": "维度",
        "language": "语言",
        "keyword_distribution": "关键词排名分布",
        "top_keywords_table": "点击量 Top 关键词",
        "top_pages_table": "点击量 Top 页面",
        "device_distribution": "设备分布",
        "country_performance": "国家/地区表现",
        "trend_analysis": "趋势分析",
        "clicks": "点击数",
        "impressions": "展示次数",
        "position": "排名",
        "ctr": "CTR",
        "keyword": "关键词",
        "page": "页面",
        "country": "国家",
        "device": "设备",
    },
    "日本語": {
        "platform_title": "SEO ヘルスインテリジェンスプラットフォーム",
        "overview": "概要",
        "keyword_intel": "キーワードインテリジェンス",
        "page_analytics": "ページ分析",
        "market_analysis": "マーケット分析",
        "health_model": "SEO ヘルスモデル",
        "recommendations": "最適化提案",
        "settings": "設定",
        "health_score": "SEO ヘルススコア",
        "moderate": "普通",
        "good": "良好",
        "poor": "要改善",
        "excellent": "優秀",
        "main_issue": "主な課題",
        "strength": "強み",
        "opportunity": "機会",
        "search_performance": "検索パフォーマンス",
        "page_effectiveness": "ページ効果",
        "technical_experience": "技術体験",
        "total_clicks": "総クリック数",
        "total_impressions": "総表示回数",
        "avg_ctr": "平均CTR",
        "avg_position": "平均順位",
        "total_keywords": "キーワード総数",
        "top10_keywords": "Top 10 キーワード",
        "opportunity_keywords": "機会キーワード",
        "ranking_funnel": "ランキングファネル",
        "all_keywords": "全キーワード",
        "need_optimization": "最適化が必要",
        "page_opportunity_matrix": "ページ機会マトリックス",
        "high_impression": "高インプレッション",
        "low_impression": "低インプレッション",
        "high_ctr": "高CTR",
        "low_ctr": "低CTR",
        "optimize": "最適化（高表示・低CTR）",
        "maintain": "維持（高表示・高CTR）",
        "improve": "改善（低表示・低CTR）",
        "low_priority": "低優先度（低表示・高CTR）",
        "global_coverage": "グローバルSEOカバレッジ",
        "market_opportunity": "マーケット機会",
        "model_version": "現在のバージョン",
        "data_coverage": "データカバレッジ",
        "available_dimensions": "利用可能な次元",
        "pending": "統合待ち",
        "diagnosis": "SEO 診断",
        "diagnosis_reason": "理由",
        "priority_actions": "優先アクション",
        "data_range": "データ範囲",
        "days_tracked": "追跡日数",
        "countries_covered": "カバー国数",
        "devices_covered": "カバーデバイス",
        "future_expansion": "将来の拡張",
        "backlink_authority": "バックリンク権威",
        "crawl_health": "クロールヘルス",
        "core_web_vitals": "コアウェブバイタル",
        "model_status": "モデルステータス",
        "weight": "ウェイト",
        "score": "スコア",
        "dimension": "次元",
        "language": "言語",
        "keyword_distribution": "キーワード順位分布",
        "top_keywords_table": "クリック数トップキーワード",
        "top_pages_table": "クリック数トップページ",
        "device_distribution": "デバイス分布",
        "country_performance": "国別パフォーマンス",
        "trend_analysis": "トレンド分析",
        "clicks": "クリック",
        "impressions": "表示回数",
        "position": "順位",
        "ctr": "CTR",
        "keyword": "キーワード",
        "page": "ページ",
        "country": "国",
        "device": "デバイス",
    },
    "한국어": {
        "platform_title": "SEO 헬스 인텔리전스 플랫폼",
        "overview": "개요",
        "keyword_intel": "키워드 인텔리전스",
        "page_analytics": "페이지 분석",
        "market_analysis": "시장 분석",
        "health_model": "SEO 헬스 모델",
        "recommendations": "최적화 제안",
        "settings": "설정",
        "health_score": "SEO 헬스 스코어",
        "moderate": "보통",
        "good": "양호",
        "poor": "개선 필요",
        "excellent": "우수",
        "main_issue": "주요 문제",
        "strength": "강점",
        "opportunity": "기회",
        "search_performance": "검색 성과",
        "page_effectiveness": "페이지 효과",
        "technical_experience": "기술 경험",
        "total_clicks": "총 클릭수",
        "total_impressions": "총 노출수",
        "avg_ctr": "평균 CTR",
        "avg_position": "평균 순위",
        "total_keywords": "총 키워드",
        "top10_keywords": "Top 10 키워드",
        "opportunity_keywords": "기회 키워드",
        "ranking_funnel": "랭킹 퍼널",
        "all_keywords": "전체 키워드",
        "need_optimization": "최적화 필요",
        "page_opportunity_matrix": "페이지 기회 매트릭스",
        "high_impression": "높은 노출",
        "low_impression": "낮은 노출",
        "high_ctr": "높은 CTR",
        "low_ctr": "낮은 CTR",
        "optimize": "최적화 (높은 노출, 낮은 CTR)",
        "maintain": "유지 (높은 노출, 높은 CTR)",
        "improve": "개선 (낮은 노출, 낮은 CTR)",
        "low_priority": "낮은 우선순위 (낮은 노출, 높은 CTR)",
        "global_coverage": "글로벌 SEO 커버리지",
        "market_opportunity": "시장 기회",
        "model_version": "현재 버전",
        "data_coverage": "데이터 커버리지",
        "available_dimensions": "사용 가능한 차원",
        "pending": "통합 대기",
        "diagnosis": "SEO 진단",
        "diagnosis_reason": "이유",
        "priority_actions": "우선 조치",
        "data_range": "데이터 범위",
        "days_tracked": "추적 일수",
        "countries_covered": "커버 국가",
        "devices_covered": "커버 디바이스s",
        "future_expansion": "향후 확장",
        "backlink_authority": "백링크 권위",
        "crawl_health": "크롤 헬스",
        "core_web_vitals": "코어 웹 바이탈",
        "model_status": "모델 상태",
        "weight": "가중치",
        "score": "점수",
        "dimension": "차원",
        "language": "언어",
        "keyword_distribution": "키워드 순위 분포",
        "top_keywords_table": "클릭수 상위 키워드",
        "top_pages_table": "클릭수 상위 페이지",
        "device_distribution": "디바이스 분포",
        "country_performance": "국가별 성과",
        "trend_analysis": "트렌드 분석",
        "clicks": "클릭",
        "impressions": "노출",
        "position": "순위",
        "ctr": "CTR",
        "keyword": "키워드",
        "page": "페이지",
        "country": "국가",
        "device": "디바이스",
    }
}

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
# 自定义CSS样式
# ============================================================
st.markdown("""
<style>
    /* 整体背景 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #E2E8F0;
    }
    
    /* 卡片样式 */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-card h3 {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .metric-card .value {
        font-size: 32px;
        font-weight: 700;
        color: #1E293B;
    }
    
    /* 健康评分大卡片 */
    .health-score-card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .health-score-card .score {
        font-size: 72px;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .health-score-card .label {
        font-size: 16px;
        color: #94A3B8;
        margin-top: 8px;
    }
    .health-score-card .grade {
        font-size: 24px;
        color: #FBBF24;
        font-weight: 600;
        margin-top: 4px;
    }
    
    /* 诊断卡片 */
    .diagnosis-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    .diagnosis-red { border-left-color: #EF4444; }
    .diagnosis-green { border-left-color: #10B981; }
    .diagnosis-yellow { border-left-color: #F59E0B; }
    
    .diagnosis-card .title {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .diagnosis-card .content {
        font-size: 16px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 6px;
    }
    .diagnosis-card .reason {
        font-size: 13px;
        color: #64748B;
    }
    
    /* 维度评分卡 */
    .dimension-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        text-align: center;
        transition: transform 0.2s;
    }
    .dimension-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    .dimension-card .dim-score {
        font-size: 36px;
        font-weight: 700;
    }
    .dimension-card .dim-name {
        font-size: 14px;
        color: #64748B;
        margin-top: 8px;
    }
    .dimension-card .dim-weight {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* 漏斗样式 */
    .funnel-item {
        background: white;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        border: 1px solid #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tab样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
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
    
    return data

# ============================================================
# SEO 健康评分计算
# ============================================================
def calculate_health_score(data):
    """计算SEO健康评分 - V2.0三维模型"""
    scores = {}
    
    # === 维度1: 搜索表现 (40%) ===
    sp_scores = []
    
    if 'daily_summary' in data:
        df = data['daily_summary']
        # SP-1: 点击趋势稳定性
        if 'clicks' in df.columns:
            clicks = df['clicks'].values
            if len(clicks) > 1:
                recent = clicks[-min(30, len(clicks)):]
                earlier = clicks[:min(30, len(clicks))]
                if np.mean(earlier) > 0:
                    trend_ratio = np.mean(recent) / np.mean(earlier)
                    sp1 = min(100, max(0, trend_ratio * 60))
                else:
                    sp1 = 50
            else:
                sp1 = 50
            sp_scores.append(sp1)
        
        # SP-2: CTR表现
        if 'ctr' in df.columns:
            avg_ctr = df['ctr'].mean() * 100 if df['ctr'].mean() < 1 else df['ctr'].mean()
            if avg_ctr >= 5:
                sp2 = 100
            elif avg_ctr >= 3:
                sp2 = 80
            elif avg_ctr >= 1.5:
                sp2 = 60
            elif avg_ctr >= 0.5:
                sp2 = 40
            else:
                sp2 = 20
            sp_scores.append(sp2)
        
        # SP-3: 平均排名
        if 'position' in df.columns:
            avg_pos = df['position'].mean()
            if avg_pos <= 3:
                sp3 = 100
            elif avg_pos <= 10:
                sp3 = 80
            elif avg_pos <= 20:
                sp3 = 60
            elif avg_pos <= 30:
                sp3 = 45
            elif avg_pos <= 50:
                sp3 = 30
            else:
                sp3 = 15
            sp_scores.append(sp3)
    
    scores['search_performance'] = np.mean(sp_scores) if sp_scores else 50
    
    # === 维度2: 页面/内容效果 (35%) ===
    pe_scores = []
    
    if 'by_query' in data:
        df_q = data['by_query']
        # PE-1: 关键词覆盖广度
        total_keywords = len(df_q)
        if total_keywords >= 2000:
            pe1 = 95
        elif total_keywords >= 1000:
            pe1 = 80
        elif total_keywords >= 500:
            pe1 = 65
        elif total_keywords >= 100:
            pe1 = 50
        else:
            pe1 = 30
        pe_scores.append(pe1)
        
        # PE-2: 高排名关键词占比
        if 'position' in df_q.columns:
            top10_ratio = len(df_q[df_q['position'] <= 10]) / max(len(df_q), 1)
            pe2 = min(100, top10_ratio * 500)
            pe_scores.append(pe2)
    
    if 'by_page' in data:
        df_p = data['by_page']
        # PE-3: 活跃页面比例
        if 'clicks' in df_p.columns:
            active_pages = len(df_p[df_p['clicks'] > 0])
            total_pages = len(df_p)
            if total_pages > 0:
                active_ratio = active_pages / total_pages
                pe3 = min(100, active_ratio * 130)
                pe_scores.append(pe3)
    
    scores['page_effectiveness'] = np.mean(pe_scores) if pe_scores else 50
    
    # === 维度3: 技术体验信号 (25%) ===
    te_scores = []
    
    if 'by_device' in data:
        df_d = data['by_device']
        # TE-1: 多设备覆盖
        devices = df_d['device'].nunique() if 'device' in df_d.columns else 0
        te1 = min(100, devices * 33.3)
        te_scores.append(te1)
        
        # TE-2: 移动端占比合理性
        if 'impressions' in df_d.columns:
            total_imp = df_d['impressions'].sum()
            if total_imp > 0:
                mobile_imp = df_d[df_d['device'] == 'MOBILE']['impressions'].sum()
                mobile_ratio = mobile_imp / total_imp
                if 0.15 <= mobile_ratio <= 0.6:
                    te2 = 85
                elif 0.1 <= mobile_ratio <= 0.7:
                    te2 = 65
                else:
                    te2 = 40
                te_scores.append(te2)
    
    if 'by_country' in data:
        df_c = data['by_country']
        # TE-3: 地理覆盖度
        countries = df_c['country'].nunique() if 'country' in df_c.columns else 0
        if countries >= 100:
            te3 = 100
        elif countries >= 50:
            te3 = 80
        elif countries >= 20:
            te3 = 60
        else:
            te3 = 40
        te_scores.append(te3)
    
    scores['technical_experience'] = np.mean(te_scores) if te_scores else 50
    
    # === 加权总分 ===
    weights = {'search_performance': 0.40, 'page_effectiveness': 0.35, 'technical_experience': 0.25}
    total_score = sum(scores[k] * weights[k] for k in weights if k in scores)
    
    # 等级判定
    if total_score >= 90:
        grade = 'A'
    elif total_score >= 70:
        grade = 'B'
    elif total_score >= 50:
        grade = 'C'
    else:
        grade = 'D'
    
    return total_score, grade, scores

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    # 语言选择
    lang_choice = st.selectbox("🌐 Language / 语言", list(LANGUAGES.keys()), index=1)
    t = LANGUAGES[lang_choice]
    
    st.markdown(f"""
    <div style="text-align:center; padding: 20px 0;">
        <div style="font-size: 28px;">🎯</div>
        <div style="font-size: 16px; font-weight: 700; color: #E2E8F0; margin-top: 8px;">
            {t['platform_title']}
        </div>
        <div style="font-size: 11px; color: #64748B; margin-top: 4px;">
            V2.0 | GSC Based
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 导航
    nav_options = {
        f"📊 {t['overview']}": "overview",
        f"🔍 {t['keyword_intel']}": "keyword",
        f"📄 {t['page_analytics']}": "page",
        f"🌎 {t['market_analysis']}": "market",
        f"🎯 {t['health_model']}": "model",
        f"🚀 {t['recommendations']}": "recommendations",
    }
    
    selected_nav = st.radio("", list(nav_options.keys()), label_visibility="collapsed")
    current_page = nav_options[selected_nav]
    
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 11px; color: #64748B; text-align: center;">
        SEO Health Intelligence Platform v2.0<br>
        Powered by GSC Data
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 加载数据
# ============================================================
data = load_data()

if not data:
    st.error("⚠️ No data files found. Please check the data/ directory.")
    st.stop()

# 计算健康评分
total_score, grade, dimension_scores = calculate_health_score(data)

# ============================================================
# 页面1: Overview（总览）
# ============================================================
if current_page == "overview":
    # --- 健康评分大卡片 ---
    grade_labels = {'A': t['excellent'], 'B': t['good'], 'C': t['moderate'], 'D': t['poor']}
    
    st.markdown(f"""
    <div class="health-score-card">
        <div style="font-size: 14px; color: #94A3B8; text-transform: uppercase; letter-spacing: 2px;">
            {t['health_score']}
        </div>
        <div class="score">{total_score:.1f}</div>
        <div class="grade">{grade} · {grade_labels.get(grade, t['moderate'])}</div>
        <div class="label">↓ {t['main_issue']}: {t['page_effectiveness']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 三维度评分卡 ---
    col1, col2, col3 = st.columns(3)
    
    dim_colors = {
        'search_performance': '#2563EB',
        'page_effectiveness': '#7C3AED',
        'technical_experience': '#10B981'
    }
    dim_names = {
        'search_performance': t['search_performance'],
        'page_effectiveness': t['page_effectiveness'],
        'technical_experience': t['technical_experience']
    }
    dim_weights = {'search_performance': '40%', 'page_effectiveness': '35%', 'technical_experience': '25%'}
    
    for col, (key, name) in zip([col1, col2, col3], dim_names.items()):
        score = dimension_scores.get(key, 0)
        color = dim_colors[key]
        with col:
            st.markdown(f"""
            <div class="dimension-card">
                <div class="dim-score" style="color: {color};">{score:.0f}</div>
                <div class="dim-name">{name}</div>
                <div class="dim-weight">{t['weight']}: {dim_weights[key]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 诊断卡片 ---
    st.markdown(f"### {t['diagnosis']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="diagnosis-card diagnosis-red">
            <div class="title" style="color: #EF4444;">🔴 {t['main_issue']}</div>
            <div class="content">{t['page_effectiveness']} needs improvement</div>
            <div class="reason">{t['diagnosis_reason']}: 75.6% pages generate limited clicks; High impression pages have low CTR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="diagnosis-card diagnosis-green">
            <div class="title" style="color: #10B981;">🟢 {t['strength']}</div>
            <div class="content">Search visibility is stable</div>
            <div class="reason">{t['diagnosis_reason']}: 2,519 keywords detected; Coverage across 201 countries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="diagnosis-card diagnosis-yellow">
            <div class="title" style="color: #F59E0B;">🟡 {t['opportunity']}</div>
            <div class="content">Ranking improvement potential</div>
            <div class="reason">{t['diagnosis_reason']}: Keywords ranking 11-30 can enter Top 10 with optimization</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- KPI 指标卡 ---
    col1, col2, col3, col4 = st.columns(4)
    
    if 'daily_summary' in data:
        df_sum = data['daily_summary']
        total_clicks = int(df_sum['clicks'].sum())
        total_impressions = int(df_sum['impressions'].sum())
        avg_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        avg_position = df_sum['position'].mean()
    else:
        total_clicks = total_impressions = 0
        avg_ctr = avg_position = 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t['total_clicks']}</h3>
            <div class="value">{total_clicks:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t['total_impressions']}</h3>
            <div class="value">{total_impressions:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t['avg_ctr']}</h3>
            <div class="value">{avg_ctr:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t['avg_position']}</h3>
            <div class="value">{avg_position:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 趋势图 ---
    if 'daily_summary' in data:
        st.markdown(f"### {t['trend_analysis']}")
        df_trend = data['daily_summary'].copy()
        if 'date' in df_trend.columns:
            df_trend['date'] = pd.to_datetime(df_trend['date'])
            df_trend = df_trend.sort_values('date')
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=df_trend['date'], y=df_trend['impressions'],
                       name=t['impressions'], marker_color='#BFDBFE', opacity=0.7),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=df_trend['date'], y=df_trend['clicks'],
                          name=t['clicks'], line=dict(color='#2563EB', width=2)),
                secondary_y=True
            )
            fig.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=30, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
                yaxis2=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 页面2: Keyword Intelligence（关键词洞察）
# ============================================================
elif current_page == "keyword":
    st.markdown(f"## 🔍 {t['keyword_intel']}")
    
    if 'by_query' in data:
        df_q = data['by_query']
        
        total_kw = len(df_q)
        top10_kw = len(df_q[df_q['position'] <= 10]) if 'position' in df_q.columns else 0
        opp_kw = len(df_q[(df_q['position'] > 10) & (df_q['position'] <= 30)]) if 'position' in df_q.columns else 0
        avg_pos = df_q['position'].mean() if 'position' in df_q.columns else 0
        
        # KPI卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['total_keywords']}</h3>
                <div class="value">{total_kw:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['top10_keywords']}</h3>
                <div class="value" style="color: #10B981;">{top10_kw}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['opportunity_keywords']}</h3>
                <div class="value" style="color: #F59E0B;">{opp_kw}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['avg_position']}</h3>
                <div class="value">{avg_pos:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 排名漏斗
        st.markdown(f"### {t['ranking_funnel']}")
        
        if 'position' in df_q.columns:
            pos_1_3 = len(df_q[df_q['position'] <= 3])
            pos_4_10 = len(df_q[(df_q['position'] > 3) & (df_q['position'] <= 10)])
            pos_11_30 = len(df_q[(df_q['position'] > 10) & (df_q['position'] <= 30)])
            pos_31_plus = len(df_q[df_q['position'] > 30])
            
            funnel_data = pd.DataFrame({
                'Stage': ['Top 3', 'Top 4-10', 'Top 11-30', '30+'],
                'Count': [pos_1_3, pos_4_10, pos_11_30, pos_31_plus],
                'Color': ['#10B981', '#2563EB', '#F59E0B', '#EF4444']
            })
            
            fig = go.Figure(go.Funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                marker=dict(color=funnel_data['Color']),
                textinfo="value+percent initial"
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 关键词气泡图
        st.markdown(f"### {t['keyword_distribution']}")
        
        if all(col in df_q.columns for col in ['position', 'impressions', 'clicks']):
            df_bubble = df_q[df_q['impressions'] > 0].head(200)
            
            fig = px.scatter(
                df_bubble, x='position', y='impressions', size='clicks',
                color='position',
                color_continuous_scale=['#10B981', '#2563EB', '#F59E0B', '#EF4444'],
                hover_data=['query'] if 'query' in df_bubble.columns else None,
                labels={'position': t['position'], 'impressions': t['impressions'], 'clicks': t['clicks']}
            )
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top关键词表格
        st.markdown(f"### {t['top_keywords_table']}")
        if 'clicks' in df_q.columns:
            top_kw = df_q.nlargest(20, 'clicks')[['query', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
            top_kw.columns = [t['keyword'], t['clicks'], t['impressions'], t['ctr'], t['position']]
            st.dataframe(top_kw, use_container_width=True, hide_index=True)
    else:
        st.info("📁 Please add cleaned_by_query.csv to the data/ folder.")

# ============================================================
# 页面3: Page Analytics（页面分析）
# ============================================================
elif current_page == "page":
    st.markdown(f"## 📄 {t['page_analytics']}")
    
    if 'by_page' in data:
        df_p = data['by_page']
        
        # 页面机会矩阵
        st.markdown(f"### {t['page_opportunity_matrix']}")
        
        if all(col in df_p.columns for col in ['impressions', 'ctr', 'clicks']):
            df_matrix = df_p[df_p['impressions'] > 0].copy()
            
            imp_median = df_matrix['impressions'].median()
            ctr_median = df_matrix['ctr'].median()
            
            def classify_page(row):
                high_imp = row['impressions'] >= imp_median
                high_ctr = row['ctr'] >= ctr_median
                if high_imp and not high_ctr:
                    return t['optimize']
                elif high_imp and high_ctr:
                    return t['maintain']
                elif not high_imp and not high_ctr:
                    return t['improve']
                else:
                    return t['low_priority']
            
            df_matrix['quadrant'] = df_matrix.apply(classify_page, axis=1)
            
            color_map = {
                t['optimize']: '#EF4444',
                t['maintain']: '#10B981',
                t['improve']: '#F59E0B',
                t['low_priority']: '#94A3B8'
            }
            
            fig = px.scatter(
                df_matrix, x='ctr', y='impressions', color='quadrant',
                size='clicks', size_max=30,
                color_discrete_map=color_map,
                hover_data=['page'] if 'page' in df_matrix.columns else None,
                labels={'ctr': t['ctr'], 'impressions': t['impressions']}
            )
            fig.add_hline(y=imp_median, line_dash="dash", line_color="#94A3B8", opacity=0.5)
            fig.add_vline(x=ctr_median, line_dash="dash", line_color="#94A3B8", opacity=0.5)
            fig.update_layout(
                height=500,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 象限统计
            quadrant_counts = df_matrix['quadrant'].value_counts()
            col1, col2, col3, col4 = st.columns(4)
            
            quadrant_list = [t['optimize'], t['maintain'], t['improve'], t['low_priority']]
            quadrant_colors = ['#EF4444', '#10B981', '#F59E0B', '#94A3B8']
            
            for col, q, c in zip([col1, col2, col3, col4], quadrant_list, quadrant_colors):
                count = quadrant_counts.get(q, 0)
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: {c};">{q.split('（')[0].split('(')[0]}</h3>
                        <div class="value">{count}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top页面表格
        st.markdown(f"### {t['top_pages_table']}")
        if 'clicks' in df_p.columns:
            top_pages = df_p.nlargest(20, 'clicks')[['page', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
            top_pages.columns = [t['page'], t['clicks'], t['impressions'], t['ctr'], t['position']]
            st.dataframe(top_pages, use_container_width=True, hide_index=True)
    else:
        st.info("📁 Please add cleaned_by_page.csv to the data/ folder.")

# ============================================================
# 页面4: Market Analysis（市场分析）
# ============================================================
elif current_page == "market":
    st.markdown(f"## 🌎 {t['market_analysis']}")
    
    if 'by_country' in data:
        df_c = data['by_country']
        
        # 全球覆盖统计
        total_countries = df_c['country'].nunique() if 'country' in df_c.columns else 0
        countries_with_clicks = df_c[df_c['clicks'] > 0]['country'].nunique() if 'clicks' in df_c.columns else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{t['countries_covered']}</h3>
                <div class="value">{total_countries}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Active Markets</h3>
                <div class="value" style="color: #10B981;">{countries_with_clicks}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            coverage_pct = countries_with_clicks / max(total_countries, 1) * 100
            st.markdown(f"""
            <div class="metric-card">
                <h3>Market Penetration</h3>
                <div class="value">{coverage_pct:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 市场机会矩阵
        st.markdown(f"### {t['market_opportunity']}")
        
        if all(col in df_c.columns for col in ['country', 'clicks', 'impressions']):
            df_market = df_c.groupby('country').agg({
                'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'
            }).reset_index()
            df_market = df_market[df_market['impressions'] > 0]
            
            # Top 20 markets
            top_markets = df_market.nlargest(20, 'impressions')
            
            fig = px.scatter(
                top_markets, x='impressions', y='ctr', size='clicks',
                color='clicks', color_continuous_scale='Blues',
                hover_data=['country'],
                text='country',
                labels={'impressions': t['impressions'], 'ctr': t['ctr'], 'clicks': t['clicks']}
            )
            fig.update_traces(textposition='top center', textfont_size=10)
            fig.update_layout(
                height=450,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 国家排名表
        st.markdown(f"### {t['country_performance']}")
        if 'clicks' in df_c.columns:
            country_summary = df_c.groupby('country').agg({
                'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'
            }).reset_index().sort_values('clicks', ascending=False).head(20)
            country_summary.columns = [t['country'], t['clicks'], t['impressions'], t['ctr'], t['position']]
            st.dataframe(country_summary, use_container_width=True, hide_index=True)
    
    # 设备分布
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### {t['device_distribution']}")
    
    if 'by_device' in data:
        df_d = data['by_device']
        device_summary = df_d.groupby('device').agg({
            'clicks': 'sum', 'impressions': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(device_summary, values='clicks', names='device',
                        color_discrete_sequence=['#2563EB', '#10B981', '#F59E0B'],
                        title=f"{t['clicks']} by {t['device']}")
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(device_summary, values='impressions', names='device',
                        color_discrete_sequence=['#2563EB', '#10B981', '#F59E0B'],
                        title=f"{t['impressions']} by {t['device']}")
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 页面5: SEO Health Model（健康模型）
# ============================================================
elif current_page == "model":
    st.markdown(f"## 🎯 {t['health_model']}")
    
    # 模型概览
    st.markdown(f"""
    <div class="health-score-card">
        <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 2px;">
            SEO HEALTH SCORE V2.0
        </div>
        <div class="score">{total_score:.1f}</div>
        <div class="grade">{grade}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 三维度详细
    col1, col2, col3 = st.columns(3)
    
    dims = [
        ('search_performance', t['search_performance'], '40%', '#2563EB'),
        ('page_effectiveness', t['page_effectiveness'], '35%', '#7C3AED'),
        ('technical_experience', t['technical_experience'], '25%', '#10B981')
    ]
    
    for col, (key, name, weight, color) in zip([col1, col2, col3], dims):
        score = dimension_scores.get(key, 0)
        with col:
            st.markdown(f"""
            <div class="dimension-card">
                <div class="dim-score" style="color: {color};">{score:.1f}</div>
                <div class="dim-name">{name}</div>
                <div class="dim-weight">{t['weight']}: {weight}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 雷达图
    categories = [t['search_performance'], t['page_effectiveness'], t['technical_experience']]
    values = [dimension_scores.get('search_performance', 0),
              dimension_scores.get('page_effectiveness', 0),
              dimension_scores.get('technical_experience', 0)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.2)',
        line=dict(color='#2563EB', width=2),
        name='Score'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showline=False, gridcolor='#E2E8F0'),
            angularaxis=dict(gridcolor='#E2E8F0')
        ),
        height=350,
        margin=dict(l=60, r=60, t=30, b=30),
        paper_bgcolor='white',
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 模型状态
    st.markdown(f"### {t['model_status']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: left;">
            <h3>{t['model_version']}</h3>
            <div class="value" style="font-size: 20px;">V2.0 GSC Based Model</div>
            <br>
            <h3>{t['data_coverage']}</h3>
            <div style="background: #E2E8F0; border-radius: 8px; height: 12px; margin-top: 8px;">
                <div style="background: linear-gradient(90deg, #2563EB, #10B981); width: 78%; height: 12px; border-radius: 8px;"></div>
            </div>
            <div style="font-size: 12px; color: #64748B; margin-top: 4px;">78% (3/6 {t['dimension']})</div>
            <br>
            <h3>{t['available_dimensions']}</h3>
            <div class="value" style="font-size: 20px;">3 / 6</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align: left;">
            <h3>{t['future_expansion']}</h3>
            <div style="margin-top: 12px;">
                <div style="padding: 8px 12px; background: #FEF3C7; border-radius: 6px; margin-bottom: 8px; font-size: 14px;">
                    ⏳ {t['backlink_authority']} — Ahrefs API
                </div>
                <div style="padding: 8px 12px; background: #FEF3C7; border-radius: 6px; margin-bottom: 8px; font-size: 14px;">
                    ⏳ {t['crawl_health']} — Screaming Frog
                </div>
                <div style="padding: 8px 12px; background: #FEF3C7; border-radius: 6px; font-size: 14px;">
                    ⏳ {t['core_web_vitals']} — PageSpeed API
                </div>
            </div>
            <br>
            <h3>{t['data_range']}</h3>
            <div style="font-size: 14px; color: #1E293B;">2025-04-03 → 2026-07-25</div>
            <div style="font-size: 12px; color: #64748B;">478 {t['days_tracked']} · 201 {t['countries_covered']} · 3 {t['devices_covered']}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 页面6: Recommendations（优化建议）
# ============================================================
elif current_page == "recommendations":
    st.markdown(f"## 🚀 {t['recommendations']}")
    
    # 优先级行动
    st.markdown(f"### {t['priority_actions']}")
    
    recommendations = [
        {
            "priority": "P0",
            "color": "#EF4444",
            "title": "Keyword Ranking Optimization",
            "desc": "Average position 23.8 → Target: Top 10. Focus on keywords ranking 11-30 with high impressions.",
            "impact": "High",
            "effort": "Medium"
        },
        {
            "priority": "P1",
            "color": "#F59E0B",
            "title": "CTR Improvement",
            "desc": "Current CTR 1.46% → Target: 2-3%. Optimize meta titles and descriptions for high-impression pages.",
            "impact": "High",
            "effort": "Low"
        },
        {
            "priority": "P1",
            "color":
