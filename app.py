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
    .spec-container {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
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

# 2. [상태 관리] session_state 초기화
if 'step' not in st.session_state:
    st.session_state.step = 1
# 자격증 리스트를 위한 초기 설정 추가
if 'spec_list' not in st.session_state:
    st.session_state.spec_list = [""]
if 'has_no_spec' not in st.session_state:
    st.session_state.has_no_spec = False

for key in ['school', 'major', 'target', 'job', 'exp', 'result']:
    if key not in st.session_state:
        st.session_state[key] = ""

# 3. [추적] 모든 과정을 track()으로 감싸기
with streamlit_analytics.track():
    st.title("Value Bridge")
    
    # 진행 바
    st.progress(st.session_state.step / 4, text=f"{st.session_state.step} / 4 단계 진행 중")
    st.write("")

    # --- 1단계: 신원 정보 ---
    if st.session_state.step == 1:
        st.subheader("먼저, 소속을 알려주세요 🎓")
        st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
        st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        if st.button("다음으로", key="step1_next"):
            if st.session_state.school and st.session_state.major:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("모든 항목을 채워주세요!")

    # --- 2단계: 목표 및 다중 자격증 입력 ---
    elif st.session_state.step == 2:
        st.subheader("어디서 어떤 일을 하고 싶으신가요? 🏢")
        st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target, placeholder="예: 한국은행, 신한은행")
        st.session_state.job = st.text_input("🎯 목표 직무", value=st.session_state.job, placeholder="예: 금융상품 기획, 리스크 관리")
        
        st.write("---")
        st.write("📜 **보유 자격증/어학 성적**")
        
        # '없음' 체크박스
        st.session_state.has_no_spec = st.checkbox("보유한 자격증이 없습니다 (없음)", value=st.session_state.has_no_spec)
        
        if not st.session_state.has_no_spec:
            # 자격증 입력 칸들을 동적으로 생성
            for i in range(len(st.session_state.spec_list)):
                col_spec, col_del = st.columns([8, 1])
                with col_spec:
                    st.session_state.spec_list[i] = st.text_input(
                        f"자격증/어학 {i+1}", 
                        value=st.session_state.spec_list[i], 
                        placeholder="예: AFPK, ADsP, 토익 900",
                        key=f"spec_input_{i}"
                    )
            
            # 자격증 추가 버튼
            if st.button("➕ 자격증 추가", key="add_spec_btn"):
                st.session_state.spec_list.append("")
                st.rerun()
        
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
                                          placeholder="예: 노동경제학 프로젝트에서 파이썬 데이터 분석을 활용, 인턴쉽 , 아르바이트 , 드러내고 싶은 경험", height=200)
        
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
        st.subheader("🎯 성현님의 직무 맞춤형 리포트")
        
        with st.spinner("AI 분석 리포트를 생성 중입니다..."):
            try:
                if not st.session_state.result:
                    # 자격증 텍스트 정리
                    if st.session_state.has_no_spec:
                        spec_summary = "보유 자격증 없음"
                    else:
                        valid_specs = [s for s in st.session_state.spec_list if s.strip()]
                        spec_summary = ", ".join(valid_specs) if valid_specs else "보유 자격증 없음"

                    prompt = f"""
                    취업 전문가로서 다음 지원자의 정보를 분석하여 {st.session_state.target} {st.session_state.job} 직무 전략을 세워주세요.
                    
                    [지원자 정보]
                    - 전공: {st.session_state.major}
                    - 보유 스펙: {spec_summary}
                    - 핵심 경험: {st.session_state.exp}
                    
                    [요구사항]
                    1. 지원자의 경험과 전공 지식이 {st.session_state.job} 직무에 어떻게 기여할지 5가지 핵심 역량으로 도출하세요.
                    2. 만약 자격증이 없다면('보유 자격증 없음'), 현재 경험만으로 어떻게 직무 전문성을 어필할지 구체적인 자소서 작성 방향을 제시하세요.
                    3. 자격증이 있다면, 해당 자격증 지식과 실무 경험을 어떻게 연결할지 전략을 세우세요.
                    4. {st.session_state.target}의 인재상과 신년사 직무 특성 직접 검색하고 반영하여 전문적인 톤으로 답변하세요.
                    """
                    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                    st.session_state.result = response.text
                
                st.markdown(f"### **{st.session_state.target} | {st.session_state.job}**")
                st.info(st.session_state.result)
                
                st.divider()
                st.link_button("수요조사 참여하고 알림 받기", "https://forms.gle/your_link")
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

        if st.button("처음부터 다시 하기"):
            for key in ['school', 'major', 'target', 'job', 'spec', 'exp', 'result']:
                st.session_state[key] = ""
            st.session_state.spec_list = [""]
            st.session_state.has_no_spec = False
            st.session_state.step = 1
            st.rerun()

st.divider()
st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")