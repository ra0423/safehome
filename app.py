# --- [스타일 설정 부분만 아래 내용으로 교체하세요] ---
style_css = """
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
        overflow: hidden; margin-bottom: 10px; /* 버튼과의 간격을 줄임 */
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .nav-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5); display: flex; flex-direction: column;
        justify-content: center; align-items: center; color: white; z-index: 1;
    }

    /* ⭐ 클릭 해결 포인트: 버튼을 이미지 위로 완벽하게 올림 */
    div.stButton {
        position: relative;
        top: -290px; /* 카드의 높이 + 마진만큼 위로 올림 */
        margin-bottom: -280px; /* 뒤따라오는 요소들이 겹치지 않게 공간 확보 */
    }
    
    div.stButton > button {
        width: 100% !important;
        height: 280px !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10 !important; /* 오버레이보다 위에 배치 */
        cursor: pointer !important;
    }
    
    /* 상세페이지 버튼은 정상화 */
    .sub-page div.stButton { top: 0; margin-bottom: 0; }
    .sub-page div.stButton > button {
        background-color: #002d56 !important; color: white !important;
        height: auto !important; width: auto !important;
    }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)
