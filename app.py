import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 SQL 분석 대시보드", layout="wide")

# 2. 스타일링 (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #f4f7f9; }
    
    .main-header {
        background-color: #002d56; padding: 50px; color: white; text-align: center; 
        border-bottom: 8px solid #af8a2c; margin-bottom: 40px;
    }
    .section-container {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 50px;
    }
    .sql-box {
        background-color: #262730; color: #39FF14; padding: 20px; 
        border-radius: 10px; font-family: 'Courier New', monospace; margin: 15px 0;
        font-size: 0.95rem; border-left: 5px solid #af8a2c;
    }
    .insight-box {
        background-color: #ebf3fb; padding: 20px; border-radius: 10px;
        border-left: 8px solid #002d56; color: #002d56; line-height: 1.7;
    }
    .tag {
        display: inline-block; background: #af8a2c; color: white; 
        padding: 2px 10px; border-radius: 5px; font-size: 0.8rem; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. SQLite DB 초기화 (정확한 파일명 반영)
@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    try:
        # 요청하신 정확한 파일명으로 로드합니다.
        df_cctv = pd.read_csv('cctv_data.csv')
        df_bus = pd.read_csv('bus_data.csv')
        df_crime = pd.read_csv('crime_data.csv')
        
        # SQL 테이블 생성
        df_cctv.to_sql('CCTV_TABLE', conn, index=False)
        df_bus.to_sql('BUS_TABLE', conn, index=False)
        df_crime.to_sql('CRIME_TABLE', conn, index=False)
        return conn
    except Exception as e:
        st.error(f"데이터 파일 로드 실패: {e}")
        st.info("팁: GitHub에 cctv_data.csv, bus_data.csv, crime_data.csv 파일이 있는지 확인해 주세요.")
        return None

conn = init_db()

# --- 대시보드 본문 ---
st.markdown('<div class="main-header"><h1>서울시 치안/교통 SQL 인사이트 포털</h1><p>정밀한 SQL 쿼리를 통한 데이터 기반 주거 안전 분석</p></div>', unsafe_allow_html=True)

if conn:
    # --- SECTION 1: 교통과 치안 ---
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📊 01. 교통 편리성과 범죄 발생의 상관관계")
    
    query1 = """
SELECT B.자치구, B.정류소수 AS Bus_Count, C.범죄합계 AS Crime_Count
FROM BUS_TABLE B
JOIN (
    SELECT 자치구, SUM(건수) AS 범죄합계 
    FROM CRIME_TABLE 
    GROUP BY 자치구
) C ON B.자치구 = C.자치구;"""
    
    df1 = pd.read_sql(query1, conn)
    col1, col2 = st.columns([1.5, 1])
    with col1:
        fig1 = px.scatter(df1, x='Bus_Count', y='Crime_Count', hover_name='자치구', trendline="ols", height=450)
        fig1.update_layout(plot_bgcolor="#f8f9fa")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.markdown('<span class="tag">SQL QUERY</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="sql-box">{query1}</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b>💡 분석 결과:</b> 유동인구가 많은 교통 요충지는 생활 편의성이 높으나 범죄 발생 빈도도 높은 경향이 있습니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SECTION 2: CCTV와 치안 ---
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📹 02. 방범 인프라(CCTV)의 범죄 예방 분석")
    
    query2 = """
SELECT V.자치구, V.CCTV대수 AS CCTV_Count, C.범죄합계 AS Crime_Count
FROM CCTV_TABLE V
JOIN (
    SELECT 자치구, SUM(건수) AS 범죄합계 
    FROM CRIME_TABLE 
    GROUP BY 자치구
) C ON V.자치구 = C.자치구;"""
    
    df2 = pd.read_sql(query2, conn)
    col3, col4 = st.columns([1.5, 1])
    with col3:
        fig2 = px.scatter(df2, x='CCTV_Count', y='Crime_Count', hover_name='자치구', height=450)
        fig2.update_layout(plot_bgcolor="#f8f9fa")
        fig2.update_traces(marker=dict(size=15, color='#e63946'))
        st.plotly_chart(fig2, use_container_width=True)
    with col4:
        st.markdown('<span class="tag">SQL QUERY</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="sql-box">{query2}</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b>💡 분석 결과:</b> 치안 수요가 높은 자치구일수록 행정력이 집중되어 CCTV 설치 대수가 많은 추세를 보입니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SECTION 3: 종합 상관도 ---
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📈 03. 지표 간 종합 상관관계 (3-Way JOIN)")
    
    query3 = """
SELECT V.CCTV대수 AS CCTV, B.정류소수 AS Bus, C.범죄합계 AS Crime
FROM CCTV_TABLE V
JOIN BUS_TABLE B ON V.자치구 = B.자치구
JOIN (
    SELECT 자치구, SUM(건수) AS 범죄합계 
    FROM CRIME_TABLE 
    GROUP BY 자치구
) C ON V.자치구 = C.자치구;"""
    
    df3 = pd.read_sql(query3, conn)
    col5, col6 = st.columns([1.5, 1])
    with col5:
        corr = df3.corr
