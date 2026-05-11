import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 통합 데이터 포털", layout="wide")

# 2. 고도화된 스타일링 (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    .main { background-color: #f4f7f9; }

    /* 헤더 디자인 */
    .gov-header {
        background-color: #002d56; 
        padding: 50px 20px; 
        color: white; 
        text-align: center; 
        border-bottom: 8px solid #af8a2c;
        margin-bottom: 40px;
    }

    /* 이미지 버튼 카드 디자인 */
    .nav-card {
        position: relative;
        width: 100%;
        height: 300px;
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        transition: 0.3s;
    }
    
    /* 사진 위에 깔리는 반투명 레이어와 글자 */
    .nav-overlay {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); /* 불투명도 조절 */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        pointer-events: none; /* 클릭이 버튼으로 전달되게 함 */
    }

    .nav-card:hover { transform: scale(1.01); }

    /* 스트림릿 버튼을 투명하게 만들어 이미지 위에 덮기 */
    div.stButton > button {
        position: absolute;
        top: -300px; /* 이미지 높이만큼 위로 올려서 겹침 */
        width: 100%;
        height: 300px;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        cursor: pointer;
        z-index: 10;
    }
    
    /* 서브페이지 뒤로가기 버튼은 정상 출력되게 설정 */
    .back-btn div.stButton > button {
        position: static;
        width: auto;
        height: auto;
        background-color: #002d56 !important;
        color: white !important;
        padding: 10px 20px;
        margin-bottom: 20px;
    }

    /* 인사이트 박스 */
    .insight-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        border-left: 10px solid #002d56;
        margin: 30px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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
        return None

df = load_data()

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- [메인 홈 화면] ---
if st.session_state.page == 'home':
    st.markdown("""
        <div class="gov-header">
            <h1 style="font-size: 3rem; margin-bottom: 10px;">서울시 안전/교통 공공데이터 포털</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">데이터로 확인하는 우리 동네 치안 안심 지
