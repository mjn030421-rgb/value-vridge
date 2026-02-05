import streamlit as st
from google import genai
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정 및 API 연결
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# 디자인 테마 (애플/토스 감성 유지)
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
    h1, h2, h3 { color: #191F28 !important; font-weight: 800 !important; }
    p { color: #4E5968 !important; }
    </style>
    """, unsafe_allow_html=True)

# API 설정
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "YOUR_LOCAL_KEY_HERE" 

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite" 

# 2. [상태 관리] session_state 초기화 ('job' 추가됨)
if 'step' not in st.session_state:
    st.session_state.step = 1
for key in ['school', 'major', 'target', 'job', 'spec', 'exp', 'result']:
    if key not in st.session_state:
        st.session_state[key] = ""

# 3. [추적] 모든 과정을 track()으로 감싸기
with streamlit_analytics.track():
    st.title("🌉 Value Bridge")
    
    # 진행 바
    progress_text = f"{st.session_state.step} / 4 단계 진행 중"
    st.progress(st.session_state.step / 4, text=progress_text)
    st.write("")

    # --- 1단계: 신원 정보 ---
    if st.session_state.step == 1:
        st.subheader("먼저, 소속을 알려주세요 🎓")
        st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
        st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        st.write("")
        if st.button("다음으로", key="step1_next"):
            if st.session_state.school and st.session_state.major:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("모든 항목을 채워주세요!")

    # --- 2단계: 목표 및 직무 추가 ---
    elif st.session_state.step == 2:
        st.subheader("어디서 어떤 일을 하고 싶으신가요? 🏢")
        st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target, placeholder="예: 한국은행, 신한은행")
        st.session_state.job = st.text_input("🎯 목표 직무", value=st.session_state.job, placeholder="예: 금융상품 기획, 디지털 뱅킹, 리스크 관리")
        st.session_state.spec = st.text_input("📜 보유 자격증/어학", value=st.session_state.spec, placeholder="예: AFPK, 토익 900")
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("다음으로", key="step2_next"):
                if st.session_state.target and st.session_state.job:
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("목표 기업과 직무를 모두 입력해 주세요.")

    # --- 3단계: 경험 기술 ---
    elif st.session_state.step == 3:
        st.subheader("가장 빛나는 경험을 들려주세요 ✨")
        st.session_state.exp = st.text_area("🌟 주요 경험 및 활동", value=st.session_state.exp, 
                                          placeholder="예: 노동경제학 수업 중 파이썬을 활용해 실업률 상관관계 분석 프로젝트 수행", height=200)
        
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

    # --- 4단계: 결과 리포트 (프롬프트 강화) ---
    elif st.session_state.step == 4:
        st.subheader("🎯 성현님의 직무 맞춤형 리포트")
        
        with st.spinner(f"AI가 {st.session_state.target} {st.session_state.job} 직무 역량을 분석 중입니다..."):
            try:
                if not st.session_state.result:
                    # 기업 + 직무 + 전공을 결합한 강화된 프롬프트
                    prompt = f"""
                    당신은 채용 전문가입니다. 다음 정보를 바탕으로 취업 전략을 세워주세요.
                    
                    1. 목표: {st.session_state.target} (기업) / {st.session_state.job} (직무)
                    2. 지원자 배경: {st.session_state.major} 전공, {st.session_state.spec} 보유
                    3. 핵심 경험: {st.session_state.exp}
                    
                    [요구사항]
                    - 위 경험을 {st.session_state.job} 직무에 필요한 핵심 역량 키워드 5개로 변환하세요.
                    - {st.session_state.major} 전공 지식이 {st.session_state.job} 직무에서 어떻게 무기가 될지 자소서 팁을 알려주세요.
                    - 답변은 깔끔한 불렛포인트 형식으로 작성하세요.
                    """
                    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                    st.session_state.result = response.text
                
                st.markdown(f"### **{st.session_state.target} | {st.session_state.job}**")
                st.info(st.session_state.result)
                
                st.divider()
                st.link_button("수요조사 참여하고 정식 버전 알림 받기", "https://forms.gle/your_link")
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

        if st.button("처음부터 다시 하기"):
            for key in ['school', 'major', 'target', 'job', 'spec', 'exp', 'result']:
                st.session_state[key] = ""
            st.session_state.step = 1
            st.rerun()

st.divider()
st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")