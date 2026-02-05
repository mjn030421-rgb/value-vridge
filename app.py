import streamlit as st
from google import genai
from google.genai import types # 실시간 검색 도구 활용을 위해 필요
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정 및 API 연결
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# 디자인 테마 (애플/토스 감성)
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
    p { color: #4E5968 !important; line-height: 1.6; }
    .intro-box {
        background-color: #F0F7FF;
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 5px solid #3182F6;
        margin-bottom: 2rem;
    }
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

    # --- 1단계: 서비스 정의 및 신원 정보 ---
    if st.session_state.step == 1:
        st.subheader("경험을 기업의 언어로 연결하다")
        st.markdown("""
        <div class="intro-box">
            <strong>Value Bridge란?</strong><br>
            당신이 대학 생활 동안 쌓아온 소중한 경험들을 목표 기업의 <b>실시간 인재상, 최신 신년사, 비전</b>과 매칭해드리는 AI 분석 서비스입니다. 
            단순한 요약을 넘어, 기업이 지금 이 순간 원하는 '핵심 역량'으로 성현님의 가치를 재해석합니다.
        </div>
        """, unsafe_allow_html=True)

        st.write("먼저, 성현님의 소속을 알려주세요 🎓")
        st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
        st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        if st.button("내 가치 연결하기 →", key="step1_next"):
            if st.session_state.school and st.session_state.major:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("모든 항목을 채워주세요!")

    # --- 2단계: 목표 및 동적 자격증 입력 ---
    elif st.session_state.step == 2:
        st.subheader("어디서 어떤 일을 하고 싶으신가요? 🏢")
        st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target, placeholder="예: 한국은행, 신한은행")
        st.session_state.job = st.text_input("🎯 목표 직무", value=st.session_state.job, placeholder="예: 금융상품 기획, 리스크 관리")
        
        st.write("---")
        st.write("📜 **보유 자격증/어학 성적**")
        st.session_state.has_no_spec = st.checkbox("보유한 자격증이 없습니다 (없음)", value=st.session_state.has_no_spec)
        
        if not st.session_state.has_no_spec:
            for i in range(len(st.session_state.spec_list)):
                st.session_state.spec_list[i] = st.text_input(
                    f"자격증/어학 {i+1}", 
                    value=st.session_state.spec_list[i], 
                    key=f"spec_input_{i}"
                )
            if st.button("➕ 자격증 추가"):
                st.session_state.spec_list.append("")
                st.rerun()
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("다음으로 →"):
                if st.session_state.target and st.session_state.job:
                    st.session_state.step = 3; st.rerun()
                else: st.error("목표 기업과 직무를 입력해 주세요.")

    # --- 3단계: 경험 기술 ---
    elif st.session_state.step == 3:
        st.subheader("가장 빛나는 경험을 들려주세요 ✨")
        st.session_state.exp = st.text_area("🌟 주요 경험 및 활동", value=st.session_state.exp, 
                                          placeholder="예: 노동경제학 프로젝트에서 파이썬 데이터 분석을 활용, 인턴쉽 , 아르바이트 , 드러내고 싶은 경험", height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전"): st.session_state.step = 2; st.rerun()
        with col2:
            if st.button("가치 브릿지 생성 🚀"):
                if st.session_state.exp:
                    st.session_state.step = 4; st.rerun()
                else: st.error("경험을 적어주세요.")

    # --- 4단계: 실시간 검색 기반 결과 리포트 ---
    elif st.session_state.step == 4:
        st.subheader("🎯 맞춤형 역량 브릿지 리포트")
        
        with st.spinner(f"{st.session_state.target}의 최신 신년사와 인재상을 검색하여 분석 중입니다..."):
            try:
                if not st.session_state.result:
                    spec_summary = "보유 자격증 없음" if st.session_state.has_no_spec else ", ".join([s for s in st.session_state.spec_list if s.strip()])
                    
                    # 실시간 검색 및 심층 분석을 위한 강화된 프롬프트
                    prompt = f"""
                    당신은 채용 전략가이자 검색 전문가입니다. 
                    먼저 구글 검색을 통해 {st.session_state.target}의 '2026년 신년사', '인재상', '핵심가치'를 직접 확인하세요.
                    그 정보들을 바탕으로 아래 지원자의 경험을 분석하여 '브릿지 리포트'를 작성하세요.

                    [지원자 정보]
                    - 소속: {st.session_state.school} {st.session_state.major}
                    - 지원 직무: {st.session_state.job}
                    - 스펙: {spec_summary}
                    - 경험: {st.session_state.exp}

                    [분석 가이드]
                    1. **기업 동향 매칭**: {st.session_state.target}이 올해 신년사, 인재상 , 가치 , 비전에서 강조한 키워드와 지원자의 경험을 연결하세요.
                    2. **역량 키워드 5선**: 직무에 최적화된 핵심 키워드 5개를 뽑고 그 이유를 기술하세요.
                    3. **전공자용 자소서 팁**: {st.session_state.major} 전공 지식이 실무에서 어떻게 발휘될지 조언하세요.
                    4. **직무 전략**: 자격증 여부에 따른 맞춤형 어필 전략을 포함하세요.
                    """
                    
                    # 실시간 구글 검색 도구 활성화 (Grounding)
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
                        )
                    )
                    st.session_state.result = response.text
                
                st.markdown(f"### **{st.session_state.target} | {st.session_state.job} 분석**")
                st.info(st.session_state.result)
                
                st.divider()
                st.link_button("수요조사 참여하고 분석 결과 저장하기", "https://forms.gle/your_link")
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

        if st.button("처음부터 다시 하기"):
            for k in ['school','major','target','job','exp','result']: st.session_state[k] = ""
            st.session_state.spec_list = [""]; st.session_state.has_no_spec = False; st.session_state.step = 1; st.rerun()

st.divider()
st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")