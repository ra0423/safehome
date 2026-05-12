import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="서울시 치안/교통 SQL 분석 포털", layout="wide")

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

def read_csv_safe(path):
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            return pd.read_csv(path, encoding=enc)
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return None

# [핵심 수정] GU 값 정규화 함수 — 공백·"서울 "·"구" 제거 후 다시 "구" 통일
def normalize_gu(series):
    s = series.astype(str).str.strip()
    s = s.str.replace(r'^서울\s*', '', regex=True)   # "서울 강남구" → "강남구"
    s = s.str.replace(r'\s+', '', regex=True)        # 내부 공백 제거
    s = s.str.replace('구$', '', regex=True)         # 끝 "구" 제거 → "강남"
    s = s + '구'                                      # 다시 "구" 추가 → "강남구" 통일
    return s

@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)

    cctv_df  = read_csv_safe('cctv_data.csv')
    bus_df   = read_csv_safe('bus_data.csv')
    crime_df = read_csv_safe('crime_data.csv')

    missing = [n for n, d in [('cctv_data.csv', cctv_df), ('bus_data.csv', bus_df), ('crime_data.csv', crime_df)] if d is None]
    if missing:
        st.error(f"파일을 읽을 수 없습니다: {missing}")
        return None, None, None, None

    def build(df, val_col):
        return pd.DataFrame({
            'GU': normalize_gu(df.iloc[:, 0]),
            val_col: pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0)
        })

    cctv  = build(cctv_df,  'CCTV_CNT')
    bus   = build(bus_df,   'BUS_CNT')
    crime = build(crime_df, 'CRIME_CNT')

    cctv .to_sql('CCTV_TABLE',  conn, index=False, if_exists='replace')
    bus  .to_sql('BUS_TABLE',   conn, index=False, if_exists='replace')
    crime.to_sql('CRIME_TABLE', conn, index=False, if_exists='replace')

    return conn, cctv, bus, crime

conn, cctv, bus, crime = init_db()

st.markdown('<div class="main-header"><h1>🏛️ 서울시 공공데이터 안심 포털</h1><p>데이터 기반 치안 및 교통 통합 지표 분석</p></div>', unsafe_allow_html=True)

if conn:
    # ── 디버그: GU 값 비교 ──────────────────────────────────────────
    with st.expander("🔍 GU 값 정규화 확인 (데이터가 안 나올 때 열어보세요)"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.write("**CCTV_TABLE GU**"); st.dataframe(cctv[['GU']].head(10))
        with col_b:
            st.write("**BUS_TABLE GU**");  st.dataframe(bus[['GU']].head(10))
        with col_c:
            st.write("**CRIME_TABLE GU**"); st.dataframe(crime[['GU']].head(10))

        # 매칭 안 되는 GU 탐지
        set_b = set(bus['GU']); set_c = set(cctv['GU']); set_cr = set(crime['GU'])
        unmatched = set_b.symmetric_difference(set_c) | set_b.symmetric_difference(set_cr)
        if unmatched:
            st.warning(f"⚠️ 아직 불일치하는 GU 값: {sorted(unmatched)}")
        else:
            st.success("✅ 모든 테이블 GU 값 일치!")

    # 01. 교통 vs 치안
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🚌 01. 교통 편리성과 범죄 발생의 상관관계")
    q1 = "SELECT B.GU, B.BUS_CNT, C.TOTAL FROM BUS_TABLE B JOIN (SELECT GU, SUM(CRIME_CNT) AS TOTAL FROM CRIME_TABLE GROUP BY GU) C ON B.GU = C.GU"
    df1 = pd.read_sql(q1, conn)

    col1, col2 = st.columns([1.8, 1])
    with col1:
        if df1.empty:
            st.error("❌ 여전히 데이터 없음 — 위 디버그 expander에서 불일치 GU 값을 확인하세요.")
        else:
            fig1 = px.scatter(df1, x='BUS_CNT', y='TOTAL', hover_name='GU', trendline="ols",
                              height=400, labels={'BUS_CNT':'정류소 수','TOTAL':'범죄 건수'})
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
        if df2.empty:
            st.error("❌ 여전히 데이터 없음 — 위 디버그 expander를 확인하세요.")
        else:
            fig2 = px.scatter(df2, x='CCTV_CNT', y='TOTAL', hover_name='GU', height=400,
                              labels={'CCTV_CNT':'CCTV 설치 수','TOTAL':'범죄 건수'})
            fig2.update_traces(marker=dict(size=12, color='#e63946'))
            st.plotly_chart(fig2, use_container_width=True)
    with col4:
        st.markdown('<div class="sql-code">' + q2 + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b
