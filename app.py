import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정 (폰트가 없으면 그래프에서 한글이 깨질 수 있습니다)
plt.rc('font', family='NanumGothic')

def load_data():
    try:
        # 1. 바뀐 파일 이름으로 읽어오기
        df_cctv = pd.read_csv('cctv_data.csv')
        df_bus = pd.read_csv('bus_data.csv')
        df_crime_raw = pd.read_csv('crime_data.csv')

        # 2. 범죄 데이터 자치구별 합산 (상세 내역 -> 자치구별 총합)
        df_crime = df_crime_raw.groupby('자치구')['건수'].sum().reset_index()

        # 3. 데이터 통합 (Merge) - '자치구' 열 기준
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, df_crime, on='자치구')
        
        return df
    except Exception as e:
        st.error(f"🚨 파일을 불러오는 중 오류가 발생했습니다: {e}")
        st.info("GitHub에 cctv_data.csv, bus_data.csv, crime_data.csv 파일이 모두 있는지 확인해주세요.")
        st.stop()

st.set_page_config(page_title="서울 안전 대시보드", layout="wide")
st.title("🏙️ 서울시 자치구별 교통 & 치안 상관관계 분석")

df = load_data()

if df is not None:
    st.success("데이터를 성공적으로 불러왔습니다!")

    # 분석 탭 구성
    tab1, tab2, tab3 = st.tabs(["교통 vs 치안", "CCTV vs 치안", "종합 상관계수"])

    with tab1:
        st.subheader("1. 교통 편리성(버스 정류소)과 범죄 발생의 관계")
        fig, ax = plt.subplots(figsize=(10, 6))
        # 실제 파일 내 열 이름인 '버스 정류소 개수'와 '건수' 사용
        sns.regplot(data=df, x='버스 정류소 개수', y='건수', ax=ax)
        st.pyplot(fig)
        st.write("💡 버스 정류소 수와 범죄 발생 건수 사이의 추세선을 확인합니다.")

    with tab2:
        st.subheader("2. CCTV 설치 대수와 범죄 발생의 관계")
        fig, ax = plt.subplots(figsize=(10, 6))
        # 실제 파일 내 열 이름인 'CCTV 개수'와 '건수' 사용
        sns.scatterplot(data=df, x='CCTV 개수', y='건수', hue='자치구', s=100, ax=ax)
        st.pyplot(fig)
        st.write("💡 자치구별 CCTV 개수에 따른 범죄 발생 분포를 확인합니다.")

    with tab3:
        st.subheader("3. 지표 간 상관관계 (Heatmap)")
        corr = df[['CCTV 개수', '버스 정류소 개수', '건수']].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
        st.write("💡 1에 가까울수록 양의 상관관계, -1에 가까울수록 음의 상관관계를 의미합니다.")
