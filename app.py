
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
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
# V3.3 SEO 健康度评估核心引擎
# ============================================================

def piecewise_linear(value: float, breakpoints: list, scores: list) -> float:
    """分段线性插值评分函数 — 消除阶梯跳变"""
    assert len(breakpoints) == len(scores), f"长度不一致: bp={len(breakpoints)}, sc={len(scores)}"
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
    """计算Gini系数 — 衡量流量集中度"""
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    if n == 0 or np.sum(sorted_vals) == 0:
        return 0
    idx = np.arange(1, n + 1)
    return (2 * np.sum(idx * sorted_vals) - (n + 1) * np.sum(sorted_vals)) / (n * np.sum(sorted_vals))


# V3.3 阈值配置（数据驱动 + 行业基准校验）
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

# V3.3 权重（AHP验证, CR=0.0182 < 0.10）
WEIGHTS = {
    'ranking': 19,
    'diversity': 8,
    'trend': 20,
    'stability': 8,
    'ctr': 14,
    'page_activity': 14,
    'device': 2,
    'region': 4,
    'concentration': 2,
    'content': 9,
}

# CTR行业基准 (FirstPageSage 2026)
CTR_BENCHMARKS = {
    (0, 1): 0.398, (1, 2): 0.187, (2, 3): 0.102,
    (3, 5): 0.0625, (5, 10): 0.0276,
    (10, 20): 0.0098, (20, 50): 0.003, (50, 100): 0.0005,
}

# 等级系统 (V3.3修复: 90→101解决边界BUG)
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
    
    # 准备数据
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
    
    # 获取月份列表
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
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标1: 关键词排名分布 (19%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        details['ranking'] = {'monthly_scores': monthly_s1, 'name': '关键词排名分布'}
    else:
        results['ranking'] = 0
        details['ranking'] = {'monthly_scores': [], 'name': '关键词排名分布'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标2: 关键词多样性 (8%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if by_query is not None and len(months) > 0:
        monthly_s2 = []
        for date in months:
            mq = by_query[by_query['data_date'] == date]
            eff = len(mq[mq['impressions'] >= 10])
            monthly_s2.append(piecewise_linear(eff, THRESHOLDS['diversity']['bp'], THRESHOLDS['diversity']['sc']))
        results['diversity'] = np.median(monthly_s2)
        details['diversity'] = {'monthly_scores': monthly_s2, 'name': '关键词多样性'}
    else:
        results['diversity'] = 0
        details['diversity'] = {'monthly_scores': [], 'name': '关键词多样性'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标3: 流量趋势-复合F (20%) — V3.3修复: 滑动窗口+排除零流量段
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if n_days >= 90:
        # F1: 滑动窗口(步长30天)计算月度变化率中位数
        segment_rates = []
        for i in range(0, n_days - 90 + 1, 30):
            seg = clicks[i:i + 90]
            x_seg = np.arange(len(seg))
            mean_seg = np.mean(seg)
            if np.std(seg) > 0 and mean_seg >= 1.0:  # 排除零流量段
                slope, _, _, _, _ = scipy_stats.linregress(x_seg, seg)
                rate = slope / mean_seg * 30
                segment_rates.append(rate)
        
        f1_rate = np.median(segment_rates) if segment_rates else -0.3
        s_f1 = piecewise_linear(f1_rate, THRESHOLDS['trend_f1']['bp'], THRESHOLDS['trend_f1']['sc'])
        
        # F2: 保留率
        peak_90d = max(np.mean(clicks[i:i + 90]) for i in range(0, n_days - 89))
        latest_90d = np.mean(clicks[-90:])
        retention = latest_90d / peak_90d if peak_90d > 0 else 0
        s_f2 = piecewise_linear(retention, THRESHOLDS['trend_f2']['bp'], THRESHOLDS['trend_f2']['sc'])
        
        results['trend'] = (s_f1 + s_f2) / 2
        details['trend'] = {'f1_rate': f1_rate, 'retention': retention, 's_f1': s_f1, 's_f2': s_f2, 'name': '流量趋势'}
    else:
        results['trend'] = 50
        details['trend'] = {'name': '流量趋势'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标4: 流量稳定性 (8%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        details['stability'] = {'cv_median': cv_median, 'name': '流量稳定性'}
    else:
        results['stability'] = 50
        details['stability'] = {'name': '流量稳定性'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标5: CTR效率 (14%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        details['ctr'] = {'monthly_scores': monthly_s5, 'name': 'CTR效率'}
    else:
        results['ctr'] = 0
        details['ctr'] = {'monthly_scores': [], 'name': 'CTR效率'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标6: 页面活跃度 (14%)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if by_page is not None and len(months) > 0:
        monthly_s6 = []
        for date in months:
            mp = by_page[by_page['data_date'] == date]
            total_p = mp['page'].nunique() if len(mp) > 0 else 0
            click_p = mp[mp['clicks'] > 0]['page'].nunique() if len(mp) > 0 else 0
            rate = click_p / total_p if total_p > 0 else 0
            monthly_s6.append(piecewise_linear(rate, THRESHOLDS['page_activity']['bp'], THRESHOLDS['page_activity']['sc']))
        results['page_activity'] = np.median(monthly_s6)
        details['page_activity'] = {'monthly_scores': monthly_s6, 'name': '页面活跃度'}
    else:
        results['page_activity'] = 0
        details['page_activity'] = {'monthly_scores': [], 'name': '页面活跃度'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标7: 设备适配 (2%) × 规模系数
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        details['device'] = {'monthly_scores': monthly_s7, 'name': '设备适配'}
    else:
        results['device'] = 0
        details['device'] = {'monthly_scores': [], 'name': '设备适配'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标8: 地区覆盖 (4%) × 规模系数
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        details['region'] = {'monthly_scores': monthly_s8, 'name': '地区覆盖'}
    else:
        results['region'] = 0
        details['region'] = {'monthly_scores': [], 'name': '地区覆盖'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标9: 页面集中度 (2%) × 规模系数 — V3.3修复: 近6月数据
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        details['concentration'] = {'gini': gini, 'name': '页面集中度'}
    else:
        results['concentration'] = 0
        details['concentration'] = {'name': '页面集中度'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 指标10: 内容深度与更新 (9%) — V3.3修复: 滚动6月新鲜度
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if query_page is not None and by_query is not None and len(months) > 0:
        # 页面覆盖深度
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
        
        # 内容新鲜度 (滚动6月窗口)
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
        details['content'] = {'depth_score': s_depth, 'freshness_score': s_freshness, 'name': '内容深度与更新'}
    else:
        results['content'] = 0
        details['content'] = {'name': '内容深度与更新'}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 加权总分
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    final_score = sum(results[key] * WEIGHTS[key] / 100 for key in WEIGHTS)
    
    # 等级判定
    grade = 'F'
    grade_label = '濒死'
    grade_label_en = 'Failing'
    grade_color = '#450a0a'
    for low, high, g, label_cn, label_en, color in GRADE_SYSTEM:
        if low <= final_score < high:
            grade = g
            grade_label = label_cn
            grade_label_en = label_en
            grade_color = color
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
            'issue_en': 'Keyword rankings critically low, almost no Top 10 keywords',
            'action_cn': '聚焦长尾关键词，优化现有11-20位关键词的页面内容深度和内链',
            'action_en': 'Focus on long-tail keywords, optimize content depth for keywords ranked 11-20',
        },
        'diversity': {
            'issue_cn': '有效关键词数量不足，搜索覆盖面窄',
            'issue_en': 'Insufficient effective keywords, narrow search coverage',
            'action_cn': '扩展内容矩阵，针对B2B买家旅程各阶段创建内容',
            'action_en': 'Expand content matrix, create content for each B2B buyer journey stage',
        },
        'trend': {
            'issue_cn': '流量持续下降，站点可能面临严重问题',
            'issue_en': 'Traffic continuously declining, site may face serious issues',
            'action_cn': '排查索引问题、算法惩罚、竞争对手抢占；制定内容恢复计划',
            'action_en': 'Investigate indexing issues, algorithm penalties, competitor displacement',
        },
        'stability': {
            'issue_cn': '流量波动剧烈，缺乏稳定的自然搜索基础',
            'issue_en': 'Traffic highly volatile, lacking stable organic search foundation',
            'action_cn': '建立常青内容体系，减少对单一关键词/页面的依赖',
            'action_en': 'Build evergreen content system, reduce dependency on single keywords/pages',
        },
        'ctr': {
            'issue_cn': 'CTR效率低于行业基准，标题和描述吸引力不足',
            'issue_en': 'CTR efficiency below industry benchmark, titles and descriptions lack appeal',
            'action_cn': '优化Title/Meta Description，加入数字、年份、行动号召词；测试结构化数据',
            'action_en': 'Optimize Title/Meta Description with numbers, dates, CTAs; test structured data',
        },
        'page_activity': {
            'issue_cn': '大量页面零点击，内容资产利用率低',
            'issue_en': 'Many pages with zero clicks, low content asset utilization',
            'action_cn': '审计零流量页面：更新、合并或删除；集中资源到高潜力页面',
            'action_en': 'Audit zero-traffic pages: update, consolidate, or remove',
        },
        'content': {
            'issue_cn': '内容深度不足且更新频率低',
            'issue_en': 'Insufficient content depth and low update frequency',
            'action_cn': '为核心页面扩展关键词覆盖(每页≥5个相关词)；建立定期内容更新机制',
            'action_en': 'Expand keyword coverage per page (≥5 related terms); establish regular update schedule',
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
                'key': key,
                'score': score,
                'level': level,
                'weight': WEIGHTS.get(key, 0),
                'issue': rule['issue_cn'] if lang == '中文' else rule['issue_en'],
                'action': rule['action_cn'] if lang == '中文' else rule['action_en'],
            })
    
    return diagnosis


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
    st.caption("B2B SEO Health Intelligence v3.3 | Based on GSC Data")


# ============================================================
# 页面1：总览仪表盘
# ============================================================
if page in ["📊 总览仪表盘", "📊 Overview Dashboard"]:
    st.markdown(f'<div class="page-title">{"📊 B2B SEO 总览仪表盘" if lang == "中文" else "📊 B2B SEO Overview Dashboard"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于 Google Search Console 数据的 V3.3 十维度 SEO 健康诊断" if lang == "中文" else "V3.3 Ten-dimension SEO health diagnosis based on GSC data"}</div>', unsafe_allow_html=True)
    
    # 计算V3.3评分
    score_result = calculate_seo_score_v33(data)
    
    # 顶部评分 + 核心指标
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
        if s >= 60:
            colors.append('#059669')
        elif s >= 40:
            colors.append('#d97706')
        else:
            colors.append('#dc2626')
    
    fig_bar = go.Figure(go.Bar(
        x=scores_list,
        y=names,
        orientation='h',
        marker_color=colors,
        text=[f"{s:.1f}" for s in scores_list],
        textposition='outside',
        textfont=dict(size=13)
    ))
    fig_bar.update_layout(
        height=450,
        xaxis=dict(range=[0, 105], title='Score', tickfont=dict(size=13)),
        yaxis=dict(tickfont=dict(size=13), autorange='reversed'),
        margin=dict(l=200, r=60, t=20, b=40),
        font=dict(size=14)
    )
    fig_bar.add_vline(x=60, line_dash="dash", line_color="#9ca3af", annotation_text="及格线(60)" if lang == '中文' else "Pass(60)")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # 雷达图 (10维度)
    st.markdown(f"### {'🎯 综合能力雷达图' if lang == '中文' else '🎯 Capability Radar'}")
    
    radar_labels = [indicator_names[k][0 if lang == '中文' else 1] for k in indicator_names]
    radar_values = [indicators[k] for k in indicator_names]
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=radar_values + [radar_values[0]],
        theta=radar_labels + [radar_labels[0]],
        fill='toself',
        fillcolor='rgba(26, 86, 219, 0.15)',
        line=dict(color='#1a56db', width=2.5),
        marker=dict(size=6, color='#1a56db')
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=12)),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        height=500,
        margin=dict(l=80, r=80, t=40, b=40),
        font=dict(size=13)
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ============================================================
# 页面2：SEO 健康度评分详情
# ============================================================
elif page in ["🎯 SEO 健康度评分", "🎯 SEO Health Score"]:
    st.markdown(f'<div class="page-title">{"🎯 SEO 健康度评分详情 (V3.3)" if lang == "中文" else "🎯 SEO Health Score Details (V3.3)"}</div>', unsafe_allow_html=True)
    
    score_result = calculate_seo_score_v33(data)
    
    # 总分展示
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem; background: linear-gradient(135deg, #eff6ff, #dbeafe); border-radius: 16px; margin-bottom: 2rem;">
        <div style="font-size: 4rem; font-weight: 800; color: {score_result['grade_color']};">{score_result['final_score']}</div>
        <div style="font-size: 1.5rem; color: {score_result['grade_color']}; font-weight: 600;">{score_result['grade']} · {score_result['grade_label'] if lang == '中文' else score_result['grade_label_en']}</div>
        <div style="font-size: 1rem; color: #6b7280; margin-top: 0.5rem;">{"V3.3 十维度评估模型 | AHP权重验证(CR=0.0182) | 分段线性插值" if lang == "中文" else "V3.3 Ten-dimension model | AHP weights (CR=0.0182) | Piecewise linear interpolation"}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 各指标详细得分
    st.markdown(f"### {'📊 各指标得分明细' if lang == '中文' else '📊 Indicator Score Details'}")
    
    indicator_info = {
        'ranking': ('关键词排名分布', 'Keyword Ranking Distribution', 19, '加权排名分(Top3×5+Top10×3+Top20×2+Top50×1)/总词数'),
        'diversity': ('关键词多样性', 'Keyword Diversity', 8, '月度有效关键词数(曝光≥10)'),
        'trend': ('流量趋势-复合F', 'Traffic Trend (Composite F)', 20, 'F1方向性(滑动窗口月度变化率) + F2保留率'),
        'stability': ('流量稳定性', 'Traffic Stability', 8, '去趋势后28天滚动CV中位数'),
        'ctr': ('CTR效率', 'CTR Efficiency', 14, '各排名位(实际CTR/行业基准CTR)按曝光加权'),
        'page_activity': ('页面活跃度', 'Page Activity', 14, '有点击页面占比'),
        'device': ('设备适配', 'Device Adaptation', 2, 'Mobile CTR / Desktop CTR × 规模系数'),
        'region': ('地区覆盖', 'Region Coverage', 4, '(有点击国家数 + Top1集中度) / 2 × 规模系数'),
        'concentration': ('页面集中度', 'Page Concentration', 2, 'Gini系数(近6月) × 规模系数'),
        'content': ('内容深度与更新', 'Content Depth & Freshness', 9, '(页面关键词覆盖深度 + 滚动6月新鲜度) / 2'),
    }
    
    indicators = score_result['indicators']
    
    for key in ['ranking', 'diversity', 'trend', 'stability', 'ctr', 'page_activity', 'device', 'region', 'concentration', 'content']:
        cn, en, weight, formula = indicator_info[key]
        name = cn if lang == '中文' else en
        score = indicators[key]
        
        if score >= 60:
            color = '#059669'
        elif score >= 40:
            color = '#d97706'
        else:
            color = '#dc2626'
        
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"**{name}** <span style='color:#6b7280;font-size:0.85rem;'>({formula})</span>", unsafe_allow_html=True)
            st.progress(min(score / 100, 1.0))
        with col2:
            st.markdown(f"<span style='font-size:1.3rem;font-weight:700;color:{color};'>{score:.1f}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<span style='color:#6b7280;'>权重{weight}%</span>", unsafe_allow_html=True)
    
    # 等级对照表
    st.markdown("---")
    st.markdown(f"### {'📋 等级对照表' if lang == '中文' else '📋 Grade Reference'}")
    
    grade_df = pd.DataFrame([
        {'等级': g, '分数范围': f'{low}-{high - 1 if high != 101 else 100}', '描述': desc_cn, 'Description': desc_en}
        for low, high, g, desc_cn, desc_en, _ in GRADE_SYSTEM
    ])
    if lang == '中文':
        st.dataframe(grade_df[['等级', '分数范围', '描述']], use_container_width=True, hide_index=True)
    else:
        st.dataframe(grade_df[['等级', '分数范围', 'Description']], use_container_width=True, hide_index=True)


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
                subplot_titles=('点击数 & 移动平均线' if lang == '中文' else 'Clicks & Moving Averages', '展示量 (Volume)' if lang == '中文' else 'Impressions (Volume)'))
            
            fig.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['clicks'], mode='markers', name='每日点击' if lang == '中文' else 'Daily Clicks',
                marker=dict(color='#93c5fd', size=4, opacity=0.6)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['MA7'], mode='lines', name='MA7', line=dict(color='#1a56db', width=2.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_filtered['data_date'], y=df_filtered['MA30'], mode='lines', name='MA30', line=dict(color='#dc2626', width=2, dash='dash')), row=1, col=1)
            
            colors = ['#22c55e' if row['clicks'] > 0 else '#ef4444' for _, row in df_filtered.iterrows()]
            fig.add_trace(go.Bar(x=df_filtered['data_date'], y=df_filtered['impressions'], name='展示量' if lang == '中文' else 'Impressions', marker_color=colors, opacity=0.7), row=2, col=1)
            
            fig.update_layout(height=650, font=dict(size=14), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=13)), margin=dict(l=60, r=20, t=80, b=40), hovermode='x unified')
            fig.update_yaxes(title_text='Clicks', row=1, col=1)
            fig.update_yaxes(title_text='Impressions', row=2, col=1)
            st.plotly_chart(fig, use_container_width=True)
            
            # CTR & Position 趋势
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
        
        st.markdown(f"### {'🏆 Top 20 关键词' if lang == '中文' else '🏆 Top 20 Keywords'}")
        top20 = df.nlargest(20, 'clicks')[['query', 'clicks', 'impress
