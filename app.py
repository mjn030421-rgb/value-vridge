import streamlit as st
from google import genai
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정 및 API 연결
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# 디자인 테마 (image_7a16c2.png 감성 적용)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stVerticalBlock"] > div:has(div.stButton) { text-align: center; }
    .stButton>button {
        background-color: #3182F6 !important;
        color: white !important;
        border-radius: 14px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        width: 100%;
        border: none !important;
    }
    .main-card {
        background-color: #F8F9FA;
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
        margin-bottom: 2rem;
    }
    h1, h2, h3 { color: #191F28 !important; font-weight: 800 !important; }
    p { color: #4E5968 !important; }
    </style>
    """, unsafe_allow_html=True)

# API 설정 (성현님의 기존 로직 유지)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "YOUR_LOCAL_KEY_HERE" 

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite" 

# 2. [상태 관리] session_state 초기화
if 'step' not in st.session_state:
    st.session_state.step = 1
for key in ['school', 'major', 'target', 'spec', 'exp', 'result']:
    if key not in st.session_state:
        st.session_state[key] = ""

# 3. [추적] 모든 과정을 track()으로 감싸기
with streamlit_analytics.track():
    st.title("🌉 Value Bridge")
    
    # 진행 바 (Progress Bar)
    progress_text = f"{st.session_state.step} / 4 단계 진행 중"
    st.progress(st.session_state.step / 4, text=progress_text)
    st.write("")

    # --- 1단계: 신원 정보 ---
    if st.session_state.step == 1:
        st.subheader("먼저, 소속을 알려주세요 🎓")
        st.write("성현님의 대학 생활을 분석하기 위한 첫 번째 단계입니다.")
        
        st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
        st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        st.write("")
        if st.button("다음으로", key="step1_next"):
            if st.session_state.school and st.session_state.major:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("모든 항목을 채워주세요!")

    # --- 2단계: 목표 및 스펙 ---
    elif st.session_state.step == 2:
        st.subheader("목표와 준비하신 스펙은요? 🏢")
        st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target, placeholder="예: 한국은행, 신한은행")
        st.session_state.spec = st.text_input("📜 보유 자격증", value=st.session_state.spec, placeholder="예: AFPK, 토익 900")
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("다음으로", key="step2_next"):
                if st.session_state.target:
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("목표 기업을 입력해 주세요.")

    # --- 3단계: 경험 기술 ---
    elif st.session_state.step == 3:
        st.subheader("가장 빛나는 경험을 들려주세요 ✨")
        st.session_state.exp = st.text_area("🌟 주요 경험 및 활동", value=st.session_state.exp, 
                                          placeholder="예: 노동경제학 프로젝트에서 파이썬 데이터 분석을 활용해...", height=200)
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("가치 브릿지 생성 🚀", key="analyze_btn"):
                if st.session_state.exp:
                    st.session_state.step = 4
                    st.rerun()
                else:
                    st.error("경험을 최소 한 문장 이상 적어주세요.")

    # --- 4단계: 결과 리포트 ---
    elif st.session_state.step == 4:
        st.subheader("🎯 성현님의 키워드 브릿지 리포트")
        
        with st.spinner("AI가 성현님의 경험을 분석하고 있습니다..."):
            try:
                if not st.session_state.result:
                    prompt = f"""
                    {st.session_state.target} 지원을 위한 핵심 역량 키워드 5개와 
                    {st.session_state.major} 전공 강점을 살린 자소서 팁을 작성해줘.
                    경험: {st.session_state.exp}
                    """
                    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                    st.session_state.result = response.text
                
                st.markdown(f"**{st.session_state.target}** 분석 결과입니다.")
                st.info(st.session_state.result)
                
                st.divider()
                st.link_button("수요조사 참여하고 정식 버전 알림 받기", "https://forms.gle/your_link")
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

        if st.button("처음부터 다시 하기"):
            for key in ['school', 'major', 'target', 'spec', 'exp', 'result']:
                st.session_state[key] = ""
            st.session_state.step = 1
            st.rerun()

st.divider()
st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")