import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 SQL 분석 포털", layout="wide")

# 2. 스타일
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

# 3. CSV 읽기 헬퍼 — 인코딩 자동 시도
def read_csv_safe(path):
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            df = pd.read_csv(path, encoding=enc)
            return df
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return None

# 4. DB 초기화 — 세션 상태로 관리하여 재실행 시 데이터 유지
@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    
    cctv_df  = read_csv_safe('cctv_data.csv')
    bus_df   = read_csv_safe('bus_data.csv')
    crime_df = read_csv_safe('crime_data.csv')

    missing = [name for name, df in [('cctv_data.csv', cctv_df), ('bus_data.csv', bus_df), ('crime_data.csv', crime_df)] if df is None]
    if missing:
        st.error(f"파일을 읽을 수 없습니다: {missing}")
        return None

    # [핵심 수정] GU 컬럼 공백 제거 + 표준 컬럼명으로 정규화
    def normalize(df, value_col):
        result = pd.DataFrame({
            'GU': df.iloc[:, 0].astype(str).str.strip(),
            value_col: pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0)
        })
        return result

    normalize(cctv_df,  'CCTV_CNT').to_sql('CCTV_TABLE',  conn, index=False, if_exists='replace')
    normalize(bus_df,   'BUS_CNT') .to_sql('BUS_TABLE',   conn, index=False, if_exists='replace')
    normalize(crime_df, 'CRIME_CNT').to_sql('CRIME_TABLE', conn, index=False, if_exists='replace')

    return conn

conn = init_db()

# --- 화면 구성 ---
st.markdown('<div class="main-header"><h1>🏛️ 서울시 공공데이터 안심 포털</h1><p>데이터 기반 치안 및 교통 통합 지표 분석</p></div>', unsafe_allow_html=True)

if conn:
    # [디버그용] 데이터 로드 확인 — 정상 동작 후 주석 처리 가능
    with st.expander("🔍 데이터 로드 확인 (디버그)"):
        for tbl in ['BUS_TABLE', 'CCTV_TABLE', 'CRIME_TABLE']:
            df_check = pd.read_sql(f"SELECT * FROM {tbl} LIMIT 3", conn)
            st.write(f"**{tbl}** ({len(pd.read_sql(f'SELECT * FROM {tbl}', conn))}행)", df_check)

    # 01. 교통 편리성 vs 치안
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🚌 01. 교통 편리성과 범죄 발생의 상관관계")
    q1 = "SELECT B.GU, B.BUS_CNT, C.TOTAL FROM BUS_TABLE B JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON TRIM(B.GU) = TRIM(C.GU)"
    df1 = pd.read_sql(q1, conn)
    
    col1, col2 = st.columns([1.8, 1])
    with col1:
        if df1.empty:
            st.warning("⚠️ 조회 결과가 없습니다. GU 컬럼 값이 테이블 간 일치하는지 확인하세요.")
        else:
            fig1 = px.scatter(df1, x='BUS_CNT', y='TOTAL', hover_name='GU', trendline="ols",
                              height=400, labels={'BUS_CNT':'정류소 수', 'TOTAL':'범죄 건수'})
            st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.markdown('<div class="sql-code">' + q1 + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 유동인구가 집중되는 교통 요충지는 생활 편의성이 높으나 범죄 발생 가능성도 비례하여 증가하므로 집중적인 치안 관리가 필요합니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 02. CCTV vs 치안
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📸 02. 방범 인프라(CCTV)의 범죄 예방 효과")
    q2 = "SELECT V.GU, V.CCTV_CNT, C.TOTAL FROM CCTV_TABLE V JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON TRIM(V.GU) = TRIM(C.GU)"
    df2 = pd.read_sql(q2, conn)
    
    col3, col4 = st.columns([1.8, 1])
    with col3:
        if df2.empty:
            st.warning("⚠️ 조회 결과가 없습니다.")
        else:
            fig2 = px.scatter(df2, x='CCTV_CNT', y='TOTAL', hover_name='GU', height=400,
                              labels={'CCTV_CNT':'CCTV 설치 수', 'TOTAL':'범죄 건수'})
            fig2.update_traces(marker=dict(size=12, color='#e63946'))
            st.plotly_chart(fig2, use_container_width=True)
    with col4:
        st.markdown('<div class="sql-code">' + q2 + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> CCTV 설치는 범죄 발생률이 높은 지역의 사후 대응 및 예방을 위해 행정력이 우선 배치된 결과로 해석할 수 있습니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 03. 종합 상관관계 (Heatmap)
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📊 03. 종합 분석 결과 및 주거 가이드")
    q3 = "SELECT V.CCTV_CNT AS CCTV, B.BUS_CNT AS BUS, C.TOTAL AS CRIME FROM CCTV_TABLE V JOIN BUS_TABLE B ON TRIM(V.GU) = TRIM(B.GU) JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON TRIM(V.GU) = TRIM(C.GU)"
    df3 = pd.read_sql(q3, conn)
    
    col5, col6 = st.columns([1.2, 1])
    with col5:
        if df3.empty:
            st.warning("⚠️ 조회 결과가 없습니다.")
        else:
            corr = df3.corr()
            fig3 = go.Figure(data=go.Heatmap(
                z=corr.values, x=['CCTV', '버스', '범죄'], y=['CCTV', '버스', '범죄'], colorscale='RdBu_r'))
            fig3.update_layout(height=350)
            st.plotly_chart(fig3, use_container_width=True)
    with col6:
        st.markdown('<div class="insight-box" style="margin-top:0;"><b>🏛️ 분석 결과 및 주거 가이드</b><br>종합 분석 결과, CCTV와 범죄 발생 간의 상관관계는 유의미하게 높았으나, 교통과 CCTV 간의 상관관계는 다소 낮게 나타났습니다. 이는 유동인구가 많은 지역에 항상 충분한 CCTV가 비례하여 설치되어 있지는 않다는 점을 시사합니다. 안전한 주거를 위해서는 교통 편리성과 방범 인프라를 별개의 기준으로 교차 검증하는 안목이 필요합니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("⚠️ 데이터 파일을 로드할 수 없습니다. cctv_data.csv, bus_data.csv, crime_data.csv 파일이 있는지 확인해 주세요.")
