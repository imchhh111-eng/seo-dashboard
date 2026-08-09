
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="B2B SEO Health Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html, body, [class*="css"] { font-size: 16px; }
.sidebar-title { font-size: 1.5rem; font-weight: 700; color: #1a56db; padding: 1rem 0; border-bottom: 2px solid #e5e7eb; margin-bottom: 1rem; }
.metric-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }
.metric-value { font-size: 2.2rem; font-weight: 700; color: #1a56db; margin: 0.5rem 0; }
.metric-label { font-size: 0.95rem; color: #6b7280; font-weight: 500; }
.score-ring { width: 180px; height: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-direction: column; margin: 0 auto; border: 8px solid; animation: pulse 2.5s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.04); } }
.score-number { font-size: 3rem; font-weight: 800; }
.score-grade { font-size: 1.2rem; font-weight: 600; }
.page-title { font-size: 1.8rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; animation: fadeIn 0.6s ease-out; }
.page-subtitle { font-size: 1rem; color: #6b7280; margin-bottom: 1.5rem; animation: fadeIn 0.8s ease-out; }
.color-legend { display: flex; gap: 1.5rem; align-items: center; padding: 0.8rem 1.2rem; background: #f9fafb; border-radius: 8px; margin: 0.5rem 0 1.5rem 0; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem; color: #374151; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; }
.chart-fade { animation: fadeIn 1s ease-out; }
.chart-grow { animation: growUp 0.8s ease-out; transform-origin: bottom; }
.chart-fly { animation: flyIn 0.9s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
.chart-fadein { animation: fadeIn 1.2s ease-in; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes growUp { from { opacity: 0; transform: scaleY(0.3); } to { opacity: 1; transform: scaleY(1); } }
@keyframes flyIn { from { opacity: 0; transform: translateX(-30px) scale(0.9); } to { opacity: 1; transform: translateX(0) scale(1); } }
.styled-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; margin: 1rem 0; }
.styled-table thead tr { background: #1a56db; color: #ffffff; text-align: left; }
.styled-table th { padding: 0.75rem 1rem; font-weight: 600; }
.styled-table td { padding: 0.65rem 1rem; border-bottom: 1px solid #e5e7eb; }
.styled-table tbody tr { transition: background 0.2s ease; animation: rowFadeIn 0.5s ease-out backwards; }
.styled-table tbody tr:nth-child(even) { background: #f9fafb; }
.styled-table tbody tr:hover { background: #eff6ff; }
.styled-table tbody tr:nth-child(1) { animation-delay: 0.05s; }
.styled-table tbody tr:nth-child(2) { animation-delay: 0.1s; }
.styled-table tbody tr:nth-child(3) { animation-delay: 0.15s; }
.styled-table tbody tr:nth-child(4) { animation-delay: 0.2s; }
.styled-table tbody tr:nth-child(5) { animation-delay: 0.25s; }
.styled-table tbody tr:nth-child(6) { animation-delay: 0.3s; }
.styled-table tbody tr:nth-child(7) { animation-delay: 0.35s; }
.styled-table tbody tr:nth-child(8) { animation-delay: 0.4s; }
.styled-table tbody tr:nth-child(9) { animation-delay: 0.45s; }
.styled-table tbody tr:nth-child(10) { animation-delay: 0.5s; }
.styled-table tbody tr:nth-child(11) { animation-delay: 0.55s; }
.styled-table tbody tr:nth-child(12) { animation-delay: 0.6s; }
.styled-table tbody tr:nth-child(13) { animation-delay: 0.65s; }
.styled-table tbody tr:nth-child(14) { animation-delay: 0.7s; }
.styled-table tbody tr:nth-child(15) { animation-delay: 0.75s; }
.styled-table tbody tr:nth-child(16) { animation-delay: 0.8s; }
.styled-table tbody tr:nth-child(17) { animation-delay: 0.85s; }
.styled-table tbody tr:nth-child(18) { animation-delay: 0.9s; }
.styled-table tbody tr:nth-child(19) { animation-delay: 0.95s; }
.styled-table tbody tr:nth-child(20) { animation-delay: 1.0s; }
@keyframes rowFadeIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
.val-good { color: #059669; font-weight: 600; }
.val-mid { color: #d97706; font-weight: 600; }
.val-bad { color: #dc2626; font-weight: 600; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

def piecewise_linear(value, breakpoints, scores):
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
WEIGHTS = {'ranking': 19, 'diversity': 8, 'trend': 20, 'stability': 8, 'ctr': 14, 'page_activity': 14, 'device': 2, 'region': 4, 'concentration': 2, 'content': 9}
CTR_BENCHMARKS = {(0, 1): 0.398, (1, 2): 0.187, (2, 3): 0.102, (3, 5): 0.0625, (5, 10): 0.0276, (10, 20): 0.0098, (20, 50): 0.003, (50, 100): 0.0005}
GRADE_SYSTEM = [(90, 101, 'A+', '卓越', 'Excellent', '#059669'), (80, 90, 'A', '优秀', 'Great', '#10b981'), (70, 80, 'B+', '良好', 'Good', '#2563eb'), (60, 70, 'B', '中上', 'Above Avg', '#3b82f6'), (50, 60, 'C+', '中等', 'Average', '#d97706'), (40, 50, 'C', '中下', 'Below Avg', '#f59e0b'), (30, 40, 'D+', '较差', 'Poor', '#dc2626'), (20, 30, 'D', '差', 'Bad', '#b91c1c'), (10, 20, 'E', '危险', 'Critical', '#7f1d1d'), (0, 10, 'F', '濒死', 'Failing', '#450a0a')]

def calculate_seo_score_v33(data):
    results = {}
    details = {}
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
        clicks, n_days, daily_avg, scale_factor = np.array([]), 0, 0, 0.5
    if by_query is not None and len(months) > 0:
        ms1 = []
        for date in months:
            mq = by_query[by_query['data_date'] == date]
            pos = mq['position'].values
            if len(pos) > 0:
                ws = (np.sum(pos <= 3) * 5 + np.sum((pos > 3) & (pos <= 10)) * 3 + np.sum((pos > 10) & (pos <= 20)) * 2 + np.sum((pos > 20) & (pos <= 50)) * 1) / len(pos)
                ms1.append(piecewise_linear(ws, THRESHOLDS['ranking']['bp'], THRESHOLDS['ranking']['sc']))
            else:
                ms1.append(0)
        results['ranking'] = np.median(ms1)
    else:
        results['ranking'] = 0
    if by_query is not None and len(months) > 0:
        ms2 = []
        for date in months:
            mq = by_query[by_query['data_date'] == date]
            ms2.append(piecewise_linear(len(mq[mq['impressions'] >= 10]), THRESHOLDS['diversity']['bp'], THRESHOLDS['diversity']['sc']))
        results['diversity'] = np.median(ms2)
    else:
        results['diversity'] = 0
    if n_days >= 90:
        seg_rates = []
        for i in range(0, n_days - 90 + 1, 30):
            seg = clicks[i:i + 90]
            m = np.mean(seg)
            if np.std(seg) > 0 and m >= 1.0:
                slope = scipy_stats.linregress(np.arange(len(seg)), seg)[0]
                seg_rates.append(slope / m * 30)
        f1_rate = np.median(seg_rates) if seg_rates else -0.3
        s_f1 = piecewise_linear(f1_rate, THRESHOLDS['trend_f1']['bp'], THRESHOLDS['trend_f1']['sc'])
        peak_90d = max(np.mean(clicks[i:i + 90]) for i in range(0, n_days - 89))
        retention = np.mean(clicks[-90:]) / peak_90d if peak_90d > 0 else 0
        s_f2 = piecewise_linear(retention, THRESHOLDS['trend_f2']['bp'], THRESHOLDS['trend_f2']['sc'])
        results['trend'] = (s_f1 + s_f2) / 2
        details['trend'] = {'f1_rate': f1_rate, 'retention': retention, 's_f1': s_f1, 's_f2': s_f2}
    else:
        results['trend'] = 50
    if n_days >= 28:
        x_all = np.arange(n_days)
        sl, ic, _, _, _ = scipy_stats.linregress(x_all, clicks)
        residuals = clicks - (sl * x_all + ic)
        rcv = []
        for i in range(28, n_days):
            wm = np.mean(clicks[i - 28:i])
            if wm > 0:
                rcv.append(np.std(residuals[i - 28:i]) / wm)
        results['stability'] = piecewise_linear(np.median(rcv) if rcv else 1.0, THRESHOLDS['stability']['bp'], THRESHOLDS['stability']['sc'])
    else:
        results['stability'] = 50
    if by_query is not None and len(months) > 0:
        ms5 = []
        for date in months:
            mq = by_query[by_query['data_date'] == date]
            tw_eff, tw = 0, 0
            for (lo, hi), bench in CTR_BENCHMARKS.items():
                seg = mq[(mq['position'] > lo) & (mq['position'] <= hi)]
                if len(seg) > 0 and seg['impressions'].sum() > 0:
                    eff = min((seg['clicks'].sum() / seg['impressions'].sum()) / bench, 2.0)
                    w = seg['impressions'].sum()
                    tw_eff += eff * w
                    tw += w
            ms5.append(piecewise_linear(tw_eff / tw if tw > 0 else 0, THRESHOLDS['ctr']['bp'], THRESHOLDS['ctr']['sc']))
        results['ctr'] = np.median(ms5)
    else:
        results['ctr'] = 0
    if by_page is not None and len(months) > 0:
        ms6 = []
        for date in months:
            mp = by_page[by_page['data_date'] == date]
            tp = mp['page'].nunique() if len(mp) > 0 else 0
            cp = mp[mp['clicks'] > 0]['page'].nunique() if len(mp) > 0 else 0
            ms6.append(piecewise_linear(cp / tp if tp > 0 else 0, THRESHOLDS['page_activity']['bp'], THRESHOLDS['page_activity']['sc']))
        results['page_activity'] = np.median(ms6)
    else:
        results['page_activity'] = 0
    if by_device is not None and len(months) > 0:
        ms7 = []
        for date in months:
            md = by_device[by_device['data_date'] == date]
            dk = md[md['device'] == 'DESKTOP']
            mb = md[md['device'] == 'MOBILE']
            dc = dk['clicks'].sum() / dk['impressions'].sum() if len(dk) > 0 and dk['impressions'].sum() > 0 else 0
            mc = mb['clicks'].sum() / mb['impressions'].sum() if len(mb) > 0 and mb['impressions'].sum() > 0 else 0
            ms7.append(piecewise_linear(mc / dc if dc > 0 else 0, THRESHOLDS['device']['bp'], THRESHOLDS['device']['sc']))
        results['device'] = np.median(ms7) * scale_factor
    else:
        results['device'] = 0
    if by_country is not None and len(months) > 0:
        ms8 = []
        for date in months:
            mc = by_country[by_country['data_date'] == date]
            cc = len(mc[mc['clicks'] > 0]) if len(mc) > 0 else 0
            sa = piecewise_linear(cc, THRESHOLDS['region_count']['bp'], THRESHOLDS['region_count']['sc'])
            top1 = mc.sort_values('impressions', ascending=False).iloc[0]['impressions'] / mc['impressions'].sum() if len(mc) > 0 and mc['impressions'].sum() > 0 else 1.0
            sb = piecewise_linear(top1, THRESHOLDS['region_concentration']['bp'], THRESHOLDS['region_concentration']['sc'])
            ms8.append((sa + sb) / 2)
        results['region'] = np.median(ms8) * scale_factor
    else:
        results['region'] = 0
    if by_page is not None and len(months) > 0:
        r6m = months[-6:] if len(months) >= 6 else months
        rp = by_page[by_page['data_date'].isin(r6m)]
        pt = rp.groupby('page')['clicks'].sum()
        pwc = pt[pt > 0].sort_values().values
        if len(pwc) > 1:
            gini = calculate_gini(pwc)
            if 0.50 <= gini <= 0.65:
                s9 = 100
            elif gini < 0.50:
                s9 = piecewise_linear(gini, [0, 0.30, 0.50], [40, 60, 100])
            else:
                s9 = piecewise_linear(gini, [0.65, 0.75, 0.85, 0.95, 1.0], [100, 80, 60, 40, 20])
        else:
            s9 = 0
        results['concentration'] = s9 * scale_factor
    else:
        results['concentration'] = 0
    if query_page is not None and by_query is not None and len(months) > 0:
        md_list = []
        for date in months:
            mqp = query_page[query_page['data_date'] == date]
            if len(mqp) > 0:
                pk = mqp.groupby('page')['query'].nunique()
                dr = len(pk[pk >= 5]) / len(pk) if len(pk) > 0 else 0
            else:
                dr = 0
            md_list.append(piecewise_linear(dr, THRESHOLDS['content_depth']['bp'], THRESHOLDS['content_depth']['sc']))
        s_depth = np.median(md_list)
        nr = []
        for i, date in enumerate(months):
            mq = by_query[by_query['data_date'] == date]
            cw = set(mq['query'].unique())
            pw = set()
            for j in range(max(0, i - 6), i):
                pw.update(by_query[by_query['data_date'] == months[j]]['query'].unique())
            nw = cw if i == 0 else cw - pw
            nr.append(len(nw) / len(cw) if len(cw) > 0 else 0)
        fm = np.median(nr[1:]) if len(nr) > 1 else 0
        s_fresh = piecewise_linear(fm, THRESHOLDS['content_freshness']['bp'], THRESHOLDS['content_freshness']['sc'])
        results['content'] = (s_depth + s_fresh) / 2
    else:
        results['content'] = 0
    final_score = sum(results[k] * WEIGHTS[k] / 100 for k in WEIGHTS)
    grade, gl, gle, gc = 'F', '濒死', 'Failing', '#450a0a'
    for lo, hi, g, lcn, len_, c in GRADE_SYSTEM:
        if lo <= final_score < hi:
            grade, gl, gle, gc = g, lcn, len_, c
            break
    return {'final_score': round(final_score, 1), 'grade': grade, 'grade_label': gl, 'grade_label_en': gle, 'grade_color': gc, 'indicators': results, 'details': details, 'scale_factor': scale_factor, 'daily_avg': daily_avg, 'n_days': n_days, 'n_months': len(months)}

def generate_diagnosis(score_result, lang='中文'):
    indicators = score_result['indicators']
    diagnosis = []
    RULES = {'ranking': {'i': '关键词排名极差，几乎无Top10词', 'ie': 'Rankings critically low', 'a': '聚焦长尾词，优化11-20位页面内容深度和内链', 'ae': 'Focus long-tail, optimize pages ranked 11-20'}, 'diversity': {'i': '有效关键词数量不足，搜索覆盖面窄', 'ie': 'Insufficient effective keywords', 'a': '扩展内容矩阵覆盖B2B买家旅程各阶段', 'ae': 'Expand content for buyer journey stages'}, 'trend': {'i': '流量持续下降，站点面临严重问题', 'ie': 'Traffic continuously declining', 'a': '排查索引/算法惩罚/竞争问题，制定恢复计划', 'ae': 'Check indexing/penalties/competition'}, 'stability': {'i': '流量波动剧烈，缺乏稳定搜索基础', 'ie': 'High traffic volatility', 'a': '建立常青内容体系，减少单一依赖', 'ae': 'Build evergreen content'}, 'ctr': {'i': 'CTR效率低于行业基准', 'ie': 'CTR below benchmark', 'a': '优化Title/Meta Description，加入数字和CTA', 'ae': 'Optimize titles with numbers and CTAs'}, 'page_activity': {'i': '大量页面零点击，内容利用率低', 'ie': 'Many zero-click pages', 'a': '审计零流量页面：更新、合并或删除', 'ae': 'Audit: update, merge, or remove'}, 'content': {'i': '内容深度不足且更新频率低', 'ie': 'Low content depth and freshness', 'a': '扩展页面关键词覆盖，建立定期更新机制', 'ae': 'Expand coverage + regular updates'}}
    for key, score in sorted(indicators.items(), key=lambda x: x[1]):
        if key in RULES:
            if score < 20:
                lv = 'urgent'
            elif score < 40:
                lv = 'attention'
            else:
                continue
            r = RULES[key]
            diagnosis.append({'key': key, 'score': score, 'level': lv, 'weight': WEIGHTS.get(key, 0), 'issue': r['i'] if lang == '中文' else r['ie'], 'action': r['a'] if lang == '中文' else r['ae']})
    return diagnosis

def render_styled_table(df, highlight_col=None):
    html = '<table class="styled-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = row[col]
            css = ''
            if highlight_col and col == highlight_col:
                try:
                    nv = float(str(val).replace('%', '').replace(',', ''))
                    css = 'val-good' if nv >= 60 else ('val-mid' if nv >= 40 else 'val-bad')
                except (ValueError, TypeError):
                    pass
            html += f'<td class="{css}">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

EXPLANATIONS = {
    'overview': {
        'cn': """**十维度评估模型**基于 Google Search Console 数据，从搜索可见性、流量质量、用户行为、内容健康四个层面对 B2B 独立站进行量化诊断。\n\n**评分方法：** 采用分段线性插值函数，消除传统阈值评分的边界跳变问题。权重通过 AHP 层次分析法确定（一致性比率 CR=0.0182<0.10）。\n\n**颜色含义：** 🟢绿色(≥60)=健康 | 🟠橙色(40-59)=需关注 | 🔴红色(<40)=需紧急优化\n\n**规模系数：** 对于日均点击<10的低流量站点，结构性指标会乘以规模系数，避免小样本导致评分虚高。""",
        'en': """**Ten-dimension model** quantifies B2B site health using GSC data across: Search Visibility, Traffic Quality, User Behavior, and Content Health.\n\n**Scoring:** Piecewise linear interpolation eliminates boundary jumps. Weights validated via AHP (CR=0.0182<0.10).\n\n**Colors:** 🟢Green(≥60)=Healthy | 🟠Orange(40-59)=Attention | 🔴Red(<40)=Urgent\n\n**Scale factor:** For low-traffic sites (<10 clicks/day), structural metrics are adjusted to prevent inflated scores."""
    },
    'score': {
        'cn': """**各指标计算逻辑：**\n\n• **关键词排名分布(19%)** — 按排名区间加权：Top3×5 + Top10×3 + Top20×2 + Top50×1，除以总词数。反映搜索竞争力。\n\n• **关键词多样性(8%)** — 月度有效关键词数（展示≥10次），衡量搜索覆盖广度。\n\n• **流量趋势(20%)** — 复合指标：F1=滚动90天窗口斜率中位数，F2=最近90天/历史峰值（保留率）。\n\n• **流量稳定性(8%)** — 去趋势后28天滚动CV中位数，越低越稳定。\n\n• **CTR效率(14%)** — 实际CTR与排名基准CTR的比值（如Top1基准=39.8%）。\n\n• **页面活跃度(14%)** — 有点击页面数/总页面数，反映内容利用率。\n\n• **设备适配(2%)** — 移动端CTR/桌面端CTR，接近1为佳。\n\n• **地区覆盖(4%)** — 有点击国家数 + Top1集中度的复合分。\n\n• **页面集中度(2%)** — Gini系数，0.50-0.65为最优区间。\n\n• **内容深度(9%)** — 页面关键词覆盖度 + 内容新鲜度。""",
        'en': """**Metric calculations:**\n\n• **Ranking(19%)** — Weighted by position bands: Top3×5 + Top10×3 + Top20×2 + Top50×1.\n\n• **Diversity(8%)** — Monthly effective keywords (impressions≥10).\n\n• **Trend(20%)** — F1=median slope of 90-day windows, F2=retention vs peak.\n\n• **Stability(8%)** — Detrended 28-day rolling CV.\n\n• **CTR(14%)** — Actual/benchmark CTR by position.\n\n• **Activity(14%)** — Pages with clicks / total pages.\n\n• **Device(2%)** — Mobile/Desktop CTR ratio.\n\n• **Region(4%)** — Country count + concentration.\n\n• **Concentration(2%)** — Gini coefficient (optimal: 0.50-0.65).\n\n• **Content(9%)** — Keyword coverage + freshness."""
    },
    'trends': {
        'cn': """**图表说明：**\n\n**上图 — 点击趋势：** 蓝色散点为每日实际点击，深蓝线为7日移动平均（短期），红色虚线为30日移动平均（长期）。MA7下穿MA30通常意味着短期恶化。\n\n**下图 — 展示量：** 柱状图展示每日搜索展示次数，反映Google曝光量变化。\n\n**CTR与排名：** 绿线=CTR(7日均值)，橙线=排名（Y轴反转，越高越好）。理想状态：CTR上升+排名数值下降。""",
        'en': """**Chart guide:**\n\n**Top — Clicks:** Blue dots = daily, dark blue = 7-day MA, red dashed = 30-day MA. MA7 below MA30 = deterioration.\n\n**Bottom — Impressions:** Daily search visibility.\n\n**CTR & Position:** Green = CTR(7d), Orange = position (inverted). Ideal: CTR up + position down."""
    },
    'keywords': {
        'cn': """**关键词分析说明：**\n\n**Top 20 表格：** 按总点击排序。关注CTR异常低的高展示词——优化Title/Description的首选目标。\n\n**机会矩阵：** X轴=展示量，Y轴=CTR，气泡大小=点击，颜色=排名。**右下角=高展示低CTR**，说明用户搜索了但没点你，标题/描述吸引力不足或意图不匹配。""",
        'en': """**Keyword guide:**\n\n**Top 20:** By clicks. Watch high-impression words with low CTR — optimization targets.\n\n**Opportunity matrix:** X=impressions, Y=CTR, size=clicks, color=position. **Bottom-right = high exposure, low conversion** — optimize titles or check intent."""
    },
    'pages': {
        'cn': """**页面分析说明：**\n\n**活跃率** = 有点击页面 ÷ 总页面。B2B典型值10-30%，低于10%说明大量内容未被利用。\n\n**Top 15：** 按点击排序，颜色=CTR。关注高点击低CTR页面。\n\n**优化机会：** 展示≥50但点击≤5的页面——已获得Google曝光但未转化，是ROI最高的优化目标。""",
        'en': """**Page guide:**\n\n**Activity rate** = Clicked pages ÷ Total. B2B typical: 10-30%.\n\n**Top 15:** By clicks, color=CTR.\n\n**Opportunities:** Impressions≥50, clicks≤5 — visible but not converting. Highest ROI targets."""
    },
    'countries': {
        'cn': """**地区分析说明：**\n\n**世界地图：** 颜色深浅=所选指标强度，可切换点击/展示/CTR/排名。\n\n**评估逻辑：** 得分=有点击国家数(广度) + Top1国家占比(集中度)。对B2B站点，目标市场覆盖比纯粹国家数更重要。""",
        'en': """**Country guide:**\n\n**Map:** Color = metric intensity. Switch between clicks/impressions/CTR/position.\n\n**Scoring:** Country count (breadth) + Top-1 concentration. For B2B, target market coverage > raw country count."""
    },
    'devices': {
        'cn': """**设备分析说明：**\n\n**点击占比：** B2B站点通常桌面端60-80%，但移动端持续增长。\n\n**CTR对比：** 移动端CTR显著低于桌面端（比值<0.7）说明移动体验有问题。\n\n**月度趋势：** 观察设备占比变化，移动端上升则需优先优化移动体验。""",
        'en': """**Device guide:**\n\n**Share:** B2B typical: desktop 60-80%, mobile growing.\n\n**CTR:** Mobile CTR << Desktop (ratio<0.7) = mobile UX issues.\n\n**Trend:** Rising mobile share = prioritize mobile optimization."""
    },
    'anomalies': {
        'cn': """**异常检测说明：**\n\n**方法：** 基于滚动窗口Z-Score，超过阈值标记为异常。\n\n**参数：** 窗口=基准时间范围（28天适合多数场景）；Z阈值=偏离程度（2.5为默认）。\n\n**🔺飙升：** 流量突增——可能被分享/排名跳升/季节性爆发。\n**🔻骤降：** 流量突降——可能索引问题/算法惩罚/服务器故障。""",
        'en': """**Anomaly guide:**\n\n**Method:** Z-Score on rolling window.\n\n**Params:** Window=baseline period (28d default); Z=deviation (2.5 default).\n\n**🔺Spikes:** Sudden surge — sharing/ranking jump/seasonal.\n**🔻Drops:** Sudden loss — indexing/penalty/server/competition."""
    },
    'actions': {
        'cn': """**优化建议说明：**\n\n**优先级：** P0(紧急)=得分<20，需立即行动；P1(关注)=得分20-40，需改进计划。\n\n**提升路径：** 每个指标提升到60分能贡献的总分增益。优先优化增益最大的指标，投入产出比最高。\n\n**计算：** 增益 = (60-当前分) × 权重%。如流量趋势8分×20% = +10.4分潜力。""",
        'en': """**Recommendations guide:**\n\n**Priority:** P0=score<20 (urgent); P1=20-40 (attention).\n\n**Path:** Potential gain if each metric reaches 60. Prioritize highest-gain metrics.\n\n**Formula:** Gain = (60-current) × weight%. E.g., Trend 8×20% = +10.4 potential."""
    }
}

@st.cache_data
def load_data():
    data = {}
    base_path = "data/"
    fm = {'by_date': 'cleaned_by_date.csv', 'by_country': 'cleaned_by_country.csv', 'by_device': 'cleaned_by_device.csv', 'daily_summary': 'cleaned_daily_summary.csv', 'by_query': 'cleaned_by_query.csv', 'by_page': 'cleaned_by_page.csv', 'date_query': 'cleaned_date_query.csv', 'date_page': 'cleaned_date_page.csv', 'query_country': 'cleaned_query_country.csv', 'query_device': 'cleaned_query_device.csv', 'page_country': 'cleaned_page_country.csv', 'page_device': 'cleaned_page_device.csv', 'query_page': 'cleaned_query_page.csv'}
    for key, fn in fm.items():
        fp = os.path.join(base_path, fn)
        data[key] = pd.read_csv(fp) if os.path.exists(fp) else None
    return data

data = load_data()

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 SEO Health Intelligence</div>', unsafe_allow_html=True)
    lang = st.radio("🌐", ['中文', 'English'], horizontal=True, key="lang")
    st.markdown("---")
    nav_cn = ["📊 总览仪表盘", "🎯 健康度评分", "📈 搜索趋势", "🔍 关键词洞察", "📄 页面分析", "🌍 地区分析", "📱 设备分布", "🚨 异常检测", "🚀 优化建议"]
    nav_en = ["📊 Overview", "🎯 Score", "📈 Trends", "🔍 Keywords", "📄 Pages", "🌍 Countries", "📱 Devices", "🚨 Anomalies", "🚀 Actions"]
    nav = nav_cn if lang == '中文' else nav_en
    page = st.radio("导航" if lang == '中文' else "Nav", nav, key="nav")
    st.markdown("---")
    if data.get('by_date') is not None:
        dr = data['by_date']['data_date']
        st.caption(f"📅 {dr.min()} → {dr.max()}")
    st.caption("B2B SEO Health Intelligence")

# ============================================================
# 页面1：总览
# ============================================================
if page in ["📊 总览仪表盘", "📊 Overview"]:
    st.markdown(f'<div class="page-title">{"📊 B2B SEO 总览仪表盘" if lang == "中文" else "📊 B2B SEO Overview"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于 GSC 数据的十维度健康诊断" if lang == "中文" else "Ten-dimension health diagnosis"}</div>', unsafe_allow_html=True)
    score_result = calculate_seo_score_v33(data)
    col_score, col_metrics = st.columns([1, 3])
    with col_score:
        st.markdown(f'<div class="score-ring" style="border-color:{score_result["grade_color"]};"><div class="score-number" style="color:{score_result["grade_color"]};">{score_result["final_score"]}</div><div class="score-grade" style="color:{score_result["grade_color"]};">{score_result["grade"]} · {score_result["grade_label"] if lang == "中文" else score_result["grade_label_en"]}</div></div>', unsafe_allow_html=True)
        st.caption(f"{'周期' if lang == '中文' else 'Period'}: {score_result['n_days']}{'天' if lang == '中文' else 'd'}")
    with col_metrics:
        if data.get('daily_summary') is not None:
            ds = data['daily_summary']
            tc, ti = ds['clicks'].sum(), ds['impressions'].sum()
            ac, ap = tc / max(ti, 1), ds['position'].mean()
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"总点击" if lang == "中文" else "Clicks"}</div><div class="metric-value">{tc:,}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"总展示" if lang == "中文" else "Impressions"}</div><div class="metric-value">{ti:,}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"平均CTR" if lang == "中文" else "Avg CTR"}</div><div class="metric-value">{ac:.2%}</div></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{"平均排名" if lang == "中文" else "Avg Pos"}</div><div class="metric-value">{ap:.1f}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"### {'📐 十维度得分' if lang == '中文' else '📐 Scores'}")
    leg = '<div class="color-legend"><div class="legend-item"><div class="legend-dot" style="background:#059669;"></div>{g}</div><div class="legend-item"><div class="legend-dot" style="background:#d97706;"></div>{m}</div><div class="legend-item"><div class="legend-dot" style="background:#dc2626;"></div>{p}</div><div class="legend-item" style="color:#9ca3af;">┆ {l}</div></div>'
    st.markdown(leg.format(g='优秀(≥60)' if lang == '中文' else 'Good(≥60)', m='中等(40-59)' if lang == '中文' else 'Avg(40-59)', p='较差(<40)' if lang == '中文' else 'Poor(<40)', l='及格线=60' if lang == '中文' else 'Pass=60'), unsafe_allow_html=True)
    with st.expander("ℹ️ 评估模型说明" if lang == '中文' else "ℹ️ About this model", expanded=False):
        st.markdown(EXPLANATIONS['overview']['cn' if lang == '中文' else 'en'])
    ind_names = {'ranking': ('关键词排名分布', 'Keyword Ranking', 19), 'diversity': ('关键词多样性', 'Keyword Diversity', 8), 'trend': ('流量趋势', 'Traffic Trend', 20), 'stability': ('流量稳定性', 'Traffic Stability', 8), 'ctr': ('CTR效率', 'CTR Efficiency', 14), 'page_activity': ('页面活跃度', 'Page Activity', 14), 'device': ('设备适配', 'Device', 2), 'region': ('地区覆盖', 'Region', 4), 'concentration': ('页面集中度', 'Concentration', 2), 'content': ('内容深度', 'Content Depth', 9)}
    indicators = score_result['indicators']
    bnames, bscores, bcolors = [], [], []
    for k in ['ranking', 'diversity', 'trend', 'stability', 'ctr', 'page_activity', 'device', 'region', 'concentration', 'content']:
        cn, en, w = ind_names[k]
        bnames.append(f"{cn}({w}%)" if lang == '中文' else f"{en}({w}%)")
        s = indicators[k]
        bscores.append(s)
        bcolors.append('#059669' if s >= 60 else '#d97706' if s >= 40 else '#dc2626')
    st.markdown('<div class="chart-grow">', unsafe_allow_html=True)
    fig_bar = go.Figure(go.Bar(x=bscores, y=bnames, orientation='h', marker_color=bcolors, text=[f"{s:.1f}" for s in bscores], textposition='outside', textfont=dict(size=13, color='#374151')))
    fig_bar.update_layout(height=460, xaxis=dict(range=[0, 108], showgrid=True, gridcolor='#f3f4f6'), yaxis=dict(autorange='reversed'), margin=dict(l=200, r=80, t=10, b=40), plot_bgcolor='#fff', paper_bgcolor='#fff')
    fig_bar.add_vline(x=60, line_dash="dash", line_color="#9ca3af", annotation_text="Pass(60)", annotation_font_color="#9ca3af")
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"### {'🎯 雷达图' if lang == '中文' else '🎯 Radar'}")
    rleg = '<div class="color-legend"><div class="legend-item"><div class="legend-dot" style="background:rgba(26,86,219,0.4);"></div>{a}</div><div class="legend-item" style="color:#9ca3af;">{b}</div></div>'
    st.markdown(rleg.format(a='当前能力' if lang == '中文' else 'Current', b='外圈=100' if lang == '中文' else 'Outer=100'), unsafe_allow_html=True)
    st.markdown('<div class="chart-fade">', unsafe_allow_html=True)
    rl = [ind_names[k][0 if lang == '中文' else 1] for k in ind_names]
    rv = [indicators[k] for k in ind_names]
    fig_r = go.Figure(data=go.Scatterpolar(r=rv + [rv[0]], theta=rl + [rl[0]], fill='toself', fillcolor='rgba(26,86,219,0.15)', line=dict(color='#1a56db', width=2.5), marker=dict(size=6, color='#1a56db')))
    fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#e5e7eb'), angularaxis=dict(tickfont=dict(size=12))), height=500, margin=dict(l=80, r=80, t=40, b=40), paper_bgcolor='#fff')
    st.plotly_chart(fig_r, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 页面2：评分详情
# ============================================================
elif page in ["🎯 健康度评分", "🎯 Score"]:
    st.markdown(f'<div class="page-title">{"🎯 SEO 健康度评分详情" if lang == "中文" else "🎯 Health Score Details"}</div>', unsafe_allow_html=True)
    score_result = calculate_seo_score_v33(data)
    st.markdown(f'<div style="text-align:center;padding:2rem;background:linear-gradient(135deg,#eff6ff,#dbeafe);border-radius:16px;margin-bottom:2rem;"><div style="font-size:4rem;font-weight:800;color:{score_result["grade_color"]};">{score_result["final_score"]}</div><div style="font-size:1.5rem;color:{score_result["grade_color"]};font-weight:600;">{score_result["grade"]} · {score_result["grade_label"] if lang == "中文" else score_result["grade_label_en"]}</div><div style="font-size:0.95rem;color:#6b7280;margin-top:0.5rem;">{"十维度 | AHP权重 | 分段线性插值" if lang == "中文" else "10-dim | AHP | Piecewise Linear"}</div></div>', unsafe_allow_html=True)
    with st.expander("ℹ️ 各指标计算逻辑" if lang == '中文' else "ℹ️ Metric calculations", expanded=False):
        st.markdown(EXPLANATIONS['score']['cn' if lang == '中文' else 'en'])
    ind_info = {'ranking': ('关键词排名分布', 19, '加权排名分'), 'diversity': ('关键词多样性', 8, '有效词数'), 'trend': ('流量趋势', 20, 'F1+F2'), 'stability': ('流量稳定性', 8, '去趋势CV'), 'ctr': ('CTR效率', 14, '实际/基准'), 'page_activity': ('页面活跃度', 14, '点击页占比'), 'device': ('设备适配', 2, 'M/D比'), 'region': ('地区覆盖', 4, '国家+集中'), 'concentration': ('页面集中度', 2, 'Gini'), 'content': ('内容深度', 9, '覆盖+新鲜')}
    indicators = score_result['indicators']
    for k in ['ranking', 'diversity', 'trend', 'stability', 'ctr', 'page_activity', 'device', 'region', 'concentration', 'content']:
        cn, w, f = ind_info[k]
        s = indicators[k]
        c = '#059669' if s >= 60 else '#d97706' if s >= 40 else '#dc2626'
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1:
            st.markdown(f"**{cn}** <span style='color:#6b7280;font-size:0.85rem;'>({f})</span>", unsafe_allow_html=True)
            st.progress(min(s / 100, 1.0))
        with c2:
            st.markdown(f"<span style='font-size:1.3rem;font-weight:700;color:{c};'>{s:.1f}</span>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<span style='color:#6b7280;'>{w}%</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"### {'📋 等级对照表' if lang == '中文' else '📋 Grades'}")
    gdf = pd.DataFrame([{'等级': g, '分数': f'{lo}-{hi-1 if hi != 101 else 100}', '描述': d} for lo, hi, g, d, _, _ in GRADE_SYSTEM])
    st.markdown(render_styled_table(gdf), unsafe_allow_html=True)


# ============================================================
# 页面3：搜索趋势
# ============================================================
elif page in ["📈 搜索趋势", "📈 Trends"]:
    st.markdown(f'<div class="page-title">{"📈 搜索表现趋势" if lang == "中文" else "📈 Search Trends"}</div>', unsafe_allow_html=True)
    if data.get('by_date') is not None:
        df = data['by_date'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date')
        cs, ce = st.columns(2)
        with cs:
            sd = st.date_input("开始" if lang == '中文' else "Start", value=df['data_date'].min(), key="ts")
        with ce:
            ed = st.date_input("结束" if lang == '中文' else "End", value=df['data_date'].max(), key="te")
        with st.expander("ℹ️ 图表阅读指南" if lang == '中文' else "ℹ️ Chart guide", expanded=False):
            st.markdown(EXPLANATIONS['trends']['cn' if lang == '中文' else 'en'])
        df_f = df[(df['data_date'] >= pd.to_datetime(sd)) & (df['data_date'] <= pd.to_datetime(ed))].copy()
        if len(df_f) > 0:
            df_f['MA7'] = df_f['clicks'].rolling(7, min_periods=1).mean()
            df_f['MA30'] = df_f['clicks'].rolling(30, min_periods=1).mean()
            st.markdown('<div class="chart-fade">', unsafe_allow_html=True)
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
            fig.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['clicks'], mode='markers', name='Clicks', marker=dict(color='#93c5fd', size=4, opacity=0.6)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['MA7'], mode='lines', name='MA7', line=dict(color='#1a56db', width=2.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['MA30'], mode='lines', name='MA30', line=dict(color='#dc2626', width=2, dash='dash')), row=1, col=1)
            fig.add_trace(go.Bar(x=df_f['data_date'], y=df_f['impressions'], name='Impressions', marker_color='#93c5fd', opacity=0.5), row=2, col=1)
            fig.update_layout(height=650, hovermode='x unified', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(l=60, r=20, t=60, b=40), plot_bgcolor='#fff', paper_bgcolor='#fff')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(f"### {'📉 CTR & 排名' if lang == '中文' else '📉 CTR & Position'}")
            st.markdown('<div class="chart-fade">', unsafe_allow_html=True)
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            df_f['ctr7'] = df_f['ctr'].rolling(7, min_periods=1).mean()
            df_f['pos7'] = df_f['position'].rolling(7, min_periods=1).mean()
            fig2.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['ctr7'] * 100, mode='lines', name='CTR%(MA7)', line=dict(color='#059669', width=2.5)), secondary_y=False)
            fig2.add_trace(go.Scatter(x=df_f['data_date'], y=df_f['pos7'], mode='lines', name='Pos(MA7)', line=dict(color='#d97706', width=2.5)), secondary_y=True)
            fig2.update_layout(height=400, legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), plot_bgcolor='#fff', paper_bgcolor='#fff')
            fig2.update_yaxes(title_text="CTR(%)", secondary_y=False)
            fig2.update_yaxes(title_text="Position", autorange="reversed", secondary_y=True)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("未找到数据" if lang == '中文' else "No data")

# ============================================================
# 页面4：关键词洞察
# ============================================================
elif page in ["🔍 关键词洞察", "🔍 Keywords"]:
    st.markdown(f'<div class="page-title">{"🔍 关键词洞察" if lang == "中文" else "🔍 Keyword Insights"}</div>', unsafe_allow_html=True)
    if data.get('by_query') is not None:
        df = data['by_query'].copy()
        tk = df['query'].nunique()
        ck = df[df['clicks'] > 0]['query'].nunique()
        topk = df.nlargest(1, 'clicks')['query'].values[0] if len(df) > 0 else '-'
        k1, k2, k3 = st.columns(3)
        with k1:
            st.
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("总关键词" if lang == '中文' else "Total", f"{tk:,}")
        with k2:
            st.metric("有点击" if lang == '中文' else "Clicked", f"{ck:,}")
        with k3:
            st.metric("Top", topk[:25])
        st.markdown("---")
        with st.expander("ℹ️ 关键词分析说明" if lang == '中文' else "ℹ️ Keyword guide", expanded=False):
            st.markdown(EXPLANATIONS['keywords']['cn' if lang == '中文' else 'en'])
        st.markdown(f"### {'🏆 Top 20' if lang == '中文' else '🏆 Top 20'}")
        t20 = df.nlargest(20, 'clicks')[['query', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        t20.index = t20.index + 1
        t20['ctr'] = t20['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
        t20['position'] = t20['position'].apply(lambda x: f"{x:.1f}")
        t20.columns = ['Keyword', 'Clicks', 'Impressions', 'CTR', 'Position']
        st.markdown(render_styled_table(t20, highlight_col='CTR'), unsafe_allow_html=True)
        st.markdown(f"### {'💎 机会矩阵' if lang == '中文' else '💎 Opportunities'}")
        st.caption("高展示+低CTR=优化机会" if lang == '中文' else "High imp + Low CTR = Opportunity")
        df_o = df[df['impressions'] >= 10].copy()
        if len(df_o) > 0:
            df_o['ctr_v'] = df_o['clicks'] / df_o['impressions'].clip(lower=1)
            st.markdown('<div class="chart-fly">', unsafe_allow_html=True)
            fig_o = px.scatter(df_o, x='impressions', y='ctr_v', size='clicks', color='position', hover_data=['query'], color_continuous_scale='RdYlGn_r')
            fig_o.update_layout(height=500, plot_bgcolor='#fff', paper_bgcolor='#fff')
            st.plotly_chart(fig_o, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("未找到数据")

# ============================================================
# 页面5：页面分析
# ============================================================
elif page in ["📄 页面分析", "📄 Pages"]:
    st.markdown(f'<div class="page-title">{"📄 页面效果分析" if lang == "中文" else "📄 Page Analysis"}</div>', unsafe_allow_html=True)
    if data.get('by_page') is not None:
        df = data['by_page'].copy()
        tp = df['page'].nunique()
        ap = df[df['clicks'] > 0]['page'].nunique()
        ar = ap / max(tp, 1)
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("总页面" if lang == '中文' else "Pages", f"{tp}")
        with p2:
            st.metric("活跃" if lang == '中文' else "Active", f"{ap}")
        with p3:
            st.metric("活跃率" if lang == '中文' else "Rate", f"{ar:.1%}")
        st.markdown("---")
        with st.expander("ℹ️ 页面分析说明" if lang == '中文' else "ℹ️ Page guide", expanded=False):
            st.markdown(EXPLANATIONS['pages']['cn' if lang == '中文' else 'en'])
        st.markdown(f"### {'🏆 Top 15' if lang == '中文' else '🏆 Top 15'}")
        st.markdown('<div class="chart-grow">', unsafe_allow_html=True)
        t15 = df.nlargest(15, 'clicks')[['page', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        fig_p = px.bar(t15, x='clicks', y='page', orientation='h', color='ctr', color_continuous_scale='Blues')
        fig_p.update_layout(height=600, yaxis=dict(tickfont=dict(size=11)), margin=dict(l=300, r=20, t=20, b=40), plot_bgcolor='#fff', paper_bgcolor='#fff')
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"### {'💎 优化机会' if lang == '中文' else '💎 Opportunities'}")
        hi = df[(df['impressions'] >= 50) & (df['clicks'] <= 5)].nlargest(10, 'impressions')
        if len(hi) > 0:
            disp = hi[['page', 'impressions', 'clicks', 'ctr', 'position']].reset_index(drop=True)
            disp.index = disp.index + 1
            disp['ctr'] = disp['ctr'].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:.2f}%")
            disp.columns = ['Page', 'Impressions', 'Clicks', 'CTR', 'Position']
            st.markdown(render_styled_table(disp, highlight_col='CTR'), unsafe_allow_html=True)
    else:
        st.info("未找到数据")

# ============================================================
# 页面6：地区分析
# ============================================================
elif page in ["🌍 地区分析", "🌍 Countries"]:
    st.markdown(f'<div class="page-title">{"🌍 国家/地区分析" if lang == "中文" else "🌍 Country Analysis"}</div>', unsafe_allow_html=True)
    if data.get('by_country') is not None:
        df = data['by_country'].copy()
        md = df.groupby('country').agg({'clicks': 'sum', 'impressions': 'sum', 'ctr': 'mean', 'position': 'mean'}).reset_index()
        md['country_upper'] = md['country'].str.upper()
        md['clicks_log'] = np.log1p(md['clicks'])
        md['imp_log'] = np.log1p(md['impressions'])
        with st.expander("ℹ️ 地区分析说明" if lang == '中文' else "ℹ️ Country guide", expanded=False):
            st.markdown(EXPLANATIONS['countries']['cn' if lang == '中文' else 'en'])
        mm = st.selectbox("🗺️ 指标" if lang == '中文' else "🗺️ Metric", ['clicks', 'impressions', 'ctr', 'position'], format_func=lambda x: {'clicks': '点击', 'impressions': '展示', 'ctr': 'CTR', 'position': '排名'}[x] if lang == '中文' else x, key="ms")
        if mm == 'clicks':
            cc = 'clicks_log'
        elif mm == 'impressions':
            cc = 'imp_log'
        else:
            cc = mm
        cscale = 'Blues' if mm in ['clicks', 'impressions'] else ('Greens' if mm == 'ctr' else 'RdYlGn_r')
        st.markdown('<div class="chart-fadein">', unsafe_allow_html=True)
        fig_m = go.Figure(data=go.Choropleth(locations=md['country_upper'], z=md[cc], locationmode='ISO-3', colorscale=cscale, marker_line_color='#fff', marker_line_width=0.5))
        fig_m.update_layout(geo=dict(showframe=False, projection_type='natural earth', showland=True, landcolor='#f8f9fa'), height=550, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor='#fff')
        st.plotly_chart(fig_m, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"### {'📊 Top 10' if lang == '中文' else '📊 Top 10'}")
        t10 = md.nlargest(10, 'clicks')[['country_upper', 'clicks', 'impressions', 'ctr', 'position']].reset_index(drop=True)
        t10.index = t10.index + 1
        t10['ctr'] = t10['ctr'].apply(lambda x: f"{x:.2%}")
        t10['position'] = t10['position'].apply(lambda x: f"{x:.1f}")
        t10.columns = ['Country', 'Clicks', 'Impressions', 'CTR', 'Position']
        st.markdown(render_styled_table(t10, highlight_col='CTR'), unsafe_allow_html=True)
    else:
        st.warning("未找到数据" if lang == '中文' else "No data")


# ============================================================
# 页面7：设备分布
# ============================================================
elif page in ["📱 设备分布", "📱 Devices"]:
    st.markdown(f'<div class="page-title">{"📱 设备分布" if lang == "中文" else "📱 Devices"}</div>', unsafe_allow_html=True)
    if data.get('by_device') is not None:
        df = data['by_device'].copy()
        ds = df.groupby('device').agg({'clicks': 'sum', 'impressions': 'sum'}).reset_index()
        with st.expander("ℹ️ 设备分析说明" if lang == '中文' else "ℹ️ Device guide", expanded=False):
            st.markdown(EXPLANATIONS['devices']['cn' if lang == '中文' else 'en'])
        cp, cb = st.columns(2)
        with cp:
            st.markdown(f"#### {'点击占比' if lang == '中文' else 'Share'}")
            fp = px.pie(ds, values='clicks', names='device', color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'], hole=0.4)
            fp.update_traces(textposition='inside', textinfo='percent+label')
            fp.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='#fff')
            st.plotly_chart(fp, use_container_width=True)
        with cb:
            st.markdown(f"#### {'CTR对比' if lang == '中文' else 'CTR'}")
            ds['ctr_p'] = ds['clicks'] / ds['impressions'].clip(lower=1)
            fc = px.bar(ds, x='device', y='ctr_p', color='device', color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'])
            fc.update_layout(height=400, yaxis=dict(tickformat='.2%'), showlegend=False, plot_bgcolor='#fff', paper_bgcolor='#fff')
            st.plotly_chart(fc, use_container_width=True)
        st.markdown(f"### {'📈 月度趋势' if lang == '中文' else '📈 Monthly'}")
        df['data_date'] = pd.to_datetime(df['data_date'])
        df['month'] = df['data_date'].dt.to_period('M').astype(str)
        mdev = df.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
        st.markdown('<div class="chart-fade">', unsafe_allow_html=True)
        ft = px.line(mdev, x='month', y='clicks', color='device', markers=True, color_discrete_sequence=['#1a56db', '#60a5fa', '#bfdbfe'])
        ft.update_layout(height=400, plot_bgcolor='#fff', paper_bgcolor='#fff')
        st.plotly_chart(ft, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("未找到设备数据" if lang == '中文' else "No device data")

# ============================================================
# 页面8：异常检测
# ============================================================
elif page in ["🚨 异常检测", "🚨 Anomalies"]:
    st.markdown(f'<div class="page-title">{"🚨 流量异常检测" if lang == "中文" else "🚨 Anomaly Detection"}</div>', unsafe_allow_html=True)
    if data.get('by_date') is not None:
        df = data['by_date'].copy()
        df['data_date'] = pd.to_datetime(df['data_date'])
        df = df.sort_values('data_date').reset_index(drop=True)
        window = st.slider("窗口" if lang == '中文' else "Window", 7, 60, 28, key="aw")
        threshold = st.slider("Z阈值" if lang == '中文' else "Z", 1.5, 4.0, 2.5, 0.5, key="at")
        with st.expander("ℹ️ 异常检测说明" if lang == '中文' else "ℹ️ Detection guide", expanded=False):
            st.markdown(EXPLANATIONS['anomalies']['cn' if lang == '中文' else 'en'])
        df['rm'] = df['clicks'].rolling(window, min_periods=7).mean()
        df['rs'] = df['clicks'].rolling(window, min_periods=7).std()
        df['z'] = (df['clicks'] - df['rm']) / df['rs'].clip(lower=0.1)
        df['anom'] = df['z'].abs() > threshold
        df['atype'] = 'normal'
        df.loc[df['z'] > threshold, 'atype'] = 'spike'
        df.loc[df['z'] < -threshold, 'atype'] = 'drop'
        anoms = df[df['anom']]
        sp = len(anoms[anoms['atype'] == 'spike'])
        dr = len(anoms[anoms['atype'] == 'drop'])
        a1, a2, a3 = st.columns(3)
        with a1:
            st.metric("异常天数" if lang == '中文' else "Anomalies", f"{len(anoms)}")
        with a2:
            st.metric("🔺 飙升" if lang == '中文' else "🔺 Spikes", f"{sp}")
        with a3:
            st.metric("🔻 骤降" if lang == '中文' else "🔻 Drops", f"{dr}")
        st.markdown("---")
        st.markdown('<div class="chart-fade">', unsafe_allow_html=True)
        fig_a = go.Figure()
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=df['clicks'], mode='lines', name='Clicks', line=dict(color='#93c5fd', width=1.5)))
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=df['rm'], mode='lines', name=f'MA{window}', line=dict(color='#1a56db', width=2)))
        up = df['rm'] + threshold * df['rs']
        lo = df['rm'] - threshold * df['rs']
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=up, mode='lines', name='Upper', line=dict(color='#d1d5db', width=1, dash='dot')))
        fig_a.add_trace(go.Scatter(x=df['data_date'], y=lo, mode='lines', name='Lower', line=dict(color='#d1d5db', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(209,213,219,0.1)'))
        sdf = df[df['atype'] == 'spike']
        ddf = df[df['atype'] == 'drop']
        if len(sdf) > 0:
            fig_a.add_trace(go.Scatter(x=sdf['data_date'], y=sdf['clicks'], mode='markers', name='Spike', marker=dict(color='#dc2626', size=10, symbol='triangle-up')))
        if len(ddf) > 0:
            fig_a.add_trace(go.Scatter(x=ddf['data_date'], y=ddf['clicks'], mode='markers', name='Drop', marker=dict(color='#059669', size=10, symbol='triangle-down')))
        fig_a.update_layout(height=500, hovermode='x unified', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(l=60, r=20, t=40, b=40), plot_bgcolor='#fff', paper_bgcolor='#fff')
        st.plotly_chart(fig_a, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if len(anoms) > 0:
            st.markdown(f"### {'📋 异常列表' if lang == '中文' else '📋 Events'}")
            da = anoms[['data_date', 'clicks', 'rm', 'z', 'atype']].copy()
            da['data_date'] = da['data_date'].dt.strftime('%Y-%m-%d')
            da['rm'] = da['rm'].apply(lambda x: f"{x:.1f}")
            da['z'] = da['z'].apply(lambda x: f"{x:.2f}")
            da.columns = ['Date', 'Clicks', 'Expected', 'Z-Score', 'Type']
            da_s = da.sort_values('Date', ascending=False).head(30).reset_index(drop=True)
            st.markdown(render_styled_table(da_s), unsafe_allow_html=True)
    else:
        st.warning("未找到数据" if lang == '中文' else "No data")

# ============================================================
# 页面9：优化建议
# ============================================================
elif page in ["🚀 优化建议", "🚀 Actions"]:
    st.markdown(f'<div class="page-title">{"🚀 SEO 优化建议" if lang == "中文" else "🚀 Recommendations"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{"基于十维度模型自动生成诊断建议" if lang == "中文" else "Auto-generated from ten-dimension model"}</div>', unsafe_allow_html=True)
    score_result = calculate_seo_score_v33(data)
    diagnosis = generate_diagnosis(score_result, lang)
    uc = sum(1 for d in diagnosis if d['level'] == 'urgent')
    ac2 = sum(1 for d in diagnosis if d['level'] == 'attention')
    hc = 10 - uc - ac2
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🔴 紧急" if lang == '中文' else "🔴 Urgent", f"{uc}")
    with c2:
        st.metric("🟡 关注" if lang == '中文' else "🟡 Attention", f"{ac2}")
    with c3:
        st.metric("🟢 健康" if lang == '中文' else "🟢 Healthy", f"{hc}")
    st.markdown("---")
    with st.expander("ℹ️ 建议逻辑说明" if lang == '中文' else "ℹ️ How this works", expanded=False):
        st.markdown(EXPLANATIONS['actions']['cn' if lang == '中文' else 'en'])
    if diagnosis:
        st.markdown(f"### {'📋 行动清单' if lang == '中文' else '📋 Actions'}")
        im = {'ranking': '关键词排名' if lang == '中文' else 'Ranking', 'diversity': '多样性' if lang == '中文' else 'Diversity', 'trend': '流量趋势' if lang == '中文' else 'Trend', 'stability': '稳定性' if lang == '中文' else 'Stability', 'ctr': 'CTR' if lang == '中文' else 'CTR', 'page_activity': '页面活跃' if lang == '中文' else 'Activity', 'device': '设备' if lang == '中文' else 'Device', 'region': '地区' if lang == '中文' else 'Region', 'concentration': '集中度' if lang == '中文' else 'Concentration', 'content': '内容' if lang == '中文' else 'Content'}
        for rec in diagnosis:
            p = 'P0' if rec['level'] == 'urgent' else 'P1'
            cl = '#dc2626' if rec['level'] == 'urgent' else '#d97706'
            bg = '#fef2f2' if rec['level'] == 'urgent' else '#fffbeb'
            nm = im.get(rec['key'], rec['key'])
            st.markdown(f'<div style="border-left:4px solid {cl};padding:1rem 1.5rem;margin:0.8rem 0;background:{bg};border-radius:0 8px 8px 0;"><div style="display:flex;justify-content:space-between;"><span style="font-weight:700;color:{cl};">{p} · {nm}</span><span style="color:#6b7280;">{rec["score"]:.1f}/100 | {rec["weight"]}%</span></div><div style="margin-top:0.5rem;font-weight:600;">⚠️ {rec["issue"]}</div><div style="margin-top:0.3rem;color:#4b5563;">💡 {rec["action"]}</div></div>', unsafe_allow_html=True)
    else:
        st.success("🎉 全部健康！" if lang == '中文' else "🎉 All healthy!")
    st.markdown("---")
    st.markdown(f"### {'📈 提升路径' if lang == '中文' else '📈 Path'}")
    indicators = score_result['indicators']
    imps = []
    for k, w in WEIGHTS.items():
        cur = indicators[k]
        if cur < 60:
            imps.append({'n': k, 'c': cur, 'g': (60 - cur) * w / 100, 'w': w})
    imps.sort(key=lambda x: x['g'], reverse=True)
    tp = sum(i['g'] for i in imps)
    cs = score_result['final_score']
    st.markdown(f'<div style="background:#eff6ff;padding:1.5rem;border-radius:12px;"><span style="font-size:1.1rem;font-weight:600;color:#1a56db;">{"当前" if lang == "中文" else "Now"}: {cs} → {"目标(全达60)" if lang == "中文" else "Target(all 60)"}: {cs + tp:.1f} (+{tp:.1f})</span></div>', unsafe_allow_html=True)
    im2 = {'ranking': '排名' if lang == '中文' else 'Rank', 'diversity': '多样性' if lang == '中文' else 'Div', 'trend': '趋势' if lang == '中文' else 'Trend', 'stability': '稳定' if lang == '中文' else 'Stab', 'ctr': 'CTR', 'page_activity': '活跃' if lang == '中文' else 'Act', 'device': '设备' if lang == '中文' else 'Dev', 'region': '地区' if lang == '中文' else 'Reg', 'concentration': '集中' if lang == '中文' else 'Conc', 'content': '内容' if lang == '中文' else 'Cont'}
    if imps:
        st.markdown('<div class="chart-grow">', unsafe_allow_html=True)
        fi = go.Figure(go.Bar(x=[i['g'] for i in imps], y=[f"{im2.get(i['n'],i['n'])}({i['c']:.0f}->60)" for i in imps], orientation='h', marker_color='#1a56db', text=[f"+{i['g']:.1f}" for i in imps], textposition='outside'))
        fi.update_layout(height=max(300, len(imps) * 50), xaxis=dict(title='Gain'), yaxis=dict(autorange='reversed'), margin=dict(l=180, r=60, t=20, b=40), plot_bgcolor='#fff', paper_bgcolor='#fff')
        st.plotly_chart(fi, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 外链权威维度已预留，待接入Ahrefs/Moz API后扩展。" if lang == '中文' else "💡 Backlink reserved for API integration.")



