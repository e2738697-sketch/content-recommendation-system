#!/usr/bin/env python3
"""
Content Recommendation System Dashboard
实时数据可视化分析仪表板
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="内容推荐系统分析仪表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase配置
@st.cache_resource
def init_supabase():
    url = os.environ.get('SUPABASE_URL', st.secrets.get('SUPABASE_URL', ''))
    key = os.environ.get('SUPABASE_KEY', st.secrets.get('SUPABASE_KEY', ''))
    return create_client(url, key)

supabase = init_supabase()

# 标题
st.title("📊 内容推荐系统 - 数据分析仪表板")
st.markdown("实时查看和分析采集的内容数据")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 控制面板")
    
    # 刷新按钮
    if st.button("🔄 刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # 数据源选择
    data_source = st.selectbox(
        "数据源",
        ["全部", "小红书", "抖音"]
    )
    
    # 时间范围
    time_range = st.selectbox(
        "时间范围",
        ["最近24小时", "最近7天", "最近30天", "全部时间"]
    )
    
    st.divider()
    st.caption("最后更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 获取数据
@st.cache_data(ttl=60)
def load_content_data():
    response = supabase.table('content_raw').select('*').execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=60)
def load_profile_data():
    response = supabase.table('content_profile').select('*').execute()
    return pd.DataFrame(response.data)

try:
    df_raw = load_content_data()
    df_profile = load_profile_data()
    
    # 合并数据
    if not df_raw.empty and not df_profile.empty:
        df = pd.merge(df_raw, df_profile, left_on='id', right_on='content_id', how='left')
    else:
        df = df_raw
    
    # 数据过滤
    if data_source != "全部":
        platform_map = {"小红书": "xiaohongshu", "抖音": "douyin"}
        df = df[df['platform'] == platform_map[data_source]]
    
    # KPI指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 总内容数",
            value=len(df),
            delta=f"+{len(df[df['created_at'] > (datetime.now() - timedelta(days=1)).isoformat()])} (24h)"
        )
    
    with col2:
        xiaohongshu_count = len(df[df['platform'] == 'xiaohongshu'])
        st.metric(
            label="🎨 小红书",
            value=xiaohongshu_count
        )
    
    with col3:
        douyin_count = len(df[df['platform'] == 'douyin'])
        st.metric(
            label="🎵 抖音",
            value=douyin_count
        )
    
    with col4:
        avg_engagement = df['engagement_rate'].mean() if 'engagement_rate' in df.columns else 0
        st.metric(
            label="💡 平均互动率",
            value=f"{avg_engagement:.2%}" if avg_engagement else "N/A"
        )
    
    st.divider()
    
    # 数据可视化
    tab1, tab2, tab3, tab4 = st.tabs(["📈 趋势分析", "🏷️ 标签分布", "📊 详细数据", "🔍 内容详情"])
    
    with tab1:
        st.subheader("内容采集趋势")
        
        # 按平台统计
        if 'platform' in df.columns:
            platform_counts = df['platform'].value_counts()
            fig1 = px.pie(
                values=platform_counts.values,
                names=platform_counts.index,
                title="平台分布",
                color_discrete_map={'xiaohongshu': '#FF2442', 'douyin': '#00F0FF'}
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        # 时间趋势
        if 'created_at' in df.columns:
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            daily_counts = df.groupby('date').size().reset_index(name='count')
            fig2 = px.line(
                daily_counts,
                x='date',
                y='count',
                title="每日采集量趋势",
                markers=True
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.subheader("内容标签分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 类别分布
            if 'category' in df.columns:
                st.write("### 类别分布")
                category_data = df['category'].explode().value_counts().head(10)
                fig3 = px.bar(
                    x=category_data.values,
                    y=category_data.index,
                    orientation='h',
                    title="Top 10 类别"
                )
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # 风格分布
            if 'style' in df.columns:
                st.write("### 风格分布")
                style_counts = df['style'].value_counts()
                fig4 = px.bar(
                    x=style_counts.index,
                    y=style_counts.values,
                    title="内容风格分布"
                )
                st.plotly_chart(fig4, use_container_width=True)
        
        # 场景分布
        if 'scenario' in df.columns:
            st.write("### 使用场景分布")
            scenario_data = df['scenario'].explode().value_counts()
            fig5 = px.pie(
                values=scenario_data.values,
                names=scenario_data.index,
                title="使用场景"
            )
            st.plotly_chart(fig5, use_container_width=True)
    
    with tab3:
        st.subheader("详细数据表")
        
        # 显示列选择
        if not df.empty:
            display_cols = st.multiselect(
                "选择要显示的列",
                options=df.columns.tolist(),
                default=['id', 'platform', 'created_at', 'category', 'style'] if all(col in df.columns for col in ['id', 'platform', 'created_at']) else df.columns.tolist()[:5]
            )
            
            if display_cols:
                st.dataframe(
                    df[display_cols],
                    use_container_width=True,
                    height=400
                )
                
                # 下载按钮
                csv = df[display_cols].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 下载CSV",
                    data=csv,
                    file_name=f"content_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("暂无数据")
    
    with tab4:
        st.subheader("内容详细信息")
        
        if not df.empty:
            # 选择一条内容
            content_id = st.selectbox(
                "选择内容ID",
                options=df['id'].tolist()
            )
            
            if content_id:
                content = df[df['id'] == content_id].iloc[0]
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("### 基本信息")
                    st.write(f"**平台**: {content.get('platform', 'N/A')}")
                    st.write(f"**创建时间**: {content.get('created_at', 'N/A')}")
                    if 'category' in content:
                        st.write(f"**类别**: {content['category']}")
                    if 'style' in content:
                        st.write(f"**风格**: {content['style']}")
                    if 'sentiment_score' in content:
                        st.write(f"**情感分数**: {content['sentiment_score']}")
                
                with col2:
                    st.write("### 原始数据")
                    if 'raw_data' in content:
                        st.json(content['raw_data'])
        else:
            st.info("暂无内容数据")

except Exception as e:
    st.error(f"加载数据时出错: {str(e)}")
    st.info("请确保Supabase凭证已正确配置")

# 页脚
st.divider()
st.caption("© 2026 Content Recommendation System | Powered by Streamlit + Supabase")
