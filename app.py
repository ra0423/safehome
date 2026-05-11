import streamlit as st
import pandas as pd
import os

# 데이터 로드 함수 (CSV 버전)
def load_data():
    # 파일들이 GitHub에 올린 이름과 정확히 일치해야 해!
    try:
        # 만약 파일이 여러 개라면 여기서 하나로 합치는(Merge) 작업을 할 수 있어
        df_cctv = pd.read_csv('cctv.csv')
        df_bus = pd.read_csv('bus_stations.csv')
        df_crime = pd.read_csv('crime_rate.csv')
        
        # '자치구' 컬럼을 기준으로 데이터 합치기
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, df_crime, on='자치구')
        
        return df
    except FileNotFoundError as e:
        st.error(f"🚨 파일을 찾을 수 없습니다: {e}")
        st.info("GitHub에 CSV 파일들이 잘 올라갔는지 확인해주세요!")
        st.stop()

st.title("🏙️ 서울시 자치구별 치안/교통 종합 분석")

# 데이터 불러오기
df = load_data()

# 데이터가 잘 불러와졌는지 확인용 테이블
st.write("### 현재 분석 데이터 요약", df.head())

# 이후에 시각화 코드(차트 등)를 작성하면 돼!