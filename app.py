import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 종합 대시보드", layout="wide")

# 2. 스타일 설정
final_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    .main-header {
        background-color: #002d56; padding: 40px; color: white; text-align: center; 
        border-bottom: 8px solid #af8a2c; margin-bottom: 50px;
    }
    
    .section-title {
        border-left: 8px solid #af8a2c; padding-left: 15px; 
        margin: 60px 0 30px 0; font-size: 2rem; font-weight: 700; color: #002d56;
    }

    .insight-box {
        background-color: #f8f9fa; padding: 25px; border-radius: 12px;
        border: 1px solid #dee2e6; border-left: 10px solid #002d56; 
        margin-bottom: 20px; font-size: 1.1rem; line-height: 1.6;
    }
    
    .sql-box {
        background-color: #262730; color: #f0f2f6; padding: 15px; border-radius: 8px;
        font-family: 'Courier New', Courier, monospace; font-size: 0.9rem; margin-bottom: 40px;
    }
    
    .chart-container {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
</style>
"""
st.markdown(final_style, unsafe_allow_html=True)

# 3. 데이터 로딩
@st.cache_data
def load_data():
    try:
        df_cctv = pd.read_csv('cctv_data.csv') 
        df_bus = pd.read_csv('bus_data.csv')
        df_crime = pd.read_csv('crime_data.csv')
        
        crime_sum = df_crime.groupby('자치구')['건수'].sum().reset_index()
        # 실제 컬럼명 반영: 'CCTV 개수', '버스 정류소 개수'
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, crime_sum, on='자치구')
        df.columns = ['자치구', 'CCTV_Count', 'Bus_Count', 'Crime_Count']
        return df
    except Exception as e:
        return None

df = load_data()

# --- 화면 구성 ---

# [HEADER]
st.markdown('<div class="main-header"><h1>서울시 치안/교통 종합 분석 대시보드</h1><p>공공데이터를 활용한 자치구별 정밀 분석 결과</p></div>', unsafe_allow_html=True)

if df is not None:
    # [SECTION 1: 교통과 치안]
    st.markdown('<div class="section-title">01. 교통 편리성 vs 범죄 발생</div>', unsafe_allow_html=True)
    
    col1_1, col1_2 = st.columns([2, 1])
    with col1_1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig1 = px.scatter(df, x='Bus_Count', y='Crime_Count', hover_name='자치구', trendline="ols", height=500,
                          labels={'Bus_Count': '버스 정류소 수', 'Crime_Count': '범죄 발생 건수'})
        fig1.update_layout(plot_bgcolor="#fdfdfd")
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col1_2:
        st.markdown(f"""
        <div class="insight-box">
            <b>🏛️ 교통-치안 가이드</b><br>
            종합 분석 결과, 유동인구가 많은 교통 밀집 지역일수록 범죄 발생 건수와의 상관관계가 포착되었습니다. 
            편리한 교통 환경은 주거의 큰 장점이지만, 안전을 위해서는 정류소 인근의 방범 순찰 강도가 높은 지역을 우선 고려하는 것이 좋습니다.
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 **데이터 추출 SQL**")
        st.code(f"""
SELECT 
    B.자치구, 
    B."버스 정류소 개수", 
    C.Crime_Sum
FROM bus_data B
JOIN (
    SELECT 자치구, SUM(건수) AS Crime_Sum 
    FROM crime_data GROUP BY 자치구
) C ON B.자치구 = C.자치구;
        """, language="sql")

    # [SECTION 2: CCTV와 치안]
    st.markdown('<div class="section-title">02. 방범 인프라(CCTV) vs 범죄 발생</div>', unsafe_allow_html=True)
    
    col2_1, col2_2 = st.columns([2, 1])
    with col2_1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig2 = px.scatter(df, x='CCTV_Count', y='Crime_Count', hover_name='자치구', height=500,
                          labels={'CCTV_Count': 'CCTV 설치 대수', 'Crime_Count': '범죄 발생 건수'})
        fig2.update_traces(marker=dict(size=15, color='#e63946', line=dict(width=1, color='white')))
        fig2.update_layout(plot_bgcolor="#fdfdfd")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2_2:
        st.markdown(f"""
        <div class="insight-box">
            <b>🏛️ 방범 인프라 가이드</b><br>
            CCTV 설치 대수는 범죄 발생과 유의미한 상관관계를 보입니다. 이는 치안 수요가 높은 곳에 인프라가 집중되고 있음을 의미합니다. 
            주거지 선택 시, 단순 설치 대수뿐 아니라 자치구별 '면적 대비 CCTV 밀도'를 함께 살피는 안목이 필요합니다.
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 **데이터 추출 SQL**")
        st.code(f"""
SELECT 
    V.자치구, 
    V."CCTV 개수", 
    C.Crime_Sum
FROM cctv_data V
JOIN (
    SELECT 자치구, SUM(건수) AS Crime_Sum 
    FROM crime_data GROUP BY 자치구
) C ON V.자치구 = C.자치구;
        """, language="sql")

    # [SECTION 3: 종합 상관도]
    st.markdown('<div class="section-title">03. 지표 간 종합 상관관계</div>', unsafe_allow_html=True)
    
    col3_1, col3_2 = st.columns([2, 1])
    with col3_1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        corr = df[['CCTV_Count', 'Bus_Count', 'Crime_Count']].corr()
        fig3 = go.Figure(data=go.Heatmap(
            z=corr.values, 
            x=['CCTV', '교통(Bus)', '범죄(Crime)'], 
            y=['CCTV', '교통(Bus)', '범죄(Crime)'], 
            colorscale='RdBu_r', zmin=-1, zmax=1))
        fig3.update_layout(height=450)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3_2:
        st.markdown(f"""
        <div class="insight-box">
            <b>🏛️ 종합 분석 결론</b><br>
            CCTV와 범죄 간의 상관관계에 비해 교통과 CCTV 간의 상관관계는 다소 낮게 나타났습니다. 
            이는 교통 요충지에 항상 비례하는 방범 시설이 갖춰진 것은 아님을 시사합니다. 
            따라서 <b>'교통 편리성'</b>과 <b>'방범 인프라'</b>를 독립적인 기준으로 교차 검증하는 것이 좋습니다.
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 **통합 분석 SQL**")
        st.code(f"""
SELECT 
    V.자치구, 
    V."CCTV 개수", 
    B."버스 정류소 개수", 
    C.Crime_Sum
FROM cctv_data V
JOIN bus_data B ON V.자치구 = B.자치구
JOIN (
    SELECT 자치구, SUM(건수) AS Crime_Sum 
    FROM crime_data GROUP BY 자치구
) C ON V.자치구 = C.자치구;
        """, language="sql")

else:
    st.error("데이터 파일을 불러올 수 없습니다. 파일명이 'cctv_data.csv', 'bus_data.csv', 'crime_data.csv'인지 확인해주세요.")
