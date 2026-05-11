import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 공공데이터 포털", layout="wide")

# 2. 통합 스타일 설정 (클릭 문제 및 변수 선언 오류 해결)
# 변수 이름을 'final_style'로 통일하여 NameError를 방지합니다.
final_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    .gov-header {
        background-color: #002d56; padding: 50px; color: white; text-align: center; 
        border-bottom: 8px solid #af8a2c; margin-bottom: 40px;
    }
    
    /* 카드 컨테이너 */
    .nav-card {
        position: relative; width: 100%; height: 280px; border-radius: 15px;
        overflow: hidden; margin-bottom: 10px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .nav-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5); display: flex; flex-direction: column;
        justify-content: center; align-items: center; color: white; z-index: 1;
    }

    /* 클릭 영역 강제 확보: 버튼을 이미지 위로 띄움 */
    div.stButton {
        position: relative;
        top: -290px; /* 카드의 높이만큼 위로 올려서 겹침 */
        margin-bottom: -280px; 
    }
    
    div.stButton > button {
        width: 100% !important;
        height: 280px !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10 !important;
        cursor: pointer !important;
    }
    
    /* 상세페이지(뒤로가기) 버튼은 정상적으로 보이게 복구 */
    .sub-page div.stButton { top: 0; margin-bottom: 0; }
    .sub-page div.stButton > button {
        background-color: #002d56 !important; 
        color: white !important;
        height: auto !important; 
        width: auto !important;
        padding: 10px 20px !important;
    }

    .insight-box {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border-left: 10px solid #002d56; margin: 30px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
</style>
"""
st.markdown(final_style, unsafe_allow_html=True)

# 3. 데이터 로딩 (파일명 매칭 주의)
@st.cache_data
def load_data():
    try:
        # 깃허브 리포지토리에 있는 정확한 파일명으로 수정하세요.
        # 예: '서울 CCTV.csv', '서울시 정류소.csv', '서울_범죄_자치구별_재정렬 (1).csv'
        df_cctv = pd.read_csv('cctv_data.csv') 
        df_bus = pd.read_csv('bus_data.csv')
        df_crime = pd.read_csv('crime_data.csv')
        
        crime_sum = df_crime.groupby('자치구')['건수'].sum().reset_index()
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, crime_sum, on='자치구')
        df.columns = ['자치구', 'CCTV_Count', 'Bus_Count', 'Crime_Count']
        return df
    except Exception as e:
        st.warning(f"데이터 로드 대기 중... 파일명을 확인해주세요: {e}")
        return None

df = load_data()

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- [메인 화면] ---
if st.session_state.page == 'home':
    st.markdown('<div class="gov-header"><h1>서울시 공공데이터 안심 포털</h1><p>데이터 기반 치안 및 교통 통합 지표 분석</p></div>', unsafe_allow_html=True)

    # 카드 1
    st.markdown('<div class="nav-card" style="background: url(\'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?q=80&w=2070\') center/cover;"><div class="nav-overlay"><h2>🚌 교통 편리성 vs 치안</h2><p>유동인구 집중 지역의 안전도 분석</p></div></div>', unsafe_allow_html=True)
    if st.button("BUS", key="b1"):
        st.session_state.page = 'p1'
        st.rerun()

    # 카드 2
    st.markdown('<div class="nav-card" style="background: url(\'https://images.unsplash.com/photo-1557597774-9d273605dfa9?q=80&w=2070\') center/cover;"><div class="nav-overlay"><h2>📹 방범 인프라 vs 치안</h2><p>CCTV 설치 효율성 및 예방 효과</p></div></div>', unsafe_allow_html=True)
    if st.button("CCTV", key="b2"):
        st.session_state.page = 'p2'
        st.rerun()

    # 카드 3
    st.markdown('<div class="nav-card" style="background: url(\'https://images.unsplash.com/photo-1551288049-bbbda536639a?q=80&w=2070\') center/cover;"><div class="nav-overlay"><h2>📊 데이터 종합 상관도</h2><p>지표 간 연관성 기반 주거 안전 가이드</p></div></div>', unsafe_allow_html=True)
    if st.button("HEAT", key="b3"):
        st.session_state.page = 'p3'
        st.rerun()

# --- [상세 페이지] ---
else:
    st.markdown('<div class="sub-page">', unsafe_allow_html=True)
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if df is not None:
        if st.session_state.page == 'p1':
            st.title("🚌 교통 편리성 vs 치안 분석")
            fig = px.scatter(df, x='Bus_Count', y='Crime_Count', hover_name='자치구', trendline="ols", height=600)
            fig.update_layout(plot_bgcolor="#f8f9fa")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 유동인구가 많은 구역은 치안 인프라가 집중되어야 할 핵심 지역입니다.</div>', unsafe_allow_html=True)

        elif st.session_state.page == 'p2':
            st.title("📹 방범 인프라 vs 치안 분석")
            fig = px.scatter(df, x='CCTV_Count', y='Crime_Count', hover_name='자치구', height=600)
            fig.update_layout(plot_bgcolor="#f8f9fa")
            fig.update_traces(marker=dict(size=18, color='#e63946', line=dict(width=1, color='white')))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="insight-box"><b>💡 인사이트:</b> CCTV 밀집도가 범죄 예방에 미치는 실질적 영향을 확인할 수 있습니다.</div>', unsafe_allow_html=True)

        elif st.session_state.page == 'p3':
            st.title("📊 데이터 종합 상관도")
            corr = df[['CCTV_Count', 'Bus_Count', 'Crime_Count']].corr()
            fig = go.Figure(data=go.Heatmap(z=corr.values, x=['CCTV', 'Bus', 'Crime'], y=['CCTV', 'Bus', 'Crime'], colorscale='RdBu_r'))
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="insight-box"><b>💡 인사이트:</b> 각 지표 간의 상관관계를 통해 종합적인 주거 안전도를 판단합니다.</div>', unsafe_allow_html=True)
    else:
        st.error("데이터가 로드되지 않았습니다. 파일명을 확인해 주세요.")
