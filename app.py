import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 공공데이터 포털", layout="wide")

# 2. 전문적인 스타일링 (CSS)
# 사진을 배경으로 쓰고 그 위에 버튼을 투명하게 올리는 트릭을 사용합니다.
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    .main { background-color: #f0f2f6; }
    .gov-header {
        background-color: #002d56; 
        padding: 50px; 
        color: white; 
        text-align: center; 
        border-bottom: 8px solid #af8a2c;
        margin-bottom: 40px;
    }
    
    /* 카드 컨테이너: 사진이 배경이 됨 */
    .nav-card {
        position: relative;
        width: 100%;
        height: 300px;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    /* 사진 위 반투명 덮개 */
    .nav-overlay {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5); /* 불투명도 조절 */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: 0.3s;
        z-index: 1;
    }
    .nav-card:hover .nav-overlay { background: rgba(0, 0, 0, 0.3); }

    /* 실제 클릭을 가로채는 투명 버튼 */
    div.stButton > button {
        position: absolute;
        top: -300px; /* 카드의 높이만큼 버튼을 끌어올림 */
        width: 100%;
        height: 300px;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 5;
        cursor: pointer;
    }

    /* 상세페이지 내의 일반 버튼(뒤로가기 등)은 정상적으로 보이게 처리 */
    .sub-page div.stButton > button {
        position: static;
        width: auto;
        height: auto;
        background-color: #002d56 !important;
        color: white !important;
        padding: 10px 25px;
        z-index: 1;
    }

    /* 인사이트 박스 */
    .insight-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        border-left: 10px solid #002d56;
        margin: 30px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # 파일명은 원본 데이터 파일명을 유지합니다.
        df_cctv = pd.read_csv('서울 CCTV.csv')
        df_bus = pd.read_csv('서울시 정류소.csv')
        df_crime = pd.read_csv('서울_범죄_자치구별_재정렬 (1).csv')
        
        df_crime_sum = df_crime.groupby('자치구')['건수'].sum().reset_index()
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, df_crime_sum, on='자치구')
        df.columns = ['자치구', 'CCTV_Count', 'Bus_Count', 'Crime_Count']
        return df
    except:
        return None

df = load_data()

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- [HOME] 메인 포털 ---
if st.session_state.page == 'home':
    st.markdown("""
        <div class="gov-header">
            <h1 style="color:white; font-size:3.5rem;">서울시 데이터 안심 주거 포털</h1>
            <p style="color:white; opacity:0.8; font-size:1.3rem;">공공데이터로 분석한 자치구별 치안 및 교통 지표</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. 교통 카드
    st.markdown("""
        <div class="nav-card" style="background: url('https://images.unsplash.com/photo-1570125909232-eb263c188f7e?q=80&w=2070&auto=format&fit=crop') center/cover;">
            <div class="nav-overlay">
                <h2 style="color:white; font-size:2.2rem;">🚌 교통 편리성 vs 치안</h2>
                <p style="color:white; font-size:1.1rem;">유동인구와 범죄율의 상관관계 분석</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("GO_BUS", key="go_bus"):
        st.session_state.page = 'bus'
        st.rerun()

    # 2. CCTV 카드
    st.markdown("""
        <div class="nav-card" style="background: url('https://images.unsplash.com/photo-1557597774-9d273605dfa9?q=80&w=2070&auto=format&fit=crop') center/cover;">
            <div class="nav-overlay">
                <h2 style="color:white; font-size:2.2rem;">📹 방범 인프라 vs 치안</h2>
                <p style="color:white; font-size:1.1rem;">CCTV 설치 대수 대비 실질 범죄 억제력</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("GO_CCTV", key="go_cctv"):
        st.session_state.page = 'cctv'
        st.rerun()

    # 3. Heatmap 카드
    st.markdown("""
        <div class="nav-card" style="background: url('https://images.unsplash.com/photo-1551288049-bbbda536639a?q=80&w=2070&auto=format&fit=crop') center/cover;">
            <div class="nav-overlay">
                <h2 style="color:white; font-size:2.2rem;">📈 데이터 상관관계 Heatmap</h2>
                <p style="color:white; font-size:1.1rem;">주거지 선택 시 고려해야 할 종합 지표</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("GO_HEAT", key="go_heat"):
        st.session_state.page = 'heat'
        st.rerun()

# --- [SUB PAGES] ---
else:
    st.markdown('<div class="sub-page">', unsafe_allow_html=True)
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 차트 배경색 설정
    PLOT_BG = "#f8f9fa"

    if st.session_state.page == 'bus':
        st.title("🚌 교통 편리성 vs 치안 분석")
        fig = px.scatter(df, x='Bus_Count', y='Crime_Count', hover_name='자치구', trendline="ols", height=700)
        fig.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor="white") # 배경색 적용
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 유동인구가 많은 교통 요충지는 생활은 편리하나 범죄 노출 가능성이 높습니다. 안전한 주거를 원하신다면 버스 정류소 수 대비 CCTV 밀집도가 높은 구를 선택하는 것이 현명합니다.</div>', unsafe_allow_html=True)

    elif st.session_state.page == 'cctv':
        st.title("📹 CCTV 방범 인프라 vs 치안 분석")
        fig = px.scatter(df, x='CCTV_Count', y='Crime_Count', hover_name='자치구', height=700)
        fig.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor="white")
        fig.update_traces(marker=dict(size=18, color='#e63946', line=dict(width=1, color='white')))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> CCTV 설치 대수와 범죄율
