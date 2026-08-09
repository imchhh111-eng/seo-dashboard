
"""
B2B SEO Health Assessment Engine V3.3
独立评分引擎模块 — 供 app.py 调用
"""
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


def piecewise_linear(value: float, breakpoints: list, scores: list) -> float:
    """分段线性插值评分函数 — 消除阶梯跳变"""
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


def calculate_gini(values: np.ndarray) -> float:
    """计算Gini系数"""
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    if n == 0 or np.sum(sorted_vals) == 0:
        return 0
    idx = np.arange(1, n + 1)
    return (2 * np.sum(idx * sorted_vals) - (n + 1) * np.sum(sorted_vals)) / (n * np.sum(sorted_vals))


# V3.3 阈值配置
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

# AHP权重 (CR=0.0182)
WEIGHTS = {
    'ranking': 19, 'diversity': 8, 'trend': 20, 'stability': 8,
    'ctr': 14, 'page_activity': 14, 'device': 2, 'region': 4,
    'concentration': 2, 'content': 9,
}

# CTR行业基准 (FirstPageSage 2026)
CTR_BENCHMARKS = {
    (0, 1): 0.398, (1, 2): 0.187, (2, 3): 0.102,
    (3, 5): 0.0625, (5, 10): 0.0276,
    (10, 20): 0.0098, (20, 50): 0.003, (50, 100): 0.0005,
}

# 等级系统
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


def calculate_seo_score_v33(data: dict) -> dict:
    """V3.3 SEO健康度评估 — 10维度模型"""
    results = {}
    details = {}

    by_date = data.get('by_date')
    by_query = data.get('by_query')
    by_page = data.get('by_page')
    by_device = data.get('by_device')
    by_country = data.get('by_country')
    query_page = data.get('query_page')

    # 转换日期
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

    # 规模系数
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

    # 指标7: 设备适配 (2%) × 规模系数
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

    # 指标8: 地区覆盖 (4%) × 规模系数
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

    # 指标9: 页面集中度 (2%) × 规模系数
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
        details['concentration'] = {'gini': gini}
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

    # 等级判定
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


def generate_diagnosis(score_result: dict, lang: str = '中文') -> list:
    """V3.3 诊断建议引擎"""
    indicators = score_result['indicators']
    diagnosis = []

    RULES = {
        'ranking': {
            'issue_cn': '关键词排名极差，几乎无Top10词',
            'issue_en': 'Keyword rankings critically low',
            'action_cn': '聚焦长尾关键词，优化11-20位关键词的页面内容深度和内链',
            'action_en': 'Focus on long-tail keywords, optimize content for keywords ranked 11-20',
        },
        'diversity': {
            'issue_cn': '有效关键词数量不足，搜索覆盖面窄',
            'issue_en': 'Insufficient effective keywords',
            'action_cn': '扩展内容矩阵，针对B2B买家旅程各阶段创建内容',
            'action_en': 'Expand content matrix for each B2B buyer journey stage',
        },
        'trend': {
            'issue_cn': '流量持续下降，站点可能面临严重问题',
            'issue_en': 'Traffic continuously declining',
            'action_cn': '排查索引问题、算法惩罚、竞争对手抢占；制定内容恢复计划',
            'action_en': 'Investigate indexing issues, algorithm penalties, competitor displacement',
        },
        'stability': {
            'issue_cn': '流量波动剧烈，缺乏稳定的自然搜索基础',
            'issue_en': 'Traffic highly volatile',
            'action_cn': '建立常青内容体系，减少对单一关键词/页面的依赖',
            'action_en': 'Build evergreen content, reduce single-keyword dependency',
        },
        'ctr': {
            'issue_cn': 'CTR效率低于行业基准，标题和描述吸引力不足',
            'issue_en': 'CTR below industry benchmark',
            'action_cn': '优化Title/Meta Description，加入数字、年份、行动号召词',
            'action_en': 'Optimize Title/Meta Description with numbers, dates, CTAs',
        },
        'page_activity': {
            'issue_cn': '大量页面零点击，内容资产利用率低',
            'issue_en': 'Many pages with zero clicks',
            'action_cn': '审计零流量页面：更新、合并或删除；集中资源到高潜力页面',
            'action_en': 'Audit zero-traffic pages: update, consolidate, or remove',
        },
        'content': {
            'issue_cn': '内容深度不足且更新频率低',
            'issue_en': 'Insufficient content depth and low update frequency',
            'action_cn': '为核心页面扩展关键词覆盖(每页≥5个相关词)；建立定期更新机制',
            'action_en': 'Expand keyword coverage per page; establish regular update schedule',
        },
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
            diagnosis.append({
                'key': key, 'score': score, 'level': level,
                'weight': WEIGHTS.get(key, 0),
                'issue': rule['issue_cn'] if lang == '中文' else rule['issue_en'],
                'action': rule['action_cn'] if lang == '中文' else rule['action_en'],
            })

    return diagnosis

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
from seo_engine_v33 import (
    calculate_seo_score_v33, generate_diagnosis,
    WEIGHTS, GRADE_SYSTEM, CTR_BENCHMARKS, THRESHOLDS
)

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
# 侧边栏导航
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 SEO Health Intelligence</div>', unsafe_allow_html=True)
    lang = st.radio("🌐 Language", ['中文', 'English'], horizontal=True, key="lang_switch")
    st.markdown("---")
    nav_items = {
        '中文': ["📊 总览仪表盘", "🎯 SEO 健康度评分", "📈 搜索表现趋势", "🔍 关键词洞察", "📄 页面效果分析", "🌍 国家/地区分析", "📱 设备分布", "🚨 流量异常检测", "🚀 优化建议"],
        'English': ["📊 Overview Dashboard", "🎯 SEO Health Score", "📈 Search Trends", "🔍 Keyword Insights", "📄 Page Analysis", "🌍 Country/Region", "📱 Device Distribution", "🚨 Anomaly Detection", "🚀 Recommendations"]
    }
    page = st.radio("导航菜单" if lang == '中文' else "Navigation", nav_items[lang], key="nav_menu")
    st.markdown("---")
    if data.get('by_date') is not None:
        date_range = data['by_date']['data_date']
        st.caption(f"📅 {'数据范围' if lang == '中文' else 'Data Range'}: {date_range.min()} → {date_range.max()}")
    st.markdown("---")
    st.caption("B2B SEO Health Intelligence v3.3 | Based on GSC Data")

# ============================================================
# 页面1：总览仪表盘
# ============================================================
if page in ["📊 总览仪表盘", "📊 Overview Dashboard"]:
    st.markdown(f'<div class="page-title">{"📊 B2B SEO 总览仪表盘" if lang == "中文" else "📊 B2B SEO Overview Dashboard"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于 Google Search Console 数据的 V3.3 十维度 SEO 健康诊断" if lang == "中文" else "V3.3 Ten-dimension SEO health diagnosis based on GSC data"}</div>', unsafe_allow_html=True)

    score_result = calculate_seo_score_v33(data)

    col_score, col_metrics = st.columns([1, 3])
    with col_score:
        st.markdown(f"""
        <div class="score-ring" style="border-color: {score_result['grade_color']};">
            <div class="score-number" style="color: {score_result['grade_color']};">{score_result['final_score']}</div>
            <div class="score-grade" style="color: {score_result['grade_color']};">{score_result['grade']} · {score_result['grade_label'] if lang == '中文' else score_result['grade_label_en']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"{'数据周期' if lang == '中文' else 'Period'}: {score_result['n_days']}{'天' if lang == '中文' else 'd'} | {'规模系数' if lang == '中文' else 'Scale'}: {score_result['scale_factor']:.3f}")

    with col_metrics:
        if data.get('daily_summary') is not None:
            df = data['daily_summary']
            total_clicks = df['clicks'].sum()
            total_impressions = df['impressions'].sum()
            avg_ctr = total_clicks / max(total_impressions, 1)
            avg_position = df['position'].mean()
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"总点击" if lang == "中文" else "Total Clicks"}</div><div class="metric-value">{total_clicks:,}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"总展示" if lang == "中文" else "Total Impressions"}</div><div class="metric-value">{total_impressions:,}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"平均CTR" if lang == "中文" else "Avg CTR"}</div><div class="metric-value">{avg_ctr:.2%}</div></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"平均排名" if lang == "中文" else "Avg Position"}</div><div class="metric-value">{avg_position:.1f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 十维度得分条形图
    st.markdown(f"### {'📐 V3.3 十维度得分' if lang == '中文' else '📐 V3.3 Ten-Dimension Scores'}")
    indicator_names = {
        'ranking': ('关键词排名分布', 'Keyword Ranking', 19),
        'diversity': ('关键词多样性', 'Keyword Diversity', 8),
        'trend': ('流量趋势', 'Traffic Trend', 20),
        'stability': ('流量稳定性', 'Traffic Stability', 8),
        'ctr': ('CTR效率', 'CTR Efficiency', 14),
        'page_activity': ('页面活跃度', 'Page Activity', 14),
        'device': ('设备适配', 'Device Adapt', 2),
        'region': ('地区覆盖', 'Region Coverage', 4),
        'concentration': ('页面集中度', 'Page Concentration', 2),
        'content': ('内容深度与更新', 'Content Depth', 9),
    }
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

    fig_bar = go.Figure(go.Bar(x=scores_list, y=names, orientation='h', marker_color=colors, text=[f"{s:.1f}" for s in scores_list], textposition='outside', textfont=dict(size=13)))
    fig_bar.update_layout(height=450, xaxis=dict(range=[0, 105], title='Score', tickfont=dict(size=13)), yaxis=dict(tickfont=dict(size=13), autorange='reversed'), margin=dict(l=200, r=60, t=20, b=40), font=dict(size=14))
    fig_bar.add_vline(x=60, line_dash="dash", line_color="#9ca3af", annotation_text="及格线(60)" if lang == '中文' else "Pass(60)")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # 雷达图
    st.markdown(f"### {'🎯 综合能力雷达图' if lang == '中文' else '🎯 Capability Radar'}")
    radar_labels = [indicator_names[k][0 if lang == '中文' else 1] for k in indicator_names]
    radar_values = [indicators[k] for k in indicator_names]
    fig_radar = go.Figure(data=go.Scatterpolar(r=radar_values + [radar_values[0]], theta=radar_labels + [radar_labels[0]], fill='toself', fillcolor='rgba(26, 86, 219, 0.15)', line=dict(color='#1a56db', width=2.5), marker=dict(size=6, color='#1a56db')))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=12)), angularaxis=dict(tickfont=dict(size=12))), height=500, margin=dict(l=80, r=80, t=40, b=40))
    st.plotly_chart(fig_radar, use_container_width=True)


# ============================================================
# 页面2：SEO 健康度评分详情
# ============================================================
elif page in ["🎯 SEO 健康度评分", "🎯 SEO Health Score"]:
    st.markdown(f'<div class="page-title">{"🎯 SEO 健康度评分详情 (V3.3)" if lang == "中文" else "🎯 SEO Health Score Details (V3.3)"}</div>', unsafe_allow_html=True)
    score_result = calculate_seo_score_v33(data)

    st.markdown(f"""
    <div style="text-align:center; padding: 2rem; background: linear-gradient(135deg, #eff6ff, #dbeafe); border-radius: 16px; margin-bottom: 2rem;">
        <div style="font-size: 4rem; font-weight: 800; color: {score_result['grade_color']};">{score_result['final_score']}</div>
        <div style="font-size: 1.5rem; color: {score_result['grade_color']}; font-weight: 600;">{score_result['grade']} · {score_result['grade_label'] if lang == '中文' else score_result['grade_label_en']}</div>
        <div style="font-size: 1rem; color: #6b7280; margin-top: 0.5rem;">{"V3.3 十维度评估模型 | AHP权重(CR=0.0182) | 分段线性插值" if lang == "中文" else "V3.3 Ten-dimension | AHP weights (CR=0.0182) | Piecewise linear"}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### {'📊 各指标得分明细' if lang == '中文' else '📊 Indicator Score Details'}")
    indicator_info = {
        'ranking': ('关键词排名分布', 'Keyword Ranking', 19, '加权排名分/总词数'),
        'diversity': ('关键词多样性', 'Keyword Diversity', 8, '月度有效关键词数(曝光≥10)'),
        'trend': ('流量趋势-复合F', 'Traffic Trend', 20, 'F1方向性 + F2保留率'),
        'stability': ('流量稳定性', 'Traffic Stability', 8, '去趋势后28天滚动CV'),
        'ctr': ('CTR效率', 'CTR Efficiency', 14, '实际CTR/行业基准CTR'),
        'page_activity': ('页面活跃度', 'Page Activity', 14, '有点击页面占比'),
        'device': ('设备适配', 'Device', 2, 'Mobile/Desktop CTR比'),
        'region': ('地区覆盖', 'Region', 4, '国家数+集中度'),
        'concentration': ('页面集中度', 'Concentration', 2, 'Gini系数(近6月)'),
        'content': ('内容深度与更新', 'Content', 9, '覆盖深度+新鲜度'),
    }
    indicators = score_result['indicators']
    for key in ['ranking', 'diversity', 'trend', 'stability', 'ctr', 'page_activity', 'device', 'region', 'concentration', 'content']:
        cn, en, weight, formula = indicator_info[key]
        name = cn if lang == '中文' else en
        score = indicators[key]
        color = '#059669' if score >= 60 else '#d97706' if score >= 40 else '#dc2626'
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"**{name}** <span style='color:#6b7280;font-size:0.85rem;'>({formula})</span>", unsafe_allow_html=True)
            st.progress(min(score / 100, 1.0))
        with col2:
            st.markdown(f"<span style='font-size:1.3rem;font-weight:700;color:{color};'>{score:.1f}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<span style='color:#6b7280;'>权重{weight}%</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### {'📋 等级对照表' if lang == '中文' else '📋 Grade Reference'}")
    grade_df = pd.DataFrame([{'等级': g, '分数范围': f'{low}-{high - 1 if high != 101 else 100}', '描述': desc_cn} for low, high, g, desc_cn, _, _ in GRADE_SYSTEM])
    st.dataframe(grade_df, use_container_width=True, hide_index=True)


# ============================================================
# 页面3：搜索表现趋势
# ============================================================
elif page in ["📈 搜索表现趋势", "📈 Search Trends"]:
    st.markdown(f'<div class="page-title">{"📈 搜索表现趋势" if lang == "中文" else "📈 Search Performance Trends"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"股市风格趋势图 — 点击量 + 移动平均线 + 展示量柱状图" if lang == "中文" else "Stock-style chart — Clicks + MA + Impressions Volume"}</div>', unsafe_allow_html=True)

    if data.get('by_date') is not None:
        df = data['by_date'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date')
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input("开始日期" if lang == '中文' else "Start Date", value=df['data_date'].min(), key="trend_start")
        with col_end:
            end_date = st.date_input("结束日期" if lang == '中文' else "End Date", value=df['data_date'].max(), key="trend_end")
        mask = (df['data_date'] >= pd.to_datetime(start_date)) & (df['data_date'] <= pd.to_datetime(end_date))
        df_filtered = df[mask].copy()

        if len(df_filtered) > 0:
            df_filtered['MA7'] = df_filtered['clicks'].rolling(window=7, min_periods=1).mean()
            df_filtered['MA30'] = df_filtered['clicks'].rolling(window=30, min_periods=1).mean()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3],
                subplot_titles=('点击数 & 移动平均线' if lang == '中文' else 'Clicks & Moving Averages', '展示量' if lang == '中文' else 'Impressions'))
            fig.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['clicks'], mode='markers', name='每日点击' if lang == '中文' else 'Daily Clicks', marker=dict(color='#93c5fd', size=4, opacity=0.6)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['MA7'], mode='lines', name='MA7', line=dict(color='#1a56db', width=2.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['MA30'], mode='lines', name='MA30', line=dict(color='#dc2626', width=2, dash='dash')), row=1, col=1)
            colors = ['#22c55e' if row['clicks'] > 0 else '#ef4444' for _, row in df_filtered.iterrows()]
            fig.add_trace(go.Bar(x=df_filtered['data_date'], y=df_filtered['impressions'], name='展示量' if lang == '中文' else 'Impressions', marker_color=colors, opacity=0.7), row=2, col=1)
            fig.update_layout(height=650, font=dict(size=14), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(l=60, r=20, t=80, b=40), hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"### {'📉 CTR & 排名趋势' if lang == '中文' else '📉 CTR & Position Trend'}")
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            df_filtered['ctr_ma7'] = df_filtered['ctr'].rolling(window=7, min_periods=1).mean()
            df_filtered['pos_ma7'] = df_filtered['position'].rolling(window=7, min_periods=1).mean()
            fig2.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['ctr_ma7'] * 100, mode='lines', name='CTR (MA7)', line=dict(color='#059669', width=2.5)), secondary_y=False)
            fig2.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['pos_ma7'], mode='lines', name='Position (MA7)', line=dict(color='#d97706', width=2.5)), secondary_y=True)
            fig2.update_layout(height=400, font=dict(size=14), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
            fig2.update_yaxes(title_text="CTR (%)", secondary_y=False)
            fig2.update_yaxes(title_text="Position", autorange="reversed", secondary_y=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("所选日期范围内无数据" if lang == '中文' else "No data in selected range")
    else:
        st.warning("未找到日期维度数据" if lang == '中文' else "Date data not found")


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
            st.metric("总关键词数" if lang == '中文' else "Total Keywords", f"{total_kw:,}")
        with k2:
            st.metric("有点击关键词" if lang == '中文' else "With Clicks", f"{kw_with_clicks:,}")
        with k3:
            st.metric("最佳关键词" if lang == '中文' else "Top Keyword", top_kw[:30])

        st.markdown("---")
        st.markdown(f"### {'🏆 Top 20 关键词' if lang == '中文' else '🏆 Top 20 Keywords'}")
        top20 = df.nlargest(20, 'clicks')[['query', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        top20.index = top20.index + 1
        top20['ctr'] = top20['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
        top20['position'] = top20['position'].apply(lambda x: f"{x:.1f}")
        top20.columns = ['Keyword', 'Clicks', 'Impressions', 'CTR', 'Position']
        st.dataframe(top20, use_container_width=True, height=500)

        st.markdown(f"### {'💎 关键词机会矩阵' if lang == '中文' else '💎 Keyword Opportunity Matrix'}")
        st.caption("高展示 + 低CTR = 优化机会" if lang == '中文' else "High impressions + Low CTR = Opportunity")
        df_opp = df[(df['impressions'] >= 10)].copy()
        if len(df_opp) > 0:
            df_opp['ctr_val'] = df_opp['clicks'] / df_opp['impressions'].clip(lower=1)
            fig_opp = px.scatter(df_opp, x='impressions', y='ctr_val', size='clicks', color='position', hover_data=['query'], color_continuous_scale='RdYlGn_r', labels={'impressions': '展示数' if lang == '中文' else 'Impressions', 'ctr_val': 'CTR', 'position': '排名' if lang == '中文' else 'Position'})
            fig_opp.update_layout(height=500, font=dict(size=14), margin=dict(l=60, r=20, t=40, b=60))
            st.plotly_chart(fig_opp, use_container_width=True)
    else:
        st.info("请确保 data/ 文件夹中包含 cleaned_by_query.csv")


# ============================================================
# 页面5：页面效果分析
# ============================================================
elif page in ["📄 页面效果分析", "📄 Page Analysis"]:
    st.markdown(f'<div class="page-title">{"📄 页面效果分析" if lang == "中文" else "📄 Page Performance Analysis"}</div>', unsafe_allow_html=True)

    if data.get('by_page') is not None:
        df = data['by_page'].copy()
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
        st.markdown(f"### {'🏆 Top 15 页面' if lang == '中文' else '🏆 Top 15 Pages'}")
        top15 = df.nlargest(15, 'clicks')[['page', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        fig_pages = px.bar(top15, x='clicks', y='page', orientation='h', color='ctr', color_continuous_scale='Blues', labels={'clicks': 'Clicks', 'page': 'Page', 'ctr': 'CTR'})
        fig_pages.update_layout(height=600, font=dict(size=13), yaxis=dict(tickfont=dict(size=11)), margin=dict(l=300, r=20, t=20, b=40))
        st.plotly_chart(fig_pages, use_container_width=True)

        st.markdown(f"### {'💎 页面优化机会' if lang == '中文' else '💎 Page Optimization Opportunities'}")
        high_imp_low_ctr = df[(df['impressions'] >= 50) & (df['clicks'] <= 5)].nlargest(10, 'impressions')
        if len(high_imp_low_ctr) > 0:
            st.caption("高展示但低点击的页面 — 优化 Title/Description 可快速提升流量" if lang == '中文' else "High impression but low click pages")
            display_df = high_imp_low_ctr[['page', 'impressions', 'clicks', 'ctr', 'position']].reset_index(drop=True)
            display_df.index = display_df.index + 1
            display_df['ctr'] = display_df['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
            display_df.columns = ['Page URL', 'Impressions', 'Clicks', 'CTR', 'Position']
            st.dataframe(display_df, use_container_width=True)
    else:
        st.info("请确保 data/ 文件夹中包含 cleaned_by_page.csv")


# ============================================================
# 页面6：国家/地区分析
# ============================================================
elif page in ["🌍 国家/地区分析", "🌍 Country/Region"]:
    st.markdown(f'<div class="page-title">{"🌍 国家/地区分析" if lang == "中文" else "🌍 Country/Region Analysis"}</div>', unsafe_allow_html=True)

    if data.get('by_country') is not None:
        df = data['by_country'].copy()
        map_data = df.groupby('country').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()
        map_data['country_upper'] = map_data['country'].str.upper()
        map_data['clicks_log'] = np.log1p(map_data['clicks'])

        map_metric = st.selectbox("🗺️ 地图展示指标" if lang == '中文' else "🗺️ Map Metric", ['clicks', 'impressions', 'ctr', 'position'],
            format_func=lambda x: {'clicks': '点击数', 'impressions': '展示数', 'ctr': 'CTR', 'position': '排名'}[x] if lang == '中文' else x, key="map_metric_sel")

        color_col = f'{map_metric}_log' if map_metric in ['clicks', 'impressions'] else map_metric
        if map_metric in ['clicks', 'impressions']:
            map_data['impressions_log'] = np.log1p(map_data['impressions'])

        fig_map = go.Figure(data=go.Choropleth(locations=map_data['country_upper'], z=map_data[color_col], locationmode='ISO-3', colorscale='Blues', marker_line_color='#ffffff', marker_line_width=0.5))
        fig_map.update_layout(geo=dict(showframe=False, projection_type='natural earth', showland=True, landcolor='#f8f9fa'), height=550, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown(f"### {'📊 Top 10 国家/地区' if lang == '中文' else '📊 Top 10 Countries'}")
        top10 = map_data.nlargest(10, 'clicks')[['country_upper', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        top10.index = top10.index + 1
        top10['ctr'] = top10['ctr'].apply(lambda x: f"{x:.2%}")
        top10['position'] = top10['position'].apply(lambda x: f"{x:.1f}")
        top10.columns = ['Country', 'Clicks', 'Impressions', 'CTR', 'Avg Position']
        st.dataframe(top10, use_container_width=True)
    else:
        st.warning("未找到国家维度数据" if lang == '中文' else "Country data not found")


# ============================================================
# 页面7：设备分布
# ============================================================
elif page in ["📱 设备分布", "📱 Device Distribution"]:
    st.markdown(f'<div class="page-title">{"📱 设备分布分析" if lang == "中文" else "📱 Device Distribution Analysis"}</div>', unsafe_allow_html=True)

    if data.get('by_device') is not None:
        df = data['by_device'].copy()
        device_summary = df.groupby('device').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()

        col_pie, col_bar = st.columns(2)
        with col_pie:
            st.markdown(f"#### {'点击数占比' if lang == '中文' else 'Clicks Distribution'}")
            fig_pie = px.pie(device_summary, values='clicks', names='device', color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'], hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
            fig_pie.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_bar:
            st.markdown(f"#### {'各设备 CTR 对比' if lang == '中文' else 'CTR by Device'}")
            device_summary['ctr_pct'] = device_summary['clicks'] / device_summary['impressions'].clip(lower=1)
            fig_ctr = px.bar(device_summary, x='device', y='ctr_pct', color='device', color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'])
            fig_ctr.update_layout(height=400, yaxis=dict(tickformat='.2%'), showlegend=False)
            st.plotly_chart(fig_ctr, use_container_width=True)

        st.markdown(f"### {'📈 设备月度趋势' if lang == '中文' else '📈 Monthly Device Trends'}")
        df['data_date'] = pd.to_datetime(df['data_date'])
        df['month'] = df['data_date'].dt.to_period('M').astype(str)
        monthly_device = df.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
        fig_trend = px.line(monthly_device, x='month', y='clicks', color='device', markers=True, color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'])
        fig_trend.update_layout(height=400, font=dict(size=14))
        st.plotly_chart(fig_trend, use_

