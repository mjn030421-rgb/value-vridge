import streamlit as st
from google import genai
from google.genai import types
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# --- 피그마 기반 디자인 테마 (브랜드 블루 & 둥근 카드) ---
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    .stApp { background-color: #F9FAFB !important; font-family: 'Pretendard', sans-serif !important; }

    /* Hero Section (상단 그라디언트 & 이미지 효과) */
    .hero-section {
        background: linear-gradient(135deg, #4854e0 0%, #6b74e8 100%);
        padding: 60px 40px;
        border-radius: 0 0 40px 40px;
        color: white !important;
        text-align: center;
        margin: -60px -100px 40px -100px;
        box-shadow: 0 10px 30px rgba(72, 84, 224, 0.2);
    }
    .hero-title { font-size: 2.8rem !important; font-weight: 800 !important; color: white !important; margin-bottom: 10px; }
    .hero-sub { font-size: 1.1rem !important; color: rgba(255,255,255,0.9) !important; line-height: 1.6; }

    /* 피그마 스타일 둥근 카드 */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: white !important;
        border-radius: 30px !important;
        padding: 30px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #F3F4F6 !important;
        margin-bottom: 25px !important;
    }

    /* 모든 글자색 검정 고정 (오류 방지) */
    h2, h3, h4, p, span, label, div { color: #1F2937 !important; }
    
    /* 입력창 디자인 */
    input, textarea, [data-baseweb="input"] {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 16px !important;
        color: #1F2937 !important;
    }
    input::placeholder { color: #9CA3AF !important; }

    /* 피그마 그라디언트 버튼 */
    .stButton>button {
        background: linear-gradient(90deg, #4854e0 0%, #6b74e8 100%) !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(72, 84, 224, 0.3) !important;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(72, 84, 224, 0.4) !important; }

    /* 진행 바 스타일 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4854e0 0%, #6b74e8 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# API 설정
try: API_KEY = st.secrets["GEMINI_API_KEY"]
except: API_KEY = "YOUR_LOCAL_KEY"

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite" 

# [상태 관리] 초기화
if 'step' not in st.session_state: st.session_state.step = 1
if 'spec_list' not in st.session_state: st.session_state.spec_list = [""]
if 'has_no_spec' not in st.session_state: st.session_state.has_no_spec = False
for key in ['school', 'major', 'target', 'job', 'exp', 'result', 'keywords']:
    if key not in st.session_state: st.session_state[key] = ""

# [메인 로직]
with streamlit_analytics.track():
    # --- Hero Section (피그마 디자인) ---
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">VALUE BRIDGE</h1>
            <p class="hero-sub">진로 설계에 막막함을 느끼는 대학생 및 취준생을 위한<br>
            AI 기반 개인 맞춤형 커리어 로드맵 설계 솔루션</p>
        </div>
    """, unsafe_allow_html=True)

    st.progress(st.session_state.step / 4)

    # --- 1~3단계 입력 (디자인 반영) ---
    if st.session_state.step == 1:
        st.subheader("먼저, 당신의 소속을 알려주세요 🎓")
        st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
        st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        if st.button("내 가치 연결하기 →"):
            if st.session_state.school and st.session_state.major: st.session_state.step = 2; st.rerun()
            else: st.error("정보를 입력해 주세요.")

    elif st.session_state.step == 2:
        st.subheader("목표 기업과 보유 자격증을 입력하세요 🏢")
        st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target)
        st.session_state.job = st.text_input("🎯 목표 직무", value=st.session_state.job)
        st.session_state.has_no_spec = st.checkbox("보유한 자격증이 없습니다", value=st.session_state.has_no_spec)
        if not st.session_state.has_no_spec:
            for i in range(len(st.session_state.spec_list)):
                st.session_state.spec_list[i] = st.text_input(f"자격증 {i+1}", value=st.session_state.spec_list[i], key=f"s_{i}")
            if st.button("➕ 추가"): st.session_state.spec_list.append(""); st.rerun()
        if st.button("다음으로 →"):
            if st.session_state.target and st.session_state.job: st.session_state.step = 3; st.rerun()
            else: st.error("내용을 입력해 주세요.")

    elif st.session_state.step == 3:
        st.subheader("당신의 빛나는 경험을 들려주세요 ✨")
        st.session_state.exp = st.text_area("🌟 주요 경험", value=st.session_state.exp, height=200, placeholder="프로젝트, 인턴 등 당신의 경험을 적어주세요.")
        if st.button("가치 브릿지 생성 🚀"):
            if st.session_state.exp: st.session_state.step = 4; st.rerun()
            else: st.error("경험을 입력해 주세요.")

    # --- 4단계: 결과 (통합 프롬프트 + 피그마 카드 레이아웃) ---
    elif st.session_state.step == 4:
        if not st.session_state.result:
            with st.spinner(f"{st.session_state.target}의 데이터를 정밀 분석 중입니다..."):
                try:
                    spec_summary = "보유 자격증 없음" if st.session_state.has_no_spec else ", ".join([s for s in st.session_state.spec_list if s.strip()])
                    # 성현님의 통합 프롬프트 (자격증 검색 기능 강화형)
                    prompt = f"""
                    [역할 정의] 당신은 HR 컨설턴트 겸 애널리스트입니다. 
                    [필수 행동 지침] 
                    1. 구글 검색을 통해 {st.session_state.target}의 최신 신년사, 경영방침, 인재상을 조사하세요.
                    2. 지원자의 자격증({spec_summary})이 {st.session_state.job} 직무에서 어떤 실무 지식을 증명하는지 검색하여 '실무 언어'로 변환하세요.
                    [출력 형식]
                    - KEYWORD_DATA_START / END 사이 기업 키워드 요약
                    - REPORT_START / END 사이 상세 리포트 (당신 호칭 사용)
                    """
                    response = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearchRetrieval())])
                    )
                    full_text = response.text
                    st.session_state.result = full_text # 파싱 로직은 이전과 동일하게 적용
                except: st.error("분석 중 오류 발생")

        # 결과 UI (피그마 카드 배치)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### 👤 프로필\n**학교:** {st.session_state.school}\n**전공:** {st.session_state.major}")
        with col2:
            st.markdown(f"#### 🏢 기업 분석\n**목표:** {st.session_state.target}\n**직무:** {st.session_state.job}")

        st.info("💡 분석된 브릿지 키워드와 리포트를 확인하세요.")
        with st.expander("📄 상세 컨설팅 리포트 전체 보기", expanded=True):
            st.markdown(st.session_state.result)
        
        st.link_button("🎁 수요조사 참여하고 기프티콘 받기", "https://docs.google.com/forms/your_link")
        if st.button("🔄 다시 하기"):
            for k in ['school','major','target','job','exp','result']: st.session_state[k] = ""
            st.session_state.step = 1; st.rerun()

st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")