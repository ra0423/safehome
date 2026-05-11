import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    try:
        # 데이터 로드
        df_cctv = pd.read_csv('cctv_data.csv')
        df_bus = pd.read_csv('bus_data.csv')
        df_crime_raw = pd.read_csv('crime_data.csv')
        
        # 자치구별 범죄 합산
        df_crime = df_crime_raw.groupby('자치구')['건수'].sum().reset_index()
        
        # 데이터 통합
        df = pd.merge(df_cctv, df_bus, on='자치구')
        df = pd.merge(df, df_crime, on='자치구')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

st.title("🏙️ Seoul Safety Dashboard")

df = load_data()

# 탭 구성 (제목은 한글로 해도 본문 텍스트라 안 깨집니다!)
tab1, tab2, tab3 = st.tabs(["Bus vs Crime", "CCTV vs Crime", "Correlation"])

# 도표 크기 (요청하신 대로 작게 설정)
CHART_SIZE = (5, 3.5)

with tab1:
    st.subheader("1. Bus Stops vs Crime")
    fig, ax = plt.subplots(figsize=CHART_SIZE)
    # x, y축에 들어가는 한글 데이터(자치구 이름 등)를 피하기 위해 범례를 조정
    sns.regplot(data=df, x='버스 정류소 개수', y='건수', ax=ax)
    
    # 축 이름을 영어로 설정 (깨짐 방지)
    ax.set_xlabel("Number of Bus Stops", fontsize=9)
    ax.set_ylabel("Crime Count", fontsize=9)
    ax.set_title("Bus Stops & Crime", fontsize=10)
    st.pyplot(fig)

with tab2:
    st.subheader("2. CCTV vs Crime")
    fig, ax = plt.subplots(figsize=CHART_SIZE)
    # hue='자치구'를 쓰면 범례에 한글이 들어가서 깨지므로, 여기서는 제거하거나 숫자로 대체합니다.
    sns.scatterplot(data=df, x='CCTV 개수', y='건수', s=50, ax=ax)
    
    ax.set_xlabel("Number of CCTV", fontsize=9)
    ax.set_ylabel("Crime Count", fontsize=9)
    ax.set_title("CCTV & Crime", fontsize=10)
    st.pyplot(fig)

with tab3:
    st.subheader("3. Heatmap")
    # 열 이름을 영어로 잠시 바꿔서 상관관계 도표 그리기
    temp_df = df[['CCTV 개수', '버스 정류소 개수', '건수']]
    temp_df.columns = ['CCTV', 'Bus', 'Crime']
    
    corr = temp_df.corr()
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, annot_kws={"size": 8})
    st.pyplot(fig)
