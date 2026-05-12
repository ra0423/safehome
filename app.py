import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 SQL 분석 포털", layout="wide")

# 2. 모든 스타일 통합 (NameError 방지)
main_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; background-color: #f4f7f9; }
    .main-header { background-color: #002d56; padding: 40px; color: white; text-align: center; border-bottom: 8px solid #af8a2c; margin-bottom: 30px; border-radius: 10px; }
    .section-container { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 40px; }
    .insight-box { background-color: #ebf3fb; padding: 20px; border-radius: 10px; border-left: 8px solid #002d56; color: #002d56; line-height: 1.7; margin-top: 15px; }
    .sql-code { background-color: #262730; color: #39FF14; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.85rem; overflow-x: auto; }
</style>
"""
st.markdown(main_style, unsafe_allow_html=True)

# 3. 데이터 로드 및 SQL 변환 (데이터 비어있음 해결)
@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    try:
        # 파일 읽기
        cctv_df = pd.read_csv('cctv_data.csv')
        bus_df = pd.read_csv('bus_data.csv')
        crime_df = pd.read_csv('crime_data.csv')

        # [핵심] 컬럼명이 무엇이든 0번째 열은 GU, 1번째 열은 VALUE로 표준화
        pd.DataFrame({'GU': cctv_df.iloc[:, 0], 'CCTV_CNT': cctv_df.iloc[:, 1]}).to_sql('CCTV_TABLE', conn, index=False, if_exists='replace')
        pd.DataFrame({'GU': bus_df.iloc[:, 0], 'BUS_CNT': bus_df.iloc[:, 1]}).to_sql('BUS_TABLE', conn, index=False, if_exists='replace')
        pd.DataFrame({'GU': crime_df.iloc[:, 0], 'CRIME_CNT': crime_df.iloc[:, 1]}).to_sql('CRIME_TABLE', conn, index=False, if_exists='replace')
        return conn
    except Exception as e:
        st.error(f"데이터 파일 오류: {e}")
        return None

conn = init_db()

# --- 화면 구성 ---
st.markdown('<div class="main-header"><h1>🏛️ 서울시 공공데이터 안심 포털</h1><p>데이터 기반 치안 및 교통 통합 지표 분석</p></div>', unsafe_allow_html=True)

if conn:
    # 01. 교통 편리성 vs 치안
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🚌 01. 교통 편리성과 범죄 발생의 상관관계")
    q1 = "SELECT B.GU, B.BUS_CNT, C.TOTAL FROM BUS_TABLE B JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON B.GU = C.GU"
    df1 = pd.read_sql(q1, conn)
    
    col1, col2 = st.columns([1.8, 1])
    with col1:
        fig1 = px.scatter(df1, x='BUS_CNT', y='TOTAL', hover_name='GU', trendline="ols", height=400, labels={'BUS_CNT':'정류소 수', 'TOTAL':'범죄 건수'})
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.markdown('<div class="sql-code">' + q1 + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 유동인구가 집중되는 교통 요충지는 생활 편의성이 높으나 범죄 발생 가능성도 비례하여 증가하므로 집중적인 치안 관리가 필요합니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 02. CCTV vs 치안
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📸 02. 방범 인프라(CCTV)의 범죄 예방 효과")
    q2 = "SELECT V.GU, V.CCTV_CNT, C.TOTAL FROM CCTV_TABLE V JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON V.GU = C.GU"
    df2 = pd.read_sql(q2, conn)
    
    col3, col4 = st.columns([1.8, 1])
    with col3:
        fig2 = px.scatter(df2, x='CCTV_CNT', y='TOTAL', hover_name='GU', height=400, labels={'CCTV_CNT':'CCTV 설치 수', 'TOTAL':'범죄 건수'})
        fig2.update_traces(marker=dict(size=12, color='#e63946'))
        st.plotly_chart(fig2, use_container_width=True)
    with col4:
        st.markdown('<div class="sql-code">' + q2 + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> CCTV 설치는 범죄 발생률이 높은 지역의 사후 대응 및 예방을 위해 행정력이 우선 배치된 결과로 해석할 수 있습니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 03. 종합 상관관계 (Heatmap)
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📊 03. 종합 분석 결과 및 주거 가이드")
    q3 = "SELECT V.CCTV_CNT AS CCTV, B.BUS_CNT AS BUS, C.TOTAL AS CRIME FROM CCTV_TABLE V JOIN BUS_TABLE B ON V.GU = B.GU JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON V.GU = C.GU"
    df3 = pd.read_sql(q3, conn)
    
    col5, col6 = st.columns([1.2, 1])
    with col5:
        corr = df3.corr()
        fig3 = go.Figure(data=go.Heatmap(z=corr.values, x=['CCTV', '버스', '범죄'], y=['CCTV', '버스', '범죄'], colorscale='RdBu_r'))
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, use_container_width=True)
    with col6:
        st.markdown('<div class="insight-box" style="margin-top:0;"><b>🏛️ 분석 결과 및 주거 가이드</b><br>종합 분석 결과, CCTV와 범죄 발생 간의 상관관계는 유의미하게 높았으나, 교통과 CCTV 간의 상관관계는 다소 낮게 나타났습니다. 이는 유동인구가 많은 지역에 항상 충분한 CCTV가 비례하여 설치되어 있지는 않다는 점을 시사합니다. 안전한 주거를 위해서는 교통 편리성과 방범 인프라를 별개의 기준으로 교차 검증하는 안목이 필요합니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("⚠️ 데이터 파일을 로드할 수 없습니다. 깃허브에 cctv_data.csv, bus_data.csv, crime_data.csv 파일이 있는지 확인해 주세요.")
