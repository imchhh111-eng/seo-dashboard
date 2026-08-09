
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================
# 全局配置
# ============================================================
st.set_page_config(
    page_title="B2B SEO Health Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 16px; }
    .sidebar-title { font-size: 1.5rem; font-weight: 700; color: #1a56db; padding: 1rem 0; border-bottom: 2px solid #e5e7eb; margin-bottom: 1rem; }
    .metric-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #1a56db; margin: 0.5rem 0; }
    .metric-label { font-size: 0.95rem; color: #6b7280; font-weight: 500; }
    .score-ring { width: 180px; height: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-direction: column; margin: 0 auto; border: 8px solid; }
    .score-number { font-size: 3rem; font-weight: 800; }
    .score-grade { font-size: 1.2rem; font-weight: 600; }
    .page-title { font-size: 1.8rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; }
    .page-subtitle { font-size: 1rem; color: #6b7280; margin-bottom: 1.5rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# V3.3 评分引擎（内嵌）
# ============================================================

def piecewise_linear(value, breakpoints, scores):
    assert len(breakpoints) == len(scores)
    if value <= breakpoints[0]:
        return scores[0]
    if value >= breakpoints[-1]:
        return scores[-1]
    for i in range(len(breakpoints) - 1):
        if breakpoints[i] <= value <= breakpoints[i + 1]:
            ratio = (value - breakpoints[i]) / (breakpoints[i + 1] - breakpoints[i])
            return scores[i] + ratio * (scores[i + 1] - scores[i])
    return scores[-1]


def calculate_gini(values):
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    if n == 0 or np.sum(sorted_vals) == 0:
        return 0
    idx = np.arange(1, n + 1)
    return (2 * np.sum(idx * sorted_vals) - (n + 1) * np.sum(sorted_vals)) / (n * np.sum(sorted_vals))


THRESHOLDS = {
    'ranking': {'bp': [0, 0.4, 0.8, 1.5, 2.5, 5.0], 'sc': [0, 20, 40, 60, 80, 100]},
    'diversity': {'bp': [0, 20, 50, 100, 200, 300], 'sc': [0, 20, 40, 60, 80, 100]},
    'trend_f1': {'bp': [-0.30, -0.20, -0.10, -0.05, -0.02, 0.02, 0.05, 0.10], 'sc': [0, 10, 20, 40, 60, 80, 100, 100]},
    'trend_f2': {'bp': [0, 0.10, 0.30, 0.50, 0.70, 0.90, 1.0], 'sc': [0, 20, 40, 60, 80, 100, 100]},
    'stability': {'bp': [0, 0.30, 0.50, 0.80, 1.20, 2.00, 3.00], 'sc': [100, 100, 80, 60, 40, 20, 0]},
    'ctr': {'bp': [0, 0.3, 0.5, 0.7, 1.0, 1.2, 2.0], 'sc': [0, 30, 50, 70, 90, 100, 100]},
    'page_activity': {'bp': [0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.60], 'sc': [0, 20, 40, 60, 80, 100, 100]},
    'device': {'bp': [0, 0.3, 0.5, 0.7, 0.9, 1.5], 'sc': [20, 40, 60, 80, 100, 100]},
    'region_count': {'bp': [0, 5, 10, 20, 30, 50], 'sc': [0, 20, 40, 60, 80, 100]},
    'region_concentration': {'bp': [0, 0.15, 0.25, 0.40, 0.60, 1.0], 'sc': [100, 100, 80, 60, 40, 20]},
    'content_depth': {'bp': [0, 0.05, 0.10, 0.20, 0.35, 0.50, 0.70], 'sc': [0, 10, 20, 40, 60, 80, 100]},
    'content_freshness': {'bp': [0, 0.05, 0.15, 0.25, 0.40, 0.60, 0.80], 'sc': [0, 10, 20, 40, 60, 80, 100]},
}

WEIGHTS = {
    'ranking': 19, 'diversity': 8, 'trend': 20, 'stability': 8,
    'ctr': 14, 'page_activity': 14, 'device': 2, 'region': 4,
    'concentration': 2, 'content': 9,
}

CTR_BENCHMARKS = {
    (0, 1): 0.398, (1, 2): 0.187, (2, 3): 0.102,
    (3, 5): 0.0625, (5, 10): 0.0276,
    (10, 20): 0.0098, (20, 50): 0.003, (50, 100): 0.0005,
}

GRADE_SYSTEM = [
    (90, 101, 'A+', '卓越', 'Excellent', '#059669'),
    (80, 90, 'A', '优秀', 'Great', '#10b981'),
    (70, 80, 'B+', '良好', 'Good', '#2563eb'),
    (60, 70, 'B', '中上', 'Above Avg', '#3b82f6'),
    (50, 60, 'C+', '中等', 'Average', '#d97706'),
    (40, 50, 'C', '中下', 'Below Avg', '#f59e0b'),
    (30, 40, 'D+', '较差', 'Poor', '#dc2626'),
    (20, 30, 'D', '差', 'Bad', '#b91c1c'),
    (10, 20, 'E', '危险', 'Critical', '#7f1d1d'),
    (0, 10, 'F', '濒死', 'Failing', '#450a0a'),
]


def calculate_seo_score_v33(data):
    results = {}
    details = {}

    by_date = data.get('by_date')
    by_query = data.get('by_query')
    by_page = data.get('by_page')
    by_device = data.get('by_device')
    by_country = data.get('by_country')
    query_page = data.get('query_page')

    for df_key in ['by_date', 'by_query', 'by_page', 'by_device', 'by_country', 'query_page']:
        df = data.get(df_key)
        if df is not None and 'data_date' in df.columns:
            data[df_key]['data_date'] = pd.to_datetime(df['data_date'])

    by_date = data.get('by_date')
    by_query = data.get('by_query')
    by_page = data.get('by_page')
    by_device = data.get('by_device')
    by_country = data.get('by_country')
    query_page = data.get('query_page')

    months = sorted(by_query['data_date'].unique()) if by_query is not None else []

    if by_date is not None:
        by_date_sorted = by_date.sort_values('data_date').reset_index(drop=True)
        clicks = by_date_sorted['clicks'].values
        n_days = len(clicks)
        daily_avg = clicks.mean()
        scale_factor = min(1.0, daily_avg / 10.0)
    else:
        clicks = np.array([])
        n_days = 0
        daily_avg = 0
        scale_factor = 0.5

    # 指标1: 关键词排名分布 (19%)
    if by_query is not None and len(months) > 0:
        monthly_s1 = []
        for date in months:
            mq = by_query[by_query['data_date'] == date]
            pos = mq['position'].values
            if len(pos) > 0:
                ws = (np.sum(pos <= 3) * 5 + np.sum((pos > 3) & (pos <= 10)) * 3 +
                      np.sum((pos > 10) & (pos <= 20)) * 2 + np.sum((pos > 20) & (pos <= 50)) * 1) / len(pos)
                monthly_s1.append(piecewise_linear(ws, THRESHOLDS['ranking']['bp'], THRESHOLDS['ranking']['sc']))
            else:
                monthly_s1.append(0)
        results['ranking'] = np.median(monthly_s1)
    else:
        results['ranking'] = 0

    # 指标2: 关键词多样性 (8%)
    if by_query is not None and len(months) > 0:
        monthly_s2 = []
        for date in months:
            mq = by_query[by_query['data_date'] == date]
            eff = len(mq[mq['impressions'] >= 10])
            monthly_s2.append(piecewise_linear(eff, THRESHOLDS['diversity']['bp'], THRESHOLDS['diversity']['sc']))
        results['diversity'] = np.median(monthly_s2)
    else:
        results['diversity'] = 0

    # 指标3: 流量趋势-复合F (20%)
    if n_days >= 90:
        segment_rates = []
        for i in range(0, n_days - 90 + 1, 30):
            seg = clicks[i:i + 90]
            x_seg = np.arange(len(seg))
            mean_seg = np.mean(seg)
            if np.std(seg) > 0 and mean_seg >= 1.0:
                slope, _, _, _, _ = scipy_stats.linregress(x_seg, seg)
                rate = slope / mean_seg * 30
                segment_rates.append(rate)
        f1_rate = np.median(segment_rates) if segment_rates else -0.3
        s_f1 = piecewise_linear(f1_rate, THRESHOLDS['trend_f1']['bp'], THRESHOLDS['trend_f1']['sc'])
        peak_90d = max(np.mean(clicks[i:i + 90]) for i in range(0, n_days - 89))
        latest_90d = np.mean(clicks[-90:])
        retention = latest_90d / peak_90d if peak_90d > 0 else 0
        s_f2 = piecewise_linear(retention, THRESHOLDS['trend_f2']['bp'], THRESHOLDS['trend_f2']['sc'])
        results['trend'] = (s_f1 + s_f2) / 2
        details['trend'] = {'f1_rate': f1_rate, 'retention': retention, 's_f1': s_f1, 's_f2': s_f2}
    else:
        results['trend'] = 50

    # 指标4: 流量稳定性 (8%)
    if n_days >= 28:
        x_all = np.arange(n_days)
        slope_all, intercept_all, _, _, _ = scipy_stats.linregress(x_all, clicks)
        predicted = slope_all * x_all + intercept_all
        residuals = clicks - predicted
        rolling_cv = []
        for i in range(28, n_days):
            w_res = residuals[i - 28:i]
            w_mean = np.mean(clicks[i - 28:i])
            if w_mean > 0:
                rolling_cv.append(np.std(w_res) / w_mean)
        cv_median = np.median(rolling_cv) if rolling_cv else 1.0
        results['stability'] = piecewise_linear(cv_median, THRESHOLDS['stability']['bp'], THRESHOLDS['stability']['sc'])
    else:
        results['stability'] = 50

    # 指标5: CTR效率 (14%)
    if by_query is not None and len(months) > 0:
        monthly_s5 = []
        for date in months:
            mq = by_query[by_query['data_date'] == date]
            tw_eff = 0
            tw = 0
            for (low, high), bench in CTR_BENCHMARKS.items():
                seg = mq[(mq['position'] > low) & (mq['position'] <= high)]
                if len(seg) > 0 and seg['impressions'].sum() > 0:
                    actual = seg['clicks'].sum() / seg['impressions'].sum()
                    eff = min(actual / bench, 2.0)
                    w = seg['impressions'].sum()
                    tw_eff += eff * w
                    tw += w
            ctr_eff = tw_eff / tw if tw > 0 else 0
            monthly_s5.append(piecewise_linear(ctr_eff, THRESHOLDS['ctr']['bp'], THRESHOLDS['ctr']['sc']))
        results['ctr'] = np.median(monthly_s5)
    else:
        results['ctr'] = 0

    # 指标6: 页面活跃度 (14%)
    if by_page is not None and len(months) > 0:
        monthly_s6 = []
        for date in months:
            mp = by_page[by_page['data_date'] == date]
            total_p = mp['page'].nunique() if len(mp) > 0 else 0
            click_p = mp[mp['clicks'] > 0]['page'].nunique() if len(mp) > 0 else 0
            rate = click_p / total_p if total_p > 0 else 0
            monthly_s6.append(piecewise_linear(rate, THRESHOLDS['page_activity']['bp'], THRESHOLDS['page_activity']['sc']))
        results['page_activity'] = np.median(monthly_s6)
    else:
        results['page_activity'] = 0

    # 指标7: 设备适配 (2%)
    if by_device is not None and len(months) > 0:
        monthly_s7 = []
        for date in months:
            md = by_device[by_device['data_date'] == date]
            desktop = md[md['device'] == 'DESKTOP']
            mobile = md[md['device'] == 'MOBILE']
            d_ctr = desktop['clicks'].sum() / desktop['impressions'].sum() if len(desktop) > 0 and desktop['impressions'].sum() > 0 else 0
            m_ctr = mobile['clicks'].sum() / mobile['impressions'].sum() if len(mobile) > 0 and mobile['impressions'].sum() > 0 else 0
            ratio = m_ctr / d_ctr if d_ctr > 0 else 0
            monthly_s7.append(piecewise_linear(ratio, THRESHOLDS['device']['bp'], THRESHOLDS['device']['sc']))
        results['device'] = np.median(monthly_s7) * scale_factor
    else:
        results['device'] = 0

    # 指标8: 地区覆盖 (4%)
    if by_country is not None and len(months) > 0:
        monthly_s8 = []
        for date in months:
            mc = by_country[by_country['data_date'] == date]
            c_click = len(mc[mc['clicks'] > 0]) if len(mc) > 0 else 0
            sa = piecewise_linear(c_click, THRESHOLDS['region_count']['bp'], THRESHOLDS['region_count']['sc'])
            if len(mc) > 0 and mc['impressions'].sum() > 0:
                top1 = mc.sort_values('impressions', ascending=False).iloc[0]['impressions'] / mc['impressions'].sum()
            else:
                top1 = 1.0
            sb = piecewise_linear(top1, THRESHOLDS['region_concentration']['bp'], THRESHOLDS['region_concentration']['sc'])
            monthly_s8.append((sa + sb) / 2)
        results['region'] = np.median(monthly_s8) * scale_factor
    else:
        results['region'] = 0

    # 指标9: 页面集中度 (2%)
    if by_page is not None and len(months) > 0:
        recent_6m = months[-6:] if len(months) >= 6 else months
        recent_pages = by_page[by_page['data_date'].isin(recent_6m)]
        page_total = recent_pages.groupby('page')['clicks'].sum()
        pages_with_clicks = page_total[page_total > 0].sort_values().values
        if len(pages_with_clicks) > 1:
            gini = calculate_gini(pages_with_clicks)
            if 0.50 <= gini <= 0.65:
                s9 = 100
            elif gini < 0.50:
                s9 = piecewise_linear(gini, [0, 0.30, 0.50], [40, 60, 100])
            else:
                s9 = piecewise_linear(gini, [0.65, 0.75, 0.85, 0.95, 1.0], [100, 80, 60, 40, 20])
        else:
            gini = 0
            s9 = 0
        results['concentration'] = s9 * scale_factor
    else:
        results['concentration'] = 0

    # 指标10: 内容深度与更新 (9%)
    if query_page is not None and by_query is not None and len(months) > 0:
        monthly_depth = []
        for date in months:
            mqp = query_page[query_page['data_date'] == date]
            if len(mqp) > 0:
                page_kw = mqp.groupby('page')['query'].nunique()
                deep_ratio = len(page_kw[page_kw >= 5]) / len(page_kw) if len(page_kw) > 0 else 0
            else:
                deep_ratio = 0
            monthly_depth.append(piecewise_linear(deep_ratio, THRESHOLDS['content_depth']['bp'], THRESHOLDS['content_depth']['sc']))
        s_depth = np.median(monthly_depth)

        new_rates_rolling = []
        for i, date in enumerate(months):
            mq = by_query[by_query['data_date'] == date]
            current_words = set(mq['query'].unique())
            lookback_start = max(0, i - 6)
            past_words = set()
            for j in range(lookback_start, i):
                past_mq = by_query[by_query['data_date'] == months[j]]
                past_words.update(past_mq['query'].unique())
            if i == 0:
                new_words = current_words
            else:
                new_words = current_words - past_words
            rate = len(new_words) / len(current_words) if len(current_words) > 0 else 0
            new_rates_rolling.append(rate)
        freshness_median = np.median(new_rates_rolling[1:]) if len(new_rates_rolling) > 1 else 0
        s_freshness = piecewise_linear(freshness_median, THRESHOLDS['content_freshness']['bp'], THRESHOLDS['content_freshness']['sc'])
        results['content'] = (s_depth + s_freshness) / 2
    else:
        results['content'] = 0

    # 加权总分
    final_score = sum(results[key] * WEIGHTS[key] / 100 for key in WEIGHTS)

    grade, grade_label, grade_label_en, grade_color = 'F', '濒死', 'Failing', '#450a0a'
    for low, high, g, label_cn, label_en, color in GRADE_SYSTEM:
        if low <= final_score < high:
            grade, grade_label, grade_label_en, grade_color = g, label_cn, label_en, color
            break

    return {
        'final_score': round(final_score, 1),
        'grade': grade,
        'grade_label': grade_label,
        'grade_label_en': grade_label_en,
        'grade_color': grade_color,
        'indicators': results,
        'details': details,
        'scale_factor': scale_factor,
        'daily_avg': daily_avg,
        'n_days': n_days,
        'n_months': len(months),
    }


def generate_diagnosis(score_result, lang='中文'):
    indicators = score_result['indicators']
    diagnosis = []
    RULES = {
        'ranking': {'issue_cn': '关键词排名极差，几乎无Top10词', 'issue_en': 'Keyword rankings critically low', 'action_cn': '聚焦长尾关键词，优化11-20位关键词的页面内容深度和内链', 'action_en': 'Focus on long-tail keywords, optimize content for keywords ranked 11-20'},
        'diversity': {'issue_cn': '有效关键词数量不足，搜索覆盖面窄', 'issue_en': 'Insufficient effective keywords', 'action_cn': '扩展内容矩阵，针对B2B买家旅程各阶段创建内容', 'action_en': 'Expand content matrix for each B2B buyer journey stage'},
        'trend': {'issue_cn': '流量持续下降，站点可能面临严重问题', 'issue_en': 'Traffic continuously declining', 'action_cn': '排查索引问题、算法惩罚、竞争对手抢占；制定内容恢复计划', 'action_en': 'Investigate indexing issues, algorithm penalties, competitor displacement'},
        'stability': {'issue_cn': '流量波动剧烈，缺乏稳定的自然搜索基础', 'issue_en': 'Traffic highly volatile', 'action_cn': '建立常青内容体系，减少对单一关键词/页面的依赖', 'action_en': 'Build evergreen content, reduce single-keyword dependency'},
        'ctr': {'issue_cn': 'CTR效率低于行业基准，标题和描述吸引力不足', 'issue_en': 'CTR below industry benchmark', 'action_cn': '优化Title/Meta Description，加入数字、年份、行动号召词', 'action_en': 'Optimize Title/Meta Description with numbers, dates, CTAs'},
        'page_activity': {'issue_cn': '大量页面零点击，内容资产利用率低', 'issue_en': 'Many pages with zero clicks', 'action_cn': '审计零流量页面：更新、合并或删除；集中资源到高潜力页面', 'action_en': 'Audit zero-traffic pages: update, consolidate, or remove'},
        'content': {'issue_cn': '内容深度不足且更新频率低', 'issue_en': 'Insufficient content depth', 'action_cn': '为核心页面扩展关键词覆盖；建立定期更新机制', 'action_en': 'Expand keyword coverage per page; establish regular update schedule'},
    }
    for key, score in sorted(indicators.items(), key=lambda x: x[1]):
        if key in RULES:
            if score < 20:
                level = 'urgent'
            elif score < 40:
                level = 'attention'
            else:
                continue
            rule = RULES[key]
            diagnosis.append({'key': key, 'score': score, 'level': level, 'weight': WEIGHTS.get(key, 0), 'issue': rule['issue_cn'] if lang == '中文' else rule['issue_en'], 'action': rule['action_cn'] if lang == '中文' else rule['action_en']})
    return diagnosis


# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
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
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 SEO Health Intelligence</div>', unsafe_allow_html=True)
    lang = st.radio("🌐 Language", ['中文', 'English'], horizontal=True, key="lang_switch")
    st.markdown("---")
    nav_items_cn = ["📊 总览仪表盘", "🎯 SEO 健康度评分", "📈 搜索表现趋势", "🔍 关键词洞察", "📄 页面效果分析", "🌍 国家/地区分析", "📱 设备分布", "🚨 流量异常检测", "🚀 优化建议"]
    nav_items_en = ["📊 Overview Dashboard", "🎯 SEO Health Score", "📈 Search Trends", "🔍 Keyword Insights", "📄 Page Analysis", "🌍 Country/Region", "📱 Device Distribution", "🚨 Anomaly Detection", "🚀 Recommendations"]
    nav_items = nav_items_cn if lang == '中文' else nav_items_en
    page = st.radio("导航菜单" if lang == '中文' else "Navigation", nav_items, key="nav_menu")
    st.markdown("---")
    if data.get('by_date') is not None:
        date_range = data['by_date']['data_date']
        st.caption(f"📅 {'数据范围' if lang == '中文' else 'Data Range'}: {date_range.min()} → {date_range.max()}")
    st.caption("B2B SEO Health Intelligence v3.3")

# ============================================================
# 页面1：总览仪表盘
# ============================================================
if page in ["📊 总览仪表盘", "📊 Overview Dashboard"]:
    st.markdown(f'<div class="page-title">{"📊 B2B SEO 总览仪表盘" if lang == "中文" else "📊 B2B SEO Overview Dashboard"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于 GSC 数据的 V3.3 十维度 SEO 健康诊断" if lang == "中文" else "V3.3 Ten-dimension SEO health diagnosis"}</div>', unsafe_allow_html=True)

    score_result = calculate_seo_score_v33(data)
    col_score, col_metrics = st.columns([1, 3])

    with col_score:
        st.markdown(f'<div class="score-ring" style="border-color: {score_result["grade_color"]};"><div class="score-number" style="color: {score_result["grade_color"]};">{score_result["final_score"]}</div><div class="score-grade" style="color: {score_result["grade_color"]};">{score_result["grade"]} · {score_result["grade_label"] if lang == "中文" else score_result["grade_label_en"]}</div></div>', unsafe_allow_html=True)
        st.caption(f"{'数据周期' if lang == '中文' else 'Period'}: {score_result['n_days']}{'天' if lang == '中文' else 'd'} | Scale: {score_result['scale_factor']:.3f}")

    with col_metrics:
        if data.get('daily_summary') is not None:
            df_sum = data['daily_summary']
            total_clicks = df_sum['clicks'].sum()
            total_impressions = df_sum['impressions'].sum()
            avg_ctr = total_clicks / max(total_impressions, 1)
            avg_position = df_sum['position'].mean()
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"总点击" if lang == "中文" else "Clicks"}</div><div class="metric-value">{total_clicks:,}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"总展示" if lang == "中文" else "Impressions"}</div><div class="metric-value">{total_impressions:,}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"平均CTR" if lang == "中文" else "Avg CTR"}</div><div class="metric-value">{avg_ctr:.2%}</div></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"平均排名" if lang == "中文" else "Avg Position"}</div><div class="metric-value">{avg_position:.1f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### {'📐 V3.3 十维度得分' if lang == '中文' else '📐 V3.3 Ten-Dimension Scores'}")
    indicator_names = {'ranking': ('关键词排名分布', 'Keyword Ranking', 19), 'diversity': ('关键词多样性', 'Keyword Diversity', 8), 'trend': ('流量趋势', 'Traffic Trend', 20), 'stability': ('流量稳定性', 'Traffic Stability', 8), 'ctr': ('CTR效率', 'CTR Efficiency', 14), 'page_activity': ('页面活跃度', 'Page Activity', 14), 'device': ('设备适配', 'Device', 2), 'region': ('地区覆盖', 'Region', 4), 'concentration': ('页面集中度', 'Concentration', 2), 'content': ('内容深度', 'Content', 9)}
    indicators = score_result['indicators']
    names = []
    scores_list = []
    colors = []
    for key in ['ranking', 'diversity', 'trend', 'stability', 'ctr', 'page_activity', 'device', 'region', 'concentration', 'content']:
        cn, en, w = indicator_names[key]
        name = f"{cn} ({w}%)" if lang == '中文' else f"{en} ({w}%)"
        names.append(name)
        s = indicators[key]
        scores_list.append(s)
        colors.append('#059669' if s >= 60 else '#d97706' if s >= 40 else '#dc2626')

    fig_bar = go.Figure(go.Bar(x=scores_list, y=names, orientation='h', marker_color=colors, text=[f"{s:.1f}" for s in scores_list], textposition='outside'))
    fig_bar.update_layout(height=450, xaxis=dict(range=[0, 105]), yaxis=dict(autorange='reversed'), margin=dict(l=200, r=60, t=20, b=40))
    fig_bar.add_vline(x=60, line_dash="dash", line_color="#9ca3af", annotation_text="Pass(60)")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.markdown(f"### {'🎯 雷达图' if lang == '中文' else '🎯 Radar'}")
    radar_labels = [indicator_names[k][0 if lang == '中文' else 1] for k in indicator_names]
    radar_values = [indicators[k] for k in indicator_names]
    fig_radar = go.Figure(data=go.Scatterpolar(r=radar_values + [radar_values[0]], theta=radar_labels + [radar_labels[0]], fill='toself', fillcolor='rgba(26,86,219,0.15)', line=dict(color='#1a56db', width=2.5)))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=500, margin=dict(l=80, r=80, t=40, b=40))
    st.plotly_chart(fig_radar, use_container_width=True)

# ============================================================
# 页面2：健康度评分详情
# ============================================================
elif page in ["🎯 SEO 健康度评分", "🎯 SEO Health Score"]:
    st.markdown(f'<div class="page-title">{"🎯 SEO 健康度评分详情 (V3.3)" if lang == "中文" else "🎯 SEO Health Score (V3.3)"}</div>', unsafe_allow_html=True)
    score_result = calculate_seo_score_v33(data)
    st.markdown(f'<div style="text-align:center; padding: 2rem; background: linear-gradient(135deg, #eff6ff, #dbeafe); border-radius: 16px; margin-bottom: 2rem;"><div style="font-size: 4rem; font-weight: 800; color: {score_result["grade_color"]};">{score_result["final_score"]}</div><div style="font-size: 1.5rem; color: {score_result["grade_color"]}; font-weight: 600;">{score_result["grade"]} · {score_result["grade_label"] if lang == "中文" else score_result["grade_label_en"]}</div><div style="font-size: 1rem; color: #6b7280; margin-top: 0.5rem;">V3.3 | AHP(CR=0.0182) | Piecewise Linear</div></div>', unsafe_allow_html=True)

    st.markdown(f"### {'📊 各指标得分明细' if lang == '中文' else '📊 Details'}")
    indicator_info = {'ranking': ('关键词排名分布', 19, '加权排名分/总词数'), 'diversity': ('关键词多样性', 8, '月度有效词数'), 'trend': ('流量趋势', 20, 'F1方向+F2保留'), 'stability': ('流量稳定性', 8, '去趋势CV'), 'ctr': ('CTR效率', 14, '实际/基准CTR'), 'page_activity': ('页面活跃度', 14, '有点击页面占比'), 'device': ('设备适配', 2, 'M/D CTR比'), 'region': ('地区覆盖', 4, '国家数+集中度'), 'concentration': ('页面集中度', 2, 'Gini系数'), 'content': ('内容深度', 9, '覆盖+新鲜度')}
    indicators = score_result['indicators']
    for key in ['ranking', 'diversity', 'trend', 'stability', 'ctr', 'page_activity', 'device', 'region', 'concentration', 'content']:
        cn, weight, formula = indicator_info[key]
        score = indicators[key]
        color = '#059669' if score >= 60 else '#d97706' if score >= 40 else '#dc2626'
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"**{cn}** <span style='color:#6b7280;font-size:0.85rem;'>({formula})</span>", unsafe_allow_html=True)
            st.progress(min(score / 100, 1.0))
        with col2:
            st.markdown(f"<span style='font-size:1.3rem;font-weight:700;color:{color};'>{score:.1f}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<span style='color:#6b7280;'>权重{weight}%</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### {'📋 等级对照表' if lang == '中文' else '📋 Grades'}")
    grade_df = pd.DataFrame([{'等级': g, '分数范围': f'{low}-{high - 1 if high != 101 else 100}', '描述': d} for low, high, g, d, _, _ in GRADE_SYSTEM])
    st.dataframe(grade_df, use_container_width=True, hide_index=True)


# ============================================================
# 页面3：搜索表现趋势
# ============================================================
elif page in ["📈 搜索表现趋势", "📈 Search Trends"]:
    st.markdown(f'<div class="page-title">{"📈 搜索表现趋势" if lang == "中文" else "📈 Search Trends"}</div>', unsafe_allow_html=True)

    if data.get('by_date') is not None:
        df = data['by_date'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date')
        col_s, col_e = st.columns(2)
        with col_s:
            start_date = st.date_input("开始" if lang == '中文' else "Start", value=df['data_date'].min(), key="ts")
        with col_e:
            end_date = st.date_input("结束" if lang == '中文' else "End", value=df['data_date'].max(), key="te")
        mask = (df['data_date'] >= pd.to_datetime(start_date)) & (df['data_date'] <= pd.to_datetime(end_date))
        df_f = df[mask].copy()

        if len(df_f) > 0:
            df_f['MA7'] = df_f['clicks'].rolling(7, min_periods=1).mean()
            df_f['MA30'] = df_f['clicks'].rolling(30, min_periods=1).mean()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
            fig.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['clicks'], mode='markers', name='Clicks', marker=dict(color='#93c5fd', size=4, opacity=0.6)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['MA7'], mode='lines', name='MA7', line=dict(color='#1a56db', width=2.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['MA30'], mode='lines', name='MA30', line=dict(color='#dc2626', width=2, dash='dash')), row=1, col=1)
            bar_colors = ['#22c55e' if c > 0 else '#ef4444' for c in df_f['clicks']]
            fig.add_trace(go.Bar(x=df_f['data_date'], y=df_f['impressions'], name='Impressions', marker_color=bar_colors, opacity=0.7), row=2, col=1)
            fig.update_layout(height=650, hovermode='x unified', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(l=60, r=20, t=60, b=40))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"### {'📉 CTR & 排名' if lang == '中文' else '📉 CTR & Position'}")
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            df_f['ctr_ma7'] = df_f['ctr'].rolling(7, min_periods=1).mean()
            df_f['pos_ma7'] = df_f['position'].rolling(7, min_periods=1).mean()
            fig2.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['ctr_ma7'] * 100, mode='lines', name='CTR%(MA7)', line=dict(color='#059669', width=2.5)), secondary_y=False)
            fig2.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['pos_ma7'], mode='lines', name='Pos(MA7)', line=dict(color='#d97706', width=2.5)), secondary_y=True)
            fig2.update_layout(height=400, legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
            fig2.update_yaxes(title_text="CTR(%)", secondary_y=False)
            fig2.update_yaxes(title_text="Position", autorange="reversed", secondary_y=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("无数据" if lang == '中文' else "No data")
    else:
        st.warning("未找到日期数据" if lang == '中文' else "No date data")

# ============================================================
# 页面4：关键词洞察
# ============================================================
elif page in ["🔍 关键词洞察", "🔍 Keyword Insights"]:
    st.markdown(f'<div class="page-title">{"🔍 关键词洞察" if lang == "中文" else "🔍 Keyword Insights"}</div>', unsafe_allow_html=True)

    if data.get('by_query') is not None:
        df = data['by_query'].copy()
        total_kw = df['query'].nunique()
        kw_with_clicks = df[df['clicks'] > 0]['query'].nunique()
        top_kw = df.nlargest(1, 'clicks')['query'].values[0] if len(df) > 0 else 'N/A'

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("总关键词" if lang == '中文' else "Total KW", f"{total_kw:,}")
        with k2:
            st.metric("有点击" if lang == '中文' else "With Clicks", f"{kw_with_clicks:,}")
        with k3:
            st.metric("Top KW", top_kw[:30])

        st.markdown("---")
        st.markdown(f"### {'🏆 Top 20' if lang == '中文' else '🏆 Top 20'}")
        top20 = df.nlargest(20, 'clicks')[['query', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        top20.index = top20.index + 1
        top20['ctr'] = top20['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
        top20['position'] = top20['position'].apply(lambda x: f"{x:.1f}")
        top20.columns = ['Keyword', 'Clicks', 'Impressions', 'CTR', 'Position']
        st.dataframe(top20, use_container_width=True, height=500)

        st.markdown(f"### {'💎 机会矩阵' if lang == '中文' else '💎 Opportunity'}")
        df_opp = df[df['impressions'] >= 10].copy()
        if len(df_opp) > 0:
            df_opp['ctr_val'] = df_opp['clicks'] / df_opp['impressions'].clip(lower=1)
            fig_opp = px.scatter(df_opp, x='impressions', y='ctr_val', size='clicks', color='position', hover_data=['query'], color_continuous_scale='RdYlGn_r')
            fig_opp.update_layout(height=500, margin=dict(l=60, r=20, t=40, b=60))
            st.plotly_chart(fig_opp, use_container_width=True)
    else:
        st.info("未找到 query 数据")


# ============================================================
# 页面5：页面效果分析
# ============================================================
elif page in ["📄 页面效果分析", "📄 Page Analysis"]:
    st.markdown(f'<div class="page-title">{"📄 页面效果分析" if lang == "中文" else "📄 Page Analysis"}</div>', unsafe_allow_html=True)

    if data.get('by_page') is not None:
        df = data['by_page'].copy()
        total_pages = df['page'].nunique()
        active_pages = df[df['clicks'] > 0]['page'].nunique()
        active_rate = active_pages / max(total_pages, 1)

        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("总页面" if lang == '中文' else "Pages", f"{total_pages}")
        with p2:
            st.metric("活跃" if lang == '中文' else "Active", f"{active_pages}")
        with p3:
            st.metric("活跃率" if lang == '中文' else "Rate", f"{active_rate:.1%}")

        st.markdown("---")
        st.markdown(f"### {'🏆 Top 15 页面' if lang == '中文' else '🏆 Top 15 Pages'}")
        top15 = df.nlargest(15, 'clicks')[['page', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        fig_pages = px.bar(top15, x='clicks', y='page', orientation='h', color='ctr', color_continuous_scale='Blues')
        fig_pages.update_layout(height=600, yaxis=dict(tickfont=dict(size=11)), margin=dict(l=300, r=20, t=20, b=40))
        st.plotly_chart(fig_pages, use_container_width=True)

        st.markdown(f"### {'💎 优化机会' if lang == '中文' else '💎 Opportunities'}")
        high_imp = df[(df['impressions'] >= 50) & (df['clicks'] <= 5)].nlargest(10, 'impressions')
        if len(high_imp) > 0:
            disp = high_imp[['page', 'impressions', 'clicks', 'ctr', 'position']].reset_index(drop=True)
            disp.index = disp.index + 1
            disp['ctr'] = disp['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
            disp.columns = ['Page', 'Impressions', 'Clicks', 'CTR', 'Position']
            st.dataframe(disp, use_container_width=True)
    else:
        st.info("未找到 page 数据")

# ============================================================
# 页面6：国家/地区分析
# ============================================================
elif page in ["🌍 国家/地区分析", "🌍 Country/Region"]:
    st.markdown(f'<div class="page-title">{"🌍 国家/地区分析" if lang == "中文" else "🌍 Country/Region"}</div>', unsafe_allow_html=True)

    if data.get('by_country') is not None:
        df = data['by_country'].copy()
        map_data = df.groupby('country').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()
        map_data['country_upper'] = map_data['country'].str.upper()
        map_data['clicks_log'] = np.log1p(map_data['clicks'])
        map_data['impressions_log'] = np.log1p(map_data['impressions'])

        map_metric = st.selectbox(
            "🗺️ 指标" if lang == '中文' else "🗺️ Metric",
            ['clicks', 'impressions', 'ctr', 'position'],
            format_func=lambda x: {'clicks': '点击', 'impressions': '展示', 'ctr': 'CTR', 'position': '排名'}[x] if lang == '中文' else x,
            key="map_sel"
        )
        if map_metric in ['clicks', 'impressions']:
            color_col = f'{map_metric}_log'
        else:
            color_col = map_metric
        cscale = 'Blues' if map_metric in ['clicks', 'impressions'] else ('Reds' if map_metric == 'ctr' else 'RdYlGn_r')

        fig_map = go.Figure(data=go.Choropleth(locations=map_data['country_upper'], z=map_data[color_col], locationmode='ISO-3', colorscale=cscale, marker_line_color='#fff', marker_line_width=0.5))
        fig_map.update_layout(geo=dict(showframe=False, projection_type='natural earth', showland=True, landcolor='#f8f9fa'), height=550, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown(f"### {'📊 Top 10' if lang == '中文' else '📊 Top 10'}")
        top10 = map_data.nlargest(10, 'clicks')[['country_upper', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        top10.index = top10.index + 1
        top10['ctr'] = top10['ctr'].apply(lambda x: f"{x:.2%}")
        top10['position'] = top10['position'].apply(lambda x: f"{x:.1f}")
        top10.columns = ['Country', 'Clicks', 'Impressions', 'CTR', 'Position']
        st.dataframe(top10, use_container_width=True)
    else:
        st.warning("未找到国家数据" if lang == '中文' else "No country data")

# ============================================================
# 页面7：设备分布
# ============================================================
elif page in ["📱 设备分布", "📱 Device Distribution"]:
    st.markdown(f'<div class="page-title">{"📱 设备分布" if lang == "中文" else "📱 Device Distribution"}</div>', unsafe_allow_html=True)

    if data.get('by_device') is not None:
        df = data['by_device'].copy()
        device_summary = df.groupby('device').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()

        col_pie, col_bar = st.columns(2)
        with col_pie:
            fig_pie = px.pie(device_summary, values='clicks', names='device', color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'], hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_bar:
            device_summary['ctr_pct'] = device_summary['clicks'] / device_summary['impressions'].clip(lower=1)
            fig_dctr = px.bar(device_summary, x='device', y='ctr_pct', color='device', color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'])
            fig_dctr.update_layout(height=400, yaxis=dict(tickformat='.2%'), showlegend=False)
            st.plotly_chart(fig_dctr, use_container_width=True)

        st.markdown(f"### {'📈 月度趋势' if lang == '中文' else '📈 Monthly'}")
        df['data_date'] = pd.to_datetime(df['data_date'])
        df['month'] = df['data_date'].dt.to_period('M').astype(str)
        monthly_device = df.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
        fig_trend = px.line(monthly_device, x='month', y='clicks', color='device', markers=True, color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'])
        fig_trend.update_layout(height=400)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("未找到设备数据" if lang == '中文' else "No device data")

# ============================================================
# 页面8：流量异常检测
# ============================================================
elif page in ["🚨 流量异常检测", "🚨 Anomaly Detection"]:
    st.markdown(f'<div class="page-title">{"🚨 流量异常检测" if lang == "中文" else "🚨 Anomaly Detection"}</div>', unsafe_allow_html=True)

    if data.get('by_date') is not None:
        df = data['by_date'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date').reset_index(drop=True)

        window = st.slider("窗口(天)" if lang == '中文' else "Window(days)", 7, 60, 28, key="aw")
        threshold = st.slider("阈值(Z)" if lang == '中文' else "Threshold(Z)", 1.5, 4.0, 2.5, 0.5, key="at")

        df['rolling_mean'] = df['clicks'].rolling(window, min_periods=7).mean()
        df['rolling_std'] = df['clicks'].rolling(window, min_periods=7).std()
        df['z_score'] = (df['clicks'] - df['rolling_mean']) / df['rolling_std'].clip(lower=0.1)
        df['is_anomaly'] = df['z_score'].abs() > threshold
        df['anomaly_type'] = 'normal'
        df.loc[df['z_score'] > threshold, 'anomaly_type'] = 'spike'
        df.loc[df['z_score'] < -threshold, 'anomaly_type'] = 'drop'

        anomalies = df[df['is_anomaly']]
        spikes = len(anomalies[anomalies['anomaly_type'] == 'spike'])
        drops = len(anomalies[anomalies['anomaly_type'] == 'drop'])

        a1, a2, a3 = st.columns(3)
        with a1:
            st.metric("异常天数" if lang == '中文' else "Anomalies", f"{len(anomalies)}")
        with a2:
            st.metric("🔺 飙升" if lang == '中文' else "🔺 Spikes", f"{spikes}")
        with a3:
            st.metric("🔻 骤降" if lang == '中文' else "🔻 Drops", f"{drops}")

        st.markdown("---")
        fig_a = go.Figure()
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=df['clicks'], mode='lines', name='Clicks', line=dict(color='#93c5fd', width=1.5)))
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=df['rolling_mean'], mode='lines', name=f'MA{window}', line=dict(color='#1a56db', width=2)))
        upper = df['rolling_mean'] + threshold * df['rolling_std']
        lower = df['rolling_mean'] - threshold * df['rolling_std']
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=upper, mode='lines', name='Upper', line=dict(color='#d1d5db', width=1, dash='dot')))
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=lower, mode='lines', name='Lower', line=dict(color='#d1d5db', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(209,213,219,0.1)'))
        spike_df = df[df['anomaly_type'] == 'spike']
        drop_df = df[df['anomaly_type'] == 'drop']
        
        if len(spike_df) > 0:
            fig_a.add_trace(go.Scatter(x=spike_df['data_date'], y=spike_df['clicks'], mode='markers', name='Spike', marker=dict(color='#dc2626', size=10, symbol='triangle-up')))
        if len(drop_df) > 0:
            fig_a.add_trace(go.Scatter(x=drop_df['data_date'], y=drop_df['clicks'], mode='markers', name='Drop', marker=dict(color='#059669', size=10, symbol='triangle-down')))
        fig_a.update_layout(height=500, hovermode='x unified', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(l=60, r=20, t=40, b=40))
        st.plotly_chart(fig_a, use_container_width=True)

        if len(anomalies) > 0:
            st.markdown(f"### {'📋 异常列表' if lang == '中文' else '📋 Events'}")
            disp_a = anomalies[['data_date', 'clicks', 'rolling_mean', 'z_score', 'anomaly_type']].copy()
            disp_a['data_date'] = disp_a['data_date'].dt.strftime('%Y-%m-%d')
            disp_a['rolling_mean'] = disp_a['rolling_mean'].apply(lambda x: f"{x:.1f}")
            disp_a['z_score'] = disp_a['z_score'].apply(lambda x: f"{x:.2f}")
            disp_a.columns = ['Date', 'Clicks', 'Expected', 'Z-Score', 'Type']
            st.dataframe(disp_a.sort_values('Date', ascending=False).head(30), use_container_width=True, hide_index=True)
    else:
        st.warning("未找到日期数据" if lang == '中文' else "No date data")

# ============================================================
# 页面9：优化建议
# ============================================================
elif page in ["🚀 优化建议", "🚀 Recommendations"]:
    st.markdown(f'<div class="page-title">{"🚀 SEO 优化建议 (V3.3)" if lang == "中文" else "🚀 Recommendations (V3.3)"}</div>', unsafe_allow_html=True)

    score_result = calculate_seo_score_v33(data)
    diagnosis = generate_diagnosis(score_result, lang)

    urgent_count = sum(1 for d in diagnosis if d['level'] == 'urgent')
    attention_count = sum(1 for d in diagnosis if d['level'] == 'attention')
    healthy_count = 10 - urgent_count - attention_count

    col_u, col_a, col_o = st.columns(3)
    with col_u:
        st.metric("🔴 紧急" if lang == '中文' else "🔴 Urgent", f"{urgent_count}")
    with col_a:
        st.metric("🟡 关注" if lang == '中文' else "🟡 Attention", f"{attention_count}")
    with col_o:
        st.metric("🟢 健康" if lang == '中文' else "🟢 Healthy", f"{healthy_count}")

    st.markdown("---")

    if diagnosis:
        st.markdown(f"### {'📋 行动清单' if lang == '中文' else '📋 Actions'}")
        ind_map = {'ranking': '关键词排名' if lang == '中文' else 'Ranking', 'diversity': '关键词多样性' if lang == '中文' else 'Diversity', 'trend': '流量趋势' if lang == '中文' else 'Trend', 'stability': '流量稳定性' if lang == '中文' else 'Stability', 'ctr': 'CTR效率' if lang == '中文' else 'CTR', 'page_activity': '页面活跃度' if lang == '中文' else 'Page Activity', 'device': '设备适配' if lang == '中文' else 'Device', 'region': '地区覆盖' if lang == '中文' else 'Region', 'concentration': '页面集中度' if lang == '中文' else 'Concentration', 'content': '内容深度' if lang == '中文' else 'Content'}

        for rec in diagnosis:
            if rec['level'] == 'urgent':
                priority = 'P0'
                color = '#dc2626'
                bg = '#fef2f2'
            else:
                priority = 'P1'
                color = '#d97706'
                bg = '#fffbeb'
            st.markdown(f"""<div style="border-left: 4px solid {color}; padding: 1rem 1.5rem; margin: 0.8rem 0; background: {bg}; border-radius: 0 8px 8px 0;"><div style="display: flex; justify-content: space-between;"><span style="font-weight: 700; color: {color};">{priority} · {ind_map.get(rec['key'], rec['key'])}</span><span style="color: #6b7280;">{rec['score']:.1f}/100 | {rec['weight']}%</span></div><div style="margin-top: 0.5rem; font-weight: 600;">⚠️ {rec['issue']}</div><div style="margin-top: 0.3rem; color: #4b5563;">💡 {rec['action']}</div></div>""", unsafe_allow_html=True)
    else:
        st.success("🎉 所有指标健康！" if lang == '中文' else "🎉 All healthy!")

    st.markdown("---")
    st.markdown(f"### {'📈 提升路径' if lang == '中文' else '📈 Improvement Path'}")

    indicators = score_result['indicators']
    improvements = []
    for key, weight in WEIGHTS.items():
        current = indicators[key]
        if current < 60:
            gain = (60 - current) * weight / 100
            improvements.append({'name': key, 'current': current, 'gain': gain, 'weight': weight})
    improvements.sort(key=lambda x: x['gain'], reverse=True)

    total_potential = sum(i['gain'] for i in improvements)
    current_score = score_result['final_score']
    st.markdown(f"""<div style="background: #eff6ff; padding: 1.5rem; border-radius: 12px;"><div style="font-size: 1.1rem; font-weight: 600; color: #1a56db;">{"当前" if lang == "中文" else "Now"}: {current_score} → {"目标" if lang == "中文" else "Target"}: {current_score + total_potential:.1f} (+{total_potential:.1f})</div></div>""", unsafe_allow_html=True)

    ind_map2 = {'ranking': '关键词排名' if lang == '中文' else 'Ranking', 'diversity': '多样性' if lang == '中文' else 'Diversity', 'trend': '流量趋势' if lang == '中文' else 'Trend', 'stability': '稳定性' if lang == '中文' else 'Stability', 'ctr': 'CTR' if lang == '中文' else 'CTR', 'page_activity': '页面活跃' if lang == '中文' else 'Activity', 'device': '设备' if lang == '中文' else 'Device', 'region': '地区' if lang == '中文' else 'Region', 'concentration': '集中度' if lang == '中文' else 'Concentration', 'content': '内容' if lang == '中文' else 'Content'}

    if improvements:
        fig_imp = go.Figure(go.Bar(
            x=[i['gain'] for i in improvements],
            y=[f"{ind_map2.get(i['name'], i['name'])} ({i['current']:.0f}→60)" for i in improvements],
            orientation='h', marker_color='#1a56db',
            text=[f"+{i['gain']:.1f}" for i in improvements], textposition='outside'
        ))
        fig_imp.update_layout(height=max(300, len(improvements) * 50), xaxis=dict(title='Gain'), yaxis=dict(autorange='reversed'), margin=dict(l=200, r=60, t=20, b=40))
        st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown("---")
    st.info("💡 外链权威维度已预留接口，待接入 Ahrefs/Moz API 后可扩展。" if lang == '中文' else "💡 Backlink Authority reserved for future API integration.")

