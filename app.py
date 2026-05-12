import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 SQL 분석 대시보드", layout="wide")

# 2. 스타일링 (안전한 문자열 처리)
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

# 3. 데이터베이스 초기화 (컬럼명 자동 매칭)
@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    try:
        # 파일 로드 (파일명: cctv_data.csv, bus_data.csv, crime_data.csv)
        cctv = pd.read_csv('cctv_data.csv')
        bus = pd.read_csv('bus_data.csv')
        crime = pd.read_csv('crime_data.csv')

        # 컬럼 이름이 한글일 경우를 대비해 첫 번째 열을 GU, 두 번째 열을 VALUE로 표준화하여 테이블 생성
        pd.DataFrame({'GU': cctv.iloc[:, 0], 'CCTV_CNT': cctv.iloc[:, 1]}).to_sql('CCTV_TABLE', conn, index=False, if_exists='replace')
        pd.DataFrame({'GU': bus.iloc[:, 0], 'BUS_CNT': bus.iloc[:, 1]}).to_sql('BUS_TABLE', conn, index=False, if_exists='replace')
        pd.DataFrame({'GU': crime.iloc[:, 0], 'CRIME_CNT': crime.iloc[:, 1]}).to_sql('CRIME_TABLE', conn, index=False, if_exists='replace')
        return conn
    except Exception as e:
        st.error(f"데이터 파일 로드 실패: {e}")
        return None

conn = init_db()

# --- 대시보드 시작 ---
st.markdown('<div class="main-header"><h1>서울시 치안/교통 SQL 인사이트 포털</h1><p>데이터 유실 방지 및 구문 오류 수정 완료 버전</p></div>', unsafe_allow_html=True)

if conn:
    # 01. 교통 편리성 분석
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📊 01. 교통 편리성과 범죄 발생의 상관관계")
    q1 = "SELECT B.GU, B.BUS_CNT, C.TOTAL FROM BUS_TABLE B JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON B.GU = C.GU"
    df1 = pd.read_sql(q1, conn)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if not df1.empty:
            fig1 = px.scatter(df1, x='BUS_CNT', y='TOTAL', hover_name='GU', trendline="ols", height=450, labels={'BUS_CNT':'정류소 수', 'TOTAL':'범죄 건수'})
            st.plotly_chart(fig1, use_container_width=True)
        else: st.warning("데이터가 비어있습니다.")
    with col2:
        st.code(q1, language='sql')
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 유동인구가 많은 교통 밀집 지역은 치안 관리가 더 집중되어야 함을 보여줍니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 02. CCTV 분석
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📹 02. 방범 인프라(CCTV)의 범죄 예방 효과")
    q2 = "SELECT V.GU, V.CCTV_CNT, C.TOTAL FROM CCTV_TABLE V JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON V.GU = C.GU"
    df2 = pd.read_sql(q2, conn)
    
    col3, col4 = st.columns([2, 1])
    with col3:
        if not df2.empty:
            fig2 = px.scatter(df2, x='CCTV_CNT', y='TOTAL', hover_name='GU', height=450, labels={'CCTV_CNT':'CCTV 수', 'TOTAL':'범죄 건수'})
            fig2.update_traces(marker=dict(size=15, color='#e63946'))
            st.plotly_chart(fig2, use_container_width=True)
        else: st.warning("데이터가 비어있습니다.")
    with col4:
        st.code(q2, language='sql')
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> CCTV 설치 대수는 범죄 발생이 빈번한 지역의 보완 지표로 활용됩니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 03. 종합 상관도
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📈 03. 지표 간 종합 상관관계")
    q3 = "SELECT V.CCTV_CNT AS CCTV, B.BUS_CNT AS BUS, C.TOTAL AS CRIME FROM CCTV_TABLE V JOIN BUS_TABLE B ON V.GU = B.GU JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON V.GU = C.GU"
    df3 = pd.read_sql(q3, conn)
    
    col5, col6 = st.columns([2, 1])
    with col5:
        if not df3.empty:
            corr = df3.corr()
            fig3 = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale='RdBu_r'))
            st.plotly_chart(fig3, use_container_width=True)
    with col6:
        st.code(q3, language='sql')
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 세 지표의 상관계수를 통해 자치구별 안전 인프라 효율성을 진단합니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("데이터베이스 연결에 실패했습니다. CSV 파일명을 확인하세요.")
