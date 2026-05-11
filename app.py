import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울시 치안/교통 공공데이터 포털", layout="wide")

# 2. 스타일 설정 (CSS를 변수에 담아 깔끔하게 처리)
style_code = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .gov-header {
        background-color: #002d56; 
        padding: 50px 20px; 
        color: white; 
        text-align: center; 
        border-bottom: 8px solid #af8a2c;
        margin-bottom: 40px;
    }
    .menu-card {
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 50px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .insight-box {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 10px;
        border-left: 10px solid #002d56;
        margin: 30px 0;
        font-size: 1.1rem;
        line-height: 1.7;
    }
    div.stButton > button {
        width: 100%; height: 60px;
        background-color: #002d56 !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 0 0 15px 15px !important;
        border: none !important;
    }
    div.stButton > button:hover { background-color: #af8a2c !important; }
    </style>
"""
st.markdown(style_code, unsafe_allow_html=True)

# 3. 데이터 로드
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
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

df = load_data()

# 4. 페이지 전환 시스템
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- [메인 화면] ---
if st.session_state.page == 'home':
    st.markdown('<div class="gov-header"><h1>서울시 치안/교통 공공데이터 포털</h1><p>데이터 기반 안전 주거 분석 시스템</p></div>', unsafe_allow_html=True)
    
    # 1번 카드
    st.image("https://images.unsplash.com/photo-1570125909232-eb263c188f7e?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
    if st.button("📊 [교통환경 분석] 상세보기", key="m1"):
        st.session_state.page = 'bus_crime'
        st.rerun()
    
    st.write("") # 간격 조절

    # 2번 카드
    st.image("https://images.unsplash.com/photo-1557597774-9d273605dfa9?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
    if st.button("🔍 [방범인프라 분석] 상세보기", key="m2"):
        st.session_state.page = 'cctv_crime'
        st.rerun()

    st.write("")

    # 3번 카드
    st.image("https://images.unsplash.com/photo-1551288049-bbbda536639a?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
    if st.button("📈 [종합지표 분석] 상세보기", key="m3"):
        st.session_state.page = 'heatmap'
        st.rerun()

# --- [상세 페이지 1] ---
elif st.session_state.page == 'bus_crime':
    if st.button("⬅️ 메인으로"):
        st.session_state.page = 'home'
        st.rerun()
    st.title("🚌 교통 편리성 vs 치안 분석")
    fig = px.scatter(df, x='Bus_Count', y='Crime_Count', hover_name='자치구', trendline="ols", height=650)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box"><b>💡 분석 가이드</b><br>유동인구가 많은 교통 요충지는 생활이 편리하지만 범죄 노출 가능성도 존재합니다. 주거지 선택 시 야간 조명과 파출소 위치를 함께 확인하세요.</div>', unsafe_allow_html=True)

# --- [상세 페이지 2] ---
elif st.session_state.page == 'cctv_crime':
    if st.button("⬅️ 메인으로"):
        st.session_state.page = 'home'
        st.rerun()
    st.title("📹 방범 인프라(CCTV) vs 치안 분석")
    fig = px.scatter(df, x='CCTV_Count', y='Crime_Count', hover_name='자치구', height=650)
    fig.update_traces(marker=dict(size=20, color='red'))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box"><b>💡 분석 가이드</b><br>CCTV 설치 대수가 범죄율을 낮추는 실질적인 억제력을 발휘하고 있는지 해당 구의 추이를 확인해보세요.</div>', unsafe_allow_html=True)

# --- [상세 페이지 3] ---
elif st.session_state.page == 'heatmap':
    if st.button("⬅️ 메인으로"):
        st.session_state.page = 'home'
        st.rerun()
    st.title("📊 종합 상관도 분석")
    corr = df[['CCTV_Count', 'Bus_Count', 'Crime_Count']].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r', height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box"><b>💡 분석 가이드</b><br>CCTV-범죄 간의 높은 상관관계(0.62)는 치안 인프라의 적절한 배치를 보여주지만, 교통과의 연계성은 보강이 필요함을 나타냅니다.</div>', unsafe_allow_html=True)
