import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정 (없으면 그래프 한글이 깨져요)
plt.rc('font', family='NanumGothic')

def load_data():
    # 1. 파일 읽기 (파일명이 깃허브와 똑같아야 합니다!)
    df_cctv = pd.read_csv('cctv_data.csv')
    df_bus = pd.read_csv('bus_data.csv')
    df_crime_raw = pd.read_csv('crime_data.csv') # 제가 드린 파일명

    # 2. 범죄 데이터 요약 (주제 분석을 위해 자치구별 총합 구하기)
    # 상세 내역을 '자치구' 기준으로 다 더합니다.
    df_crime = df_crime_raw.groupby('자치구')['건수'].sum().reset_index()
    df_crime.rename(columns={'건수': '총범죄건수'}, inplace=True)

    # 3. 컬럼명 통일 (에러 방지용)
    df_cctv.rename(columns={df_cctv.columns[0]: '자치구'}, inplace=True)
    df_bus.rename(columns={df_bus.columns[0]: '자치구'}, inplace=True)

    # 4. 데이터 하나로 합치기
    df = pd.merge(df_cctv, df_bus, on='자치구')
    df = pd.merge(df, df_crime, on='자치구')
    
    return df

st.set_page_config(page_title="서울 안전 대시보드", layout="wide")
st.title("🏙️ 서울시 자치구별 교통 & 치안 상관관계 분석")

try:
    df = load_data()
    st.success("데이터 통합 완료!")

    # --- 탭 구성 (요청하신 3가지 주제) ---
    tab1, tab2, tab3 = st.tabs(["교통 vs 치안", "CCTV vs 치안", "종합 검증"])

    with tab1:
        st.subheader("1. 교통 편리성(버스)과 범죄율의 관계")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.regplot(data=df, x='버스정류소수', y='총범죄건수', ax=ax)
        st.pyplot(fig)
        st.write("💡 버스 정류소가 많으면서(교통 편리) 범죄율이 낮은 자치구를 찾아보세요.")

    with tab2:
        st.subheader("2. CCTV 개수와 범죄율의 관계")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=df, x='CCTV개수', y='총범죄건수', size='총범죄건수', hue='자치구', ax=ax)
        st.pyplot(fig)
        st.write("💡 CCTV 설치 대수와 실제 범죄 발생 건수의 상관관계를 분석합니다.")

    with tab3:
        st.subheader("3. 종합 상관계수 (CCTV, 버스, 범죄율)")
        # 숫자 데이터만 골라서 상관계수 계산
        corr = df[['CCTV개수', '버스정류소수', '총범죄건수']].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
        st.write("💡 세 지표 간의 밀접도를 숫자로 확인합니다. (1에 가까울수록 높은 상관관계)")

except Exception as e:
    st.error(f"데이터 로드 중 오류가 발생했습니다. 파일명을 확인해주세요: {e}")
