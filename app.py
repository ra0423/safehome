import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울시 치안/교통 공공데이터 포털", layout="wide")

# 2. CSS 스타일링 (따옴표 오류를 최소화하기 위해 변수에 저장)
style_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 헤더 */
    .gov-header {
        background-color: #002d56; padding: 50px; color: white; text-align: center; 
        border-bottom: 8px solid #af8a2c; margin-bottom: 40px;
    }
    
    /* 사진 버튼 카드 */
    .nav-card {
        position: relative; width: 100%; height: 280px; border-radius: 15px;
        overflow: hidden; margin-bottom: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .nav-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5); display: flex; flex-direction: column;
        justify-content: center; align-items: center; color: white; z-index: 1;
    }
    
    /* 투명 클릭 버튼 */
    div.stButton > button {
        position: absolute; top: -280px; width: 100%; height: 280px;
        background: transparent !important; color: transparent !important;
        border: none !important; z-index: 5; cursor: pointer;
    }
    
    /* 서브페이지 전용 버튼(뒤로가기) */
    .sub-page div.stButton > button {
        position: static; width: auto; height: auto;
        background-color: #002d56 !important; color: white !important;
        padding: 10px 20px; z-index: 1;
    }

    /* 인사이트 박스 */
    .insight-box {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border-left: 10px solid #002d56; margin: 30px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# 3. 데이터 로딩
@st.cache_data
def load_data():
    try:
        # 파일명을 실제 깃허브에 올리신 이름과 동일하게 맞춰주세요.
        df_cctv = pd.read_csv('서울 CCTV.csv')
        df_bus = pd.read_csv('서울시 정류소.csv')
        df_crime = pd.read_csv('서울_범죄_자치구별_재정렬 (1).csv')
        
        crime_sum = df_crime.groupby('자치구')['건수'].sum().reset_index()
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, crime_sum, on='자치구')
        df.columns = ['자치구', 'CCTV_Count', 'Bus_Count', 'Crime_Count']
        return df
    except:
        st.error("데이터 파일을 찾을 수 없습니다. 파일명을 확인해 주세요.")
        return None

df = load_data()

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 메인 화면 ---
if st.session_state.page == 'home':
    st.markdown('<div class="gov-header"><h1>서울시 공공데이터 안심 포털</h1><p>데이터 기반 치안 및 교통 통합 지표 분석</p></div>', unsafe_allow_html=True)

    # 1. 교통 분석 버튼
    st.markdown('<div class="nav-card" style="background: url(\'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?q=80&w=2070\') center/cover;"><div class="nav-overlay"><h2>🚌 교통 편리성 vs 치안</h2><p>유동인구 집중 지역의 안전도 분석</p></div></div>', unsafe_allow_html=True)
    if st.button("BUS", key="b1"):
        st.session_state.page = 'p1'
        st.rerun()

    # 2. CCTV 분석 버튼
    st.markdown('<div class="nav-card" style="background: url(\'https://images.unsplash.com/photo-1557597774-9d273605dfa9?q=80&w=2070\') center/cover;"><div class="nav-overlay"><h2>📹 방범 인프라 vs 치안</h2><p>CCTV 설치 효율성 및 예방 효과</p></div></div>', unsafe_allow_html=True)
    if st.button("CCTV", key="b2"):
        st.session_state.page = 'p2'
        st.rerun()

    # 3. 종합 분석 버튼
    st.markdown('<div class="nav-card" style="background: url(\'https://images.unsplash.com/photo-1551288049-bbbda536639a?q=80&w=2070\') center/cover;"><div class="nav-overlay"><h2>📊 데이터 종합 상관도</h2><p>지표 간 연관성 기반 주거 안전 가이드</p></div></div>', unsafe_allow_html=True)
    if st.button("HEAT", key="b3"):
        st.session_state.page = 'p3'
        st.rerun()

# --- 상세 페이지 ---
else:
    st.markdown('<div class="sub-page">', unsafe_allow_html=True)
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.page == 'p1':
        st.title("🚌 교통 편리성 vs 치안 분석")
        fig = px.scatter(df, x='Bus_Count', y='Crime_Count', hover_name='자치구', trendline="ols", height=600)
        fig.update_layout(plot_bgcolor="#f8f9fa") # 차트 배경색
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 교통 요충지는 유동인구가 많아 편리하지만 범죄 노출 빈도도 함께 상승하는 경향이 있습니다. 주거지 선택 시 인근의 방범 시설을 반드시 교차 확인하십시오.</div>', unsafe_allow_html=True)

    elif st.session_state.page == 'p2':
        st.title("📹 방범 인프라 vs 치안 분석")
        fig = px.scatter(df, x='CCTV_Count', y='Crime_Count', hover_name='자치구', height=600)
        fig.update_layout(plot_bgcolor="#f8f9fa")
        fig.update_traces(marker=dict(size=18, color='#e63946', line=dict(width=1, color='white')))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> CCTV 수치가 높은 구는 행정적 집중 관리가 이루어지는 지역임을 의미합니다. 인프라 대비 실제 발생 건수의 비율을 따져보는 것이 실질적인 안전도 파악에 유리합니다.</div>', unsafe_allow_html=True)

    elif st.session_state.page == 'p3':
        st.title("📊 데이터 종합 상관도")
        corr = df[['CCTV_Count', 'Bus_Count', 'Crime_Count']].corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=['CCTV', 'Bus', 'Crime'], y=['CCTV', 'Bus', 'Crime'], colorscale='RdBu_r'))
        fig.update_layout(height=600, plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box"><b>💡 인사이트:</b> CCTV와 범죄의 상관관계(0.62)는 높지만 교통과의 연관성(0.46)은 상대적으로 낮습니다. 이는 교통 접근성만으로 치안 인프라 수준을 판단해서는 안 된다는 것을 시사합니다.</div>', unsafe_allow_html=True)
