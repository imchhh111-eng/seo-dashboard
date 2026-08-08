import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="SEO 健康度诊断",
    page_icon="🔍",
    layout="wide"
)


# ==================== 数据加载 ====================
@st.cache_data
def load_data():
    """加载所有CSV数据文件"""
    base_path = "data"

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
st.sidebar.title("SEO 健康度诊断")
st.sidebar.markdown("---")
st.sidebar.subheader("导航菜单")

page = st.sidebar.radio(
    "选择分析模块",
    ["📊 总览仪表盘", "🏥 SEO 健康度评分", "📈 搜索表现趋势",
     "🌍 国家/地区分析", "📱 设备分布", "🚨 流量异常检测"],
    label_visibility="collapsed"
)

# 显示数据范围
if not data['by_date'].empty:
    min_date = data['by_date']['data_date'].min().strftime('%Y-%m-%d')
    max_date = data['by_date']['data_date'].max().strftime('%Y-%m-%d')
    st.sidebar.markdown("---")
    st.sidebar.caption(f"数据范围: {min_date} 至 {max_date}")

st.sidebar.markdown("---")
st.sidebar.caption("B2B SEO 健康度诊断工具 v1.0 | 基于 GSC 数据")

# ==================== 页面1：总览仪表盘 ====================
if page == "📊 总览仪表盘":
    st.title("B2B独立站 SEO 总览仪表盘")
    st.markdown("📊")

    if not data['by_date'].empty:
        df = data['by_date']
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总点击数", f"{df['clicks'].sum():,}")
        col2.metric("总展示次数", f"{df['impressions'].sum():,}")
        avg_ctr = df['clicks'].sum() / df['impressions'].sum() * 100 if df['impressions'].sum() > 0 else 0
        col3.metric("平均CTR", f"{avg_ctr:.2f}%")
        col4.metric("平均排名", f"{df['position'].mean():.1f}")

    st.info("请从左侧导航菜单单选择具体分析模块")

# ==================== 页面2：SEO 健康度评分 ====================
elif page == "🏥 SEO 健康度评分":
    st.title("SEO 健康度评分")

    if not data['by_date'].empty and not data['by_query'].empty:
        df_date = data['by_date']
        df_query = data['by_query']

        # --- 搜索表现维度 (40%) ---
        total_clicks = df_date['clicks'].sum()
        total_impressions = df_date['impressions'].sum()
        avg_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        avg_position = df_date['position'].mean()

        # CTR评分 (B2B行业基准: 2-3% 为良好)
        ctr_score = min(100, (avg_ctr / 3.0) * 100)

        # 排名评分 (排名越低越好，1-10为优秀)
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

        # 点击量评分 (基于日均点击)
        days_count = (df_date['data_date'].max() - df_date['data_date'].min()).days + 1
        daily_clicks = total_clicks / days_count if days_count > 0 else 0
        click_score = min(100, (daily_clicks / 10) * 100)

        search_performance_score = (ctr_score * 0.4 + position_score * 0.35 + click_score * 0.25)

        # --- 内容质量维度 (30%) ---
        # 关键词覆盖度
        unique_queries = df_query['query'].nunique() if 'query' in df_query.columns else 0
        keyword_coverage_score = min(100, (unique_queries / 100) * 100)

        # 页面覆盖度
        if not data['by_page'].empty and 'page' in data['by_page'].columns:
            unique_pages = data['by_page']['page'].nunique()
        else:
            unique_pages = 0
        page_coverage_score = min(100, (unique_pages / 20) * 100)

        # 内容深度 (基于有点击的关键词比例)
        if not df_query.empty and 'clicks' in df_query.columns:
            clicked_queries = df_query[df_query['clicks'] > 0]['query'].nunique()
            content_depth_score = min(100, (clicked_queries / max(unique_queries, 1)) * 100)
        else:
            content_depth_score = 50

        content_quality_score = (keyword_coverage_score * 0.4 + page_coverage_score * 0.3 + content_depth_score * 0.3)

        # --- 技术SEO维度 (15%) ---
        # 基于设备兼容性
        if not data['by_device'].empty:
            device_types = data['by_device']['device'].nunique()
            mobile_data = data['by_device'][data['by_device']['device'] == 'MOBILE']
            desktop_data = data['by_device'][data['by_device']['device'] == 'DESKTOP']

            if not mobile_data.empty and not desktop_data.empty:
                mobile_ctr = mobile_data['clicks'].sum() / mobile_data['impressions'].sum() * 100 if mobile_data[
                                                                                                         'impressions'].sum() > 0 else 0
                desktop_ctr = desktop_data['clicks'].sum() / desktop_data['impressions'].sum() * 100 if desktop_data[
                                                                                                            'impressions'].sum() > 0 else 0
                # 移动端和桌面端CTR差距越小越好
                ctr_gap = abs(mobile_ctr - desktop_ctr)
                device_compat_score = max(0, 100 - ctr_gap * 20)
            else:
                device_compat_score = 50
        else:
            device_compat_score = 50

        technical_seo_score = device_compat_score

        # --- 用户体验维度 (15%) ---
        # 基于CTR趋势和排名稳定性
        if len(df_date) >= 30:
            recent_30 = df_date.nlargest(30, 'data_date')
            older_30 = df_date.nsmallest(30, 'data_date')

            recent_ctr = recent_30['clicks'].sum() / recent_30['impressions'].sum() * 100 if recent_30[
                                                                                                 'impressions'].sum() > 0 else 0
            older_ctr = older_30['clicks'].sum() / older_30['impressions'].sum() * 100 if older_30[
                                                                                              'impressions'].sum() > 0 else 0

            if older_ctr > 0:
                ctr_trend = (recent_ctr - older_ctr) / older_ctr * 100
            else:
                ctr_trend = 0

            # 趋势为正则加分
            trend_score = min(100, max(0, 50 + ctr_trend * 2))
        else:
            trend_score = 50

        # 排名稳定性
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

        # 等级判定
        if total_score >= 90:
            grade, grade_text, grade_color = "A", "优秀", "green"
        elif total_score >= 70:
            grade, grade_text, grade_color = "B", "良好", "blue"
        elif total_score >= 50:
            grade, grade_text, grade_color = "C", "一般", "orange"
        else:
            grade, grade_text, grade_color = "D", "严重", "red"

        # 显示评分
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: #f0f2f6;">
                <h1 style="font-size: 72px; margin: 0; color: {grade_color};">{grade}</h1>
                <h3>{grade_text}</h3>
                <h2>{total_score:.1f} / 100</h2>
            </div>
            """, unsafe_allow_html=True)

        # 雷达图
        st.subheader("各维度得分")
        categories = ['内容质量', '技术SEO', '搜索表现', '用户体验']
        scores = [content_quality_score, technical_seo_score, search_performance_score, user_experience_score]

        fig = go.Figure(data=go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            line_color='#1f77b4'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # 详细得分
        st.subheader("详细评分明细")
        score_data = {
            "维度": ["搜索表现 (40%)", "内容质量 (30%)", "技术SEO (15%)", "用户体验 (15%)"],
            "得分": [f"{search_performance_score:.1f}", f"{content_quality_score:.1f}",
                     f"{technical_seo_score:.1f}", f"{user_experience_score:.1f}"],
            "说明": [
                f"CTR={avg_ctr:.2f}%, 平均排名={avg_position:.1f}, 日均点击={daily_clicks:.1f}",
                f"关键词覆盖={unique_queries}个, 页面覆盖={unique_pages}个",
                f"设备兼容性评分={device_compat_score:.1f}",
                f"趋势评分={trend_score:.1f}, 稳定性={stability_score:.1f}"
            ]
        }
        st.table(pd.DataFrame(score_data))

# ==================== 页面3：搜索表现趋势 ====================
elif page == "📈 搜索表现趋势":
    st.title("搜索表现趋势")
    st.subheader("点击数 & 展示次数趋势")

    if not data['by_date'].empty:
        df = data['by_date'].sort_values('data_date')

        # 日期范围选择
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("开始日期", df['data_date'].min())
        with col2:
            end_date = st.date_input("结束日期", df['data_date'].max())

        # 时间粒度选择
        granularity = st.radio("时间粒度", ["日", "周", "月"], horizontal=True)

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

        # 双轴图
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=df_agg['data_date'], y=df_agg['impressions'], name="展示次数", marker_color='#4ECDC4',
                   opacity=0.7),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=df_agg['data_date'], y=df_agg['clicks'], name="点击数", line=dict(color='#FF6B6B', width=2)),
            secondary_y=True
        )
        fig.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig.update_yaxes(title_text="展示次数", secondary_y=False)
        fig.update_yaxes(title_text="点击数", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        # CTR和排名趋势
        st.subheader("CTR & 平均排名趋势")
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(
            go.Scatter(x=df_agg['data_date'], y=df_agg['ctr'] * 100 if df_agg['ctr'].max() <= 1 else df_agg['ctr'],
                       name="CTR (%)", line=dict(color='#45B7D1', width=2)),
            secondary_y=False
        )
        fig2.add_trace(
            go.Scatter(x=df_agg['data_date'], y=df_agg['position'], name="平均排名",
                       line=dict(color='#96CEB4', width=2, dash='dash')),
            secondary_y=True
        )
        fig2.update_layout(height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig2.update_yaxes(title_text="CTR (%)", secondary_y=False)
        fig2.update_yaxes(title_text="平均排名", autorange="reversed", secondary_y=True)
        st.plotly_chart(fig2, use_container_width=True)

# ==================== 页面4：国家/地区分析 ====================
elif page == "🌍 国家/地区分析":
    st.title("国家/地区分析")

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

        # Top 10 国家
        st.subheader("Top 10 流量来源国家")
        top10 = country_summary.head(10)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top10['country'], y=top10['clicks'],
            name='点击数', marker_color='#FF6B6B'
        ))
        fig.add_trace(go.Bar(
            x=top10['country'], y=top10['impressions'] / 100,
            name='展示次数 (÷100)', marker_color='#4ECDC4'
        ))
        fig.update_layout(barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)

        # 国家详细数据表
        st.subheader("各国家详细数据")
        display_df = country_summary.head(20).copy()
        display_df['ctr'] = display_df['ctr'].apply(lambda x: f"{x:.2f}%")
        display_df['position'] = display_df['position'].apply(lambda x: f"{x:.1f}")
        display_df.columns = ['国家', '点击数', '展示次数', '平均排名', 'CTR']
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # 地理分布图
        st.subheader("全球流量分布")
        fig_map = px.choropleth(
            country_summary,
            locations='country',
            color='clicks',
            hover_name='country',
            color_continuous_scale='Reds',
            title='各国点击量分布'
        )
        fig_map.update_layout(height=400)
        st.plotly_chart(fig_map, use_container_width=True)

# ==================== 页面5：设备分布 ====================
elif page == "📱 设备分布":
    st.title("设备分布分析")

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
            st.subheader("点击量占比")
            fig_pie1 = px.pie(device_summary, values='clicks', names='device',
                              color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
            fig_pie1.update_layout(height=350)
            st.plotly_chart(fig_pie1, use_container_width=True)

        with col2:
            st.subheader("展示量占比")
            fig_pie2 = px.pie(device_summary, values='impressions', names='device',
                              color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
            fig_pie2.update_layout(height=350)
            st.plotly_chart(fig_pie2, use_container_width=True)

        # 各设备CTR对比
        st.subheader("各设备 CTR & 排名对比")
        fig_device = go.Figure()
        fig_device.add_trace(go.Bar(
            x=device_summary['device'], y=device_summary['ctr'],
            name='CTR (%)', marker_color='#FF6B6B'
        ))
        fig_device.update_layout(height=350)
        st.plotly_chart(fig_device, use_container_width=True)

        # 设备趋势
        st.subheader("各设备月度趋势")
        df['month'] = df['data_date'].dt.to_period('M').apply(lambda r: r.start_time)
        device_trend = df.groupby(['month', 'device']).agg({'clicks': 'sum'}).reset_index()
        fig_trend = px.line(device_trend, x='month', y='clicks', color='device',
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        fig_trend.update_layout(height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

# ==================== 页面6：流量异常检测 ====================
elif page == "🚨 流量异常检测":
    st.title("流量异常检测")
    st.markdown("基于统计方法自动识别流量异常波动，帮助快速定位问题")

    if not data['by_date'].empty:
        df = data['by_date'].sort_values('data_date').copy()

        # ===== 参数设置 =====
        st.sidebar.markdown("---")
        st.sidebar.subheader("异常检测参数")

        detection_method = st.sidebar.selectbox(
            "检测方法",
            ["Z-Score (标准差法)", "IQR (四分位距法)", "移动平均偏离法"]
        )

        metric_choice = st.sidebar.selectbox(
            "检测指标",
            ["impressions", "clicks", "ctr", "position"],
            format_func=lambda x: {"impressions": "展示次数", "clicks": "点击数", "ctr": "CTR", "position": "平均排名"}[
                x]
        )

        if detection_method == "Z-Score (标准差法)":
            threshold = st.sidebar.slider("Z-Score 阈值", 1.0, 4.0, 2.0, 0.1,
                                          help="越小越敏感，检测到的异常越多")
        elif detection_method == "IQR (四分位距法)":
            threshold = st.sidebar.slider("IQR 倍数", 1.0, 3.0, 1.5, 0.1,
                                          help="越小越敏感，检测到的异常越多")
        else:
            window_size = st.sidebar.slider("移动窗口大小 (天)", 3, 30, 7)
            threshold = st.sidebar.slider("偏离倍数", 1.0, 4.0, 2.0, 0.1)

        # ===== 异常检测算法 =====
        metric_data = df[metric_choice].values
        dates = df['data_date'].values

        anomalies = np.zeros(len(metric_data), dtype=bool)
        anomaly_type = [''] * len(metric_data)  # 'high' or 'low'

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

        else:  # 移动平均偏离法
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

        # ===== 异常统计概览 =====
        total_anomalies = anomalies.sum()
        high_anomalies = sum(1 for t in anomaly_type if t == 'high')
        low_anomalies = sum(1 for t in anomaly_type if t == 'low')

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总数据点", f"{len(df)}")
        col2.metric("异常点数量", f"{total_anomalies}",
                    delta=f"{total_anomalies / len(df) * 100:.1f}%" if len(df) > 0 else "0%")
        col3.metric("异常高值", f"{high_anomalies}", delta="↑ 突增")
        col4.metric("异常低值", f"{low_anomalies}", delta="↓ 突降")

        # ===== 异常可视化 =====
        st.subheader("异常点可视化")

        metric_labels = {"impressions": "展示次数", "clicks": "点击数", "ctr": "CTR", "position": "平均排名"}

        fig = go.Figure()

        # 正常数据点
        normal_mask = ~df['is_anomaly']
        fig.add_trace(go.Scatter(
            x=df[normal_mask]['data_date'],
            y=df[normal_mask][metric_choice],
            mode='lines',
            name='正常数据',
            line=dict(color='#4ECDC4', width=1.5)
        ))

        # 异常高值
        high_mask = df['anomaly_type'] == 'high'
        if high_mask.any():
            fig.add_trace(go.Scatter(
                x=df[high_mask]['data_date'],
                y=df[high_mask][metric_choice],
                mode='markers',
                name='异常高值 ↑',
                marker=dict(color='red', size=10, symbol='triangle-up')
            ))

        # 异常低值
        low_mask = df['anomaly_type'] == 'low'
        if low_mask.any():
            fig.add_trace(go.Scatter(
                x=df[low_mask]['data_date'],
                y=df[low_mask][metric_choice],
                mode='markers',
                name='异常低值 ↓',
                marker=dict(color='orange', size=10, symbol='triangle-down')
            ))

        # 添加阈值线
        if detection_method == "Z-Score (标准差法)":
            mean = np.mean(metric_data)
            std = np.std(metric_data)
            fig.add_hline(y=mean + threshold * std, line_dash="dash", line_color="red",
                          annotation_text=f"上界 (μ+{threshold}σ)")
            fig.add_hline(y=mean - threshold * std, line_dash="dash", line_color="orange",
                          annotation_text=f"下界 (μ-{threshold}σ)")
            fig.add_hline(y=mean, line_dash="dot", line_color="gray", annotation_text="均值")
        elif detection_method == "IQR (四分位距法)":
            fig.add_hline(y=upper_bound, line_dash="dash", line_color="red",
                          annotation_text=f"上界 (Q3+{threshold}×IQR)")
            fig.add_hline(y=lower_bound, line_dash="dash", line_color="orange",
                          annotation_text=f"下界 (Q1-{threshold}×IQR)")

        fig.update_layout(
            title=f"{metric_labels[metric_choice]} 异常检测结果",
            xaxis_title="日期",
            yaxis_title=metric_labels[metric_choice],
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ===== 异常事件列表 =====
        st.subheader("🚨 异常事件明细")

        if total_anomalies > 0:
            anomaly_df = df[df['is_anomaly']].copy()
            anomaly_df['日期'] = anomaly_df['data_date'].dt.strftime('%Y-%m-%d')
            anomaly_df['类型'] = anomaly_df['anomaly_type'].map({'high': '🔴 异常高值', 'low': '🟡 异常低值'})
            anomaly_df['指标值'] = anomaly_df[metric_choice].apply(
                lambda x: f"{x:.2f}" if metric_choice == 'ctr' else f"{int(x)}")


            # 添加可能原因分析
            def analyze_cause(row):
                if row['anomaly_type'] == 'high':
                    if metric_choice == 'impressions':
                        return "可能原因: 内容被搜索引擎推荐/热点关键词排名提升/季节性流量高峰"
                    elif metric_choice == 'clicks':
                        return "可能原因: 标题优化效果显现/排名大幅提升/外部引流"
                    elif metric_choice == 'position':
                        return "可能原因: 排名突然下降（数值越大排名越靠后）/算法更新影响"
                    else:
                        return "可能原因: 展示量下降但点击不变/标题吸引力突然提升"
                else:
                    if metric_choice == 'impressions':
                        return "可能原因: 搜索引擎算法更新/关键词排名下降/技术问题导致页面未被索引"
                    elif metric_choice == 'clicks':
                        return "可能原因: 排名下降/竞争对手优化/搜索意图变化"
                    elif metric_choice == 'position':
                        return "可能原因: 排名突然提升（数值越小排名越靠前）/竞争对手退出"
                    else:
                        return "可能原因: 展示量大幅增加但点击未跟上/标题与搜索意图不匹配"


            anomaly_df['可能原因'] = anomaly_df.apply(analyze_cause, axis=1)

            display_cols = ['日期', '类型', '指标值', '可能原因']
            st.dataframe(
                anomaly_df[display_cols].sort_values('日期', ascending=False),
                use_container_width=True,
                hide_index=True
            )

            # ===== 异常趋势分析 =====
            st.subheader("📊 异常分布统计")

            col1, col2 = st.columns(2)

            with col1:
                # 按月统计异常数量
                anomaly_df['month'] = pd.to_datetime(anomaly_df['日期']).dt.to_period('M').astype(str)
                monthly_anomalies = anomaly_df.groupby('month').size().reset_index(name='异常数量')

                fig_monthly = px.bar(monthly_anomalies, x='month', y='异常数量',
                                     title="月度异常数量分布",
                                     color_discrete_sequence=['#FF6B6B'])
                fig_monthly.update_layout(height=300)
                st.plotly_chart(fig_monthly, use_container_width=True)

            with col2:
                # 异常类型占比
                type_counts = anomaly_df['anomaly_type'].value_counts()
                fig_type = px.pie(values=type_counts.values,
                                  names=['异常高值' if n == 'high' else '异常低值' for n in type_counts.index],
                                  title="异常类型占比",
                                  color_discrete_sequence=['#FF6B6B', '#FFA500'])
                fig_type.update_layout(height=300)
                st.plotly_chart(fig_type, use_container_width=True)

        else:
            st.success("✅ 未检测到异常数据点！当前数据表现稳定。")
            st.info("💡 提示：可以尝试降低检测阈值来发现更细微的波动。")

        # ===== 检测方法说明 =====
        with st.expander("📖 检测方法说明"):
            st.markdown("""
            ### 三种异常检测方法对比

            | 方法 | 原理 | 适用场景 | 优缺点 |
            |------|------|----------|--------|
            | **Z-Score** | 计算数据点偏离均值的标准差倍数 | 数据近似正态分布 | 简单直观，但对极端值敏感 |
            | **IQR** | 基于四分位距确定正常范围 | 数据有偏态分布 | 对极端值鲁棒，不假设分布 |
            | **移动平均** | 与近期趋势对比偏离程度 | 有明显趋势的时序数据 | 能捕捉趋势变化，但需调窗口 |

            ### 参数调节建议
            - **阈值越小** → 越敏感，检测到更多异常（可能有误报）
            - **阈值越大** → 越保守，只检测极端异常（可能漏报）
            - **B2B网站建议**: Z-Score 阈值 2.0-2.5，IQR 倍数 1.5
            """)
    else:
        st.warning("未找到日期维度数据，请检查数据文件。")

