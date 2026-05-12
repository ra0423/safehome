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
    .main-header { background-color: #002d56; padding: 50px; color: white; text-align: center; border-bottom: 8px solid #af8a2c; margin-bottom: 40px; }
    .section-container { background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 50px; }
    .sql-box { background-color: #262730; color: #39FF14; padding: 20px; border-radius: 10px; font-family: 'Courier New', monospace; margin: 15px 0; font-size: 0.95rem; border-left: 5px solid #af8a2c; }
    .insight-box { background-color: #ebf3fb; padding: 20px; border-radius: 10px; border-left: 8px solid #002d56; color: #002d56; line-height: 1.7; }
    .tag { display: inline-block; background: #af8a2c; color: white; padding: 2px 10px; border-radius: 5px; font-size: 0.8rem; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. SQLite DB 초기화 및 데이터 로드 안정화
@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    try:
        # 데이터 로드 및 컬럼명 강제 표준화 (SQL 에러 방지)
        df_cctv_raw = pd.read_csv('cctv_data.csv')
        df_bus_raw = pd.read_csv('bus_data.csv')
        df_crime_raw = pd.read_csv('crime_data.csv')

        # SQL 쿼리에서 오류가 나지 않도록 컬럼명을 영어로 고정하여 테이블 생성
        # CCTV: [자치구, CCTV대수] -> [GU, CCTV_CNT]
        df_cctv = pd.DataFrame({'GU': df_cctv_raw.iloc[:, 0], 'CCTV_CNT': df_cctv_raw.iloc[:, 1]})
        
        # BUS: [자치구, 정류소수] -> [GU, BUS_CNT]
        df_bus = pd.DataFrame({'GU': df_bus_raw.iloc[:, 0], 'BUS_CNT': df_bus_raw.iloc[:, 1]})
        
        # CRIME: [자치구, 건수] -> [GU, CRIME_CNT]
        df_crime = pd.DataFrame({'GU': df_crime_raw.iloc[:, 0], 'CRIME_CNT': df_crime_raw.iloc[:, 1]})

        df_cctv.to_sql('CCTV_TABLE', conn, index=False, if_exists='replace')
        df_bus.to_sql('BUS_TABLE', conn, index=False, if_exists='replace')
        df_crime.to_sql('CRIME_TABLE', conn, index=False, if_exists='replace')
        
        return conn
    except Exception as e:
        st.error(f"데이터 로드 에러: {e}")
        return None

conn = init_db()

st.markdown('<div class="main-header"><h1>서울시 치안/교통 SQL 인사이트 포털</h1><p>정밀 SQL 쿼리 기반 데이터 분석</p></div>', unsafe_allow_html=True)

if conn:
    # --- SECTION 1 ---
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📊 01. 교통 편리성과 범죄 발생의 상관관계")
    
    query1 = "SELECT B.GU, B.BUS_CNT, C.CRIME_TOTAL FROM BUS_TABLE B JOIN (SELECT GU, SUM(CRIME_CNT) AS CRIME_TOTAL FROM CRIME_TABLE GROUP BY GU) C ON B.GU = C.GU"
    df1 = pd.read_sql(query1, conn)
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        fig1 = px.scatter(df1, x='BUS_CNT', y='CRIME_TOTAL', hover_name='GU', trendline="ols", height=450, labels={'BUS_CNT':'정류소 수', 'CRIME_TOTAL':'범죄 건수'})
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.markdown('<span class="tag">SQL QUERY</span>', unsafe_allow_html=True)
        st.code(query1, language='sql')
        st.markdown('<div class="insight-box">유동인구가 많은 교통 요충지는 생활 편의성이 높으나 범죄 빈도도 높은 경향이 있습니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SECTION 2 ---
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📹 02. 방범 인프라(CCTV)의 범죄 예방 분석")
    
    query2 = "SELECT V.GU, V.CCTV_CNT, C.CRIME_TOTAL FROM CCTV_TABLE V JOIN (SELECT GU, SUM(CRIME_CNT) AS CRIME_TOTAL FROM CRIME_TABLE GROUP BY GU) C ON V.GU = C.GU"
    df2 = pd.read_sql(query2, conn)
    
    col3, col4 = st.columns([1.5, 1])
    with col3:
        fig2 = px.scatter(df2, x='CCTV_CNT', y='CRIME_TOTAL', hover_name='GU', height=450, labels={'CCTV_CNT':'CCTV 수', 'CRIME_TOTAL':'범죄 건수'})
        fig2.update_traces(marker=dict(size=15, color='#e63946'))
        st.plotly_chart(fig2, use_container_width=True)
    with col4:
        st.markdown('<span class="tag">SQL QUERY</span>', unsafe_allow_html=True)
        st.code(query2, language='sql')
        st.markdown('<div class="insight-box">치안 수요가 높은 자치구일수록 행정력이 집중되어 CCTV 설치 대수가 많은 추세를 보입니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SECTION 3 ---
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📈 03. 지표 간 종합 상관관계")
    
    query3 = "SELECT V.CCTV_CNT AS CCTV, B.BUS_CNT AS BUS, C.CRIME_TOTAL AS CRIME FROM CCTV_TABLE V JOIN BUS_TABLE B ON V.GU = B.GU JOIN (SELECT GU, SUM(CRIME_CNT) AS CRIME_TOTAL FROM CRIME_TABLE GROUP BY GU) C ON V.GU = C.GU"
    df3 = pd.read_sql(query3, conn)
    
    col5, col6 = st.columns([1.5, 1])
    with col5:
        corr = df3.corr()
        fig3 = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale='RdBu_r'))
        st.plotly_chart(fig3, use_container_width=True)
    with col6:
        st.markdown('<span class="tag">SQL QUERY</span>', unsafe_allow_html=True)
        st.code(query3, language='sql')
        st.markdown('<div class="insight-box">각 지표 간의 상관관계를 통해 종합적인 주거 안전도를 판단할 수 있습니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
