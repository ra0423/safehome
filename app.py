import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 및 브라우저 탭 이름
st.set_page_config(page_title="서울시 치안/교통 공공데이터 포털", layout="wide")

# 2. 전문적인 스타일링 (CSS) - 관공서 신뢰감을 주는 디자인
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 전체 배경 및 헤더 */
    .main { background-color: #ffffff; }
    .gov-header {
        background-color: #002d56; 
        padding: 60px 20px; 
        color: white; 
        text-align: center; 
        border-bottom: 8px solid #af8a2c;
        margin-bottom: 50px;
    }
    
    /* 메뉴 카드 디자인 (이미지+버튼 일체형) */
    .menu-card {
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 70px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    }
    
    /* 인사이트 박스 디자인 */
    .insight-box {
        background-color: #f1f3f5;
        padding: 30px;
        border-radius: 12px;
        border-left: 10px solid #002d56;
        margin: 40px 0;
        font-size: 1.15rem;
        line-height: 1.8;
        color: #212529;
    }
    
    /* 버튼 스타일 커스텀 */
    div.stButton > button {
        width: 100%;
        height: 70px;
        background-color: #002d56 !important;
        color: white !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        border-radius: 0 0 15px 15px !important;
        border: none !important;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: #af8a2c !important;
        transition: 0.3s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        # 파일명은 요청하신 대로 cctv_data.csv, bus_data.csv, crime_data.csv 기준입니다.
        df_cctv = pd.read_csv('cctv_data.csv')
        df_bus = pd.read_csv('bus_data.csv')
        df_crime_raw = pd.read_csv('crime_data.csv')
        
        # 자치구별 범죄 합산 처리
        df_crime = df_crime_raw.groupby('자치구')['건수'].sum().reset_index()
        
        # 데이터 병합
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, df_crime, on='자치구')
        
        # 데이터 시각화용 영문 컬럼명 설정
        df.columns = ['자치구', 'CCTV_Count', 'Bus_Count', 'Crime_Count']
        return df
    except Exception as e:
        st.error(f"데이터 파일 로드 중 오류가 발생했습니다: {e}")
        return None

df = load_data()

# 4. 페이지 전환 로직
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- [HOME] 메인 포털 화면 ---
if st.session_state.page == 'home':
    st.markdown("""
        <div class="gov-header">
            <h1 style="font-size: 3.5rem; margin-bottom: 15px; font-weight: 700;">서울시 공공데이터 치안/교통 통합 분석 포털</h1>
            <p style="font-size:
