import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정 및 테마
st.set_page_config(page_title="서울시 치안/교통 공공데이터 포털", layout="wide")

# 관공서 느낌의 커스텀 CSS (이미지 버튼 및 레이아웃)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    .main { background-color: #ffffff; }
    
    /* 헤더 스타일 */
    .gov-header {
        background-color: #003366; 
        padding: 40px; 
        border-radius: 5px; 
        color: white; 
        text-align: center; 
        margin-bottom: 40px;
        border-bottom: 5px solid #cb941e;
    }
    
    /* 이미지 버튼 스타일 */
    .img-btn {
        position: relative;
        width: 100%;
        height: 250px;
        margin-bottom: 250px;
        border-radius: 15px;
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.3s;
        border: 1px solid #ddd;
    }
    
    .img-btn:hover { transform: scale(1.02); }
    
    /* 인사이트 박스 */
    .insight-box {
        background-color: #f1f3f5;
        padding: 25px;
        border-radius: 10px;
        border-left: 8px solid #003366;
        margin: 30px 0;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df_cctv = pd.read_csv('cctv_data.csv')
        df_bus = pd.read_csv('bus_data.csv')
        df_crime_raw = pd.read_csv('crime_data.csv')
        df_crime = df_crime_raw.groupby('자치구')['건수'].sum().reset_index()
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, df_crime, on='자치구')
        df.columns = ['자치구', 'CCTV_Count', 'Bus_Count', 'Crime_Count']
        return df
    except:
        st.error("데이터 파일을 로드할 수 없습니다. 파일명을 확인해주세요.")
        return None

df = load_data()

# 페이지 관리 세션
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 메인 화면 (Home) ---
if st.session_state.page == 'home':
    st.markdown("""
        <div class="gov-header">
            <p style="font-size: 1.2rem; margin-bottom: 10px;">Seoul Public Data Portal</p>
            <h1 style="font-size: 2.8rem; font-weight: 700;">서울시 자치구별 치안 및 교통 통합 분석 시스템</h1>
            <p style="opacity: 0.8;">본 시스템은 공공데이터포털의 최신 데이터를 바탕으로 시민의 안전한 주거 선택을 지원합니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 세로 3줄 배치 (사진 + 버튼 결합)
    # 1번 메뉴
    st.image("https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    if st.button("📊 [교통 vs 치안] 유동인구 지표 기반 상관관계 분석 시작하기", key="btn1", use_container_width=True):
        st.session_state.page = 'bus_crime'
        st.rerun()
    st.markdown("<br><br>", unsafe_allow_html=True)

    # 2번 메뉴
    st.image("https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    if st.button("🔍 [CCTV vs 치안] 방범 인프라 효율성 및 안전도 검증", key="btn2", use_container_width=True):
        st.session_state.page = 'cctv_crime'
        st.rerun()
    st.markdown("<br><br>", unsafe_allow_html=True)

    # 3번 메뉴
    st.image("https://images.
