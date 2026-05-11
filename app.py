import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="서울시 치안/교통 데이터 포털", layout="wide")

# 폰트 깨짐 방지 및 스타일링 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; height: 100px; font-size: 20px; border-radius: 10px; }
    .title-box { background-color: #003366; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 30px; }
    .insight-box { background-color: #e9ecef; padding: 15px; border-radius: 5px; border-left: 5px solid #003366; margin-top: 10px; }
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
        # 열 이름 정리 (Plotly 표시용)
        df.columns = ['자치구', 'CCTV_Count', 'Bus_Count', 'Crime_Count']
        return df
    except:
        st.error("데이터 파일을 찾을 수 없습니다. cctv_data.csv, bus_data.csv, crime_data.csv 파일을 확인해주세요.")
        return None

df = load_data()

# --- 메인 화면 (Home) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    st.markdown('<div class="title-box"><h1>🏛️ 서울시 자치구별 치안 및 교통 데이터 포털</h1><p>공공데이터 기반 안전 주거지 분석 시스템</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚌\n교통 vs 치안 분석"):
            st.session_state.page = 'bus_crime'
            st.rerun()
            
    with col2:
        if st.button("📹\nCCTV vs 치안 분석"):
            st.session_state.page = 'cctv_crime'
            st.rerun()
            
    with col3:
        if st.button("📊\n종합 상관관계 분석"):
            st.session_state.page = 'heatmap'
            st.rerun()

# --- 1. 교통 vs 치안 (Bus vs Crime) ---
elif st.session_state.page == 'bus_crime':
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()
        
    st.header("🚌 교통 편리성 vs 치안 (Bus vs Crime)")
    fig = px.scatter(df, x='Bus_Count', y='Crime_Count', hover_name='자치구', 
                     trendline="ols", labels={'Bus_Count':'버스 정류소 개수', 'Crime_Count':'범죄 발생 건수'})
    fig.update_traces(marker=dict(size=12, color='#003366'))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 분석 인사이트</b><br>
    유동인구가 보장된 교통 요충지는 범죄 노출 가능성이 높을 수 있으므로, 단순히 정류소 개수만 볼 것이 아니라 해당 지역의 야간 조명 및 파출소 위치를 함께 고려해야 합니다. 안전하게 집을 고르기 위해서는 교통 편리성과 범죄 발생 수 사이의 균형이 잘 잡힌 자치구를 선택하는 것이 핵심입니다.
    </div>
    """, unsafe_allow_html=True)

# --- 2. CCTV vs 치안 (CCTV vs Crime) ---
elif st.session_state.page == 'cctv_crime':
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()
        
    st.header("📹 CCTV 설치 대수 vs 치안 (CCTV vs Crime)")
    fig = px.scatter(df, x='CCTV_Count', y='Crime_Count', hover_name='자치구',
                     text='자치구', # 점 위에 자치구명 상시 표시 (선택사항)
                     hover_data={'CCTV_Count': True, 'Crime_Count': True},
                     labels={'CCTV_Count':'CCTV 설치 개수', 'Crime_Count':'범죄 발생 건수'})
    fig.update_traces(marker=dict(size=15, color='#e63946'), textposition='top center')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 분석 인사이트</b><br>
    CCTV가 적음에도 범죄율이 낮은 곳은 기초 치안 공동체가 잘 형성된 지역일 가능성이 높으며, 반대로 CCTV가 많음에도 범죄율이 높은 곳은 그만큼 행정력이 집중되어야 하는 고위험 지역임을 나타냅니다. 주거지 결정 시 CCTV 대수뿐만 아니라 실제 범죄 발생 추이를 함께 비교하여 인프라 대비 실질적 안전도를 파악해야 합니다.
    </div>
    """, unsafe_allow_html=True)

# --- 3. 종합 상관관계 (Heatmap) ---
elif st.session_state.page == 'heatmap':
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = 'home'
        st.rerun()
        
    st.header("📊 데이터 지표 간 상관관계 분석")
    st.info("ℹ️ 가이드: 색상이 붉을수록(1에 가까울수록) 두 지표가 강한 양의 상관관계를 가짐을 의미합니다.")
    
    corr = df[['CCTV_Count', 'Bus_Count', 'Crime_Count']].corr()
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r',
                    labels=dict(color="상관도"),
                    x=['CCTV', 'Bus', 'Crime'], y=['CCTV', 'Bus', 'Crime'])
    st.plotly_chart(fig, use_container_width=False)
    
    st.markdown("""
    <div class="insight-box">
    <b>💡 분석 인사이트</b><br>
    분석 결과 CCTV와 범죄 간의 상관관계는 0.62로 높아 범죄 취약 지역에 CCTV가 집중 설치되었음을 알 수 있으나, 교통(Bus)과 CCTV의 관련성은 0.46으로 다소 낮게 나타났습니다. 따라서 안전한 주거를 위해서는 단순히 교통이 편리한 곳을 찾기보다, 교통 요충지 중에서도 CCTV 인프라가 충분히 보완된 지역인지 개별적으로 검증하는 과정이 필요합니다.
    </div>
    """, unsafe_allow_html=True)
