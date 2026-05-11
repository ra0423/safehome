import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# 1. 한글 폰트 설정 (Streamlit Cloud 환경 대응)
@st.cache_data
def set_korean_font():
    # 리눅스 환경에 설치된 나눔고딕을 찾거나, 기본 폰트 설정
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
    
    # 만약 로컬에 나눔고딕이 있다면 적용 (시스템 환경에 따라 다를 수 있음)
    for font in fm.findSystemFonts():
        if 'Nanum' in font:
            fm.fontManager.addfont(font)
            font_name = fm.FontProperties(fname=font).get_name()
            plt.rc('font', family=font_name)
            break

set_korean_font()

def load_data():
    try:
        df_cctv = pd.read_csv('cctv_data.csv')
        df_bus = pd.read_csv('bus_data.csv')
        df_crime_raw = pd.read_csv('crime_data.csv')
        
        # 자치구별 합산
        df_crime = df_crime_raw.groupby('자치구')['건수'].sum().reset_index()
        
        # 데이터 통합
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, df_crime, on='자치구')
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        st.stop()

st.title("🏙️ 서울시 자치구별 교통 & 치안 분석")

df = load_data()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["교통 vs 치안", "CCTV vs 치안", "종합 상관계수"])

# 도표 크기 설정 (기존 10, 6에서 약 40% 축소한 6, 4 정도로 설정)
CHART_SIZE = (6, 4)

with tab1:
    st.subheader("1. 교통 편리성(버스)과 범죄 발생")
    fig, ax = plt.subplots(figsize=CHART_SIZE)
    sns.regplot(data=df, x='버스 정류소 개수', y='건수', ax=ax)
    ax.set_title("버스 정류소 수 vs 범죄 건수")
    ax.set_xlabel("버스 정류소 개수")
    ax.set_ylabel("범죄 건수")
    st.pyplot(fig)

with tab2:
    st.subheader("2. CCTV 설치 대수와 범죄 발생")
    fig, ax = plt.subplots(figsize=CHART_SIZE)
    sns.scatterplot(data=df, x='CCTV 개수', y='건수', hue='자치구', s=80, ax=ax)
    ax.set_title("CCTV 수 vs 범죄 건수")
    ax.set_xlabel("CCTV 개수")
    ax.set_ylabel("범죄 건수")
    # 범례가 너무 크면 그래프를 가리므로 밖으로 빼거나 크기 조절
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small', ncol=2)
    st.pyplot(fig)

with tab3:
    st.subheader("3. 지표 간 상관관계")
    corr = df[['CCTV 개수', '버스 정류소 개수', '건수']].corr()
    # 상관관계 히트맵은 더 작게 (5, 4)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt=".2f")
    st.pyplot(fig)
