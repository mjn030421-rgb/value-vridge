import streamlit as st
from google import genai
from google.genai import types
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# --- 디자인 테마 (CSS 수정: 여백 제거 및 버튼 스타일 개선) ---
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 기본 폰트 및 배경 */
    .stApp { background-color: #F9FAFB !important; font-family: 'Pretendard', sans-serif !important; }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #4854e0 0%, #6b74e8 100%);
        padding: 50px 30px;
        border-radius: 0 0 40px 40px;
        color: white !important;
        text-align: center;
        margin: -60px -100px 30px -100px;
        box-shadow: 0 10px 30px rgba(72, 84, 224, 0.2);
    }
    .hero-title { font-size: 2.5rem !important; font-weight: 800 !important; color: white !important; margin-bottom: 10px; }
    .hero-sub { font-size: 1rem !important; color: rgba(255,255,255,0.9) !important; }

    /* 둥근 카드 스타일 (여백 최적화) */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: white !important;
        border-radius: 24px !important;
        padding: 24px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #F3F4F6 !important;
        margin-bottom: 20px !important;
    }

    /* 텍스트 색상 (검정 고정) */
    h2, h3, h4, p, span, label, div { color: #1F2937 !important; }
    
    /* 입력창 디자인 */
    input, textarea, [data-baseweb="input"] {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        color: #1F2937 !important;
    }
    input::placeholder { color: #9CA3AF !important; }

    /* [메인 버튼] 보라색 그라디언트 */
    .stButton>button {
        background: linear-gradient(90deg, #4854e0 0%, #6b74e8 100%) !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 6px 20px rgba(72, 84, 224, 0.4) !important; 
    }

    /* [이전 버튼] 회색 스타일 (Secondary) */
    div[data-testid="column"] .stButton>button:has(div:contains("이전")) {
        background: #F3F4F6 !important;
        color: #4B5563 !important;
        box-shadow: none !important;
    }

    /* 결과 화면 카드 헤더 */
    .result-header {
        font-size: 1.1rem;
        font-weight: 800;
        color: #4854e0 !important;
        margin-bottom: 12px;
        border-bottom: 2px solid #F3F4F6;
        padding-bottom: 8px;
    }

    /* 기프티콘 버튼 스타일 (밝은 민트/블루) */
    .gift-button {
        display: block;
        width: 100%;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #005F4F;
        text-align: center;
        padding: 15px;
        border-radius: 16px;
        text-decoration: none;
        font-weight: 800;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(0, 201, 255, 0.3);
        transition: 0.3s;
    }
    .gift-button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 201, 255, 0.4);
        color: #004D40;
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
    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">VALUE BRIDGE</h1>
            <p class="hero-sub">AI 기반 개인 맞춤형 커리어 로드맵 설계 솔루션</p>
        </div>
    """, unsafe_allow_html=True)

    st.progress(st.session_state.step / 4)

    # --- 1단계: 소속 정보 ---
    if st.session_state.step == 1:
        st.subheader("먼저, 당신의 소속을 알려주세요 🎓")
        st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
        st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        st.write("") # 간격 조정
        if st.button("내 가치 연결하기 →"):
            if st.session_state.school and st.session_state.major: st.session_state.step = 2; st.rerun()
            else: st.error("정보를 입력해 주세요.")

    # --- 2단계: 목표 및 자격증 (빈 공간 수정됨) ---
    elif st.session_state.step == 2:
        st.subheader("목표 기업과 보유 자격증을 입력하세요 🏢")
        
        # 불필요한 컨테이너 분리 없이 깔끔하게 배치
        st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target)
        st.session_state.job = st.text_input("🎯 목표 직무", value=st.session_state.job)
        
        # 빈 공간을 만들던 st.write("---") 제거함
        st.write("") 
        st.markdown("##### 📜 자격증 / 어학")
        st.session_state.has_no_spec = st.checkbox("보유한 자격증이 없습니다", value=st.session_state.has_no_spec)
        
        if not st.session_state.has_no_spec:
            for i in range(len(st.session_state.spec_list)):
                st.session_state.spec_list[i] = st.text_input(f"자격증 {i+1}", value=st.session_state.spec_list[i], key=f"s_{i}", label_visibility="collapsed", placeholder="자격증 명을 입력하세요")
            if st.button("➕ 자격증 추가"): st.session_state.spec_list.append(""); st.rerun()
            
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전 단계"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("다음으로 →"):
                if st.session_state.target and st.session_state.job: st.session_state.step = 3; st.rerun()
                else: st.error("기업과 직무를 입력해 주세요.")

    # --- 3단계: 경험 기술 ---
    elif st.session_state.step == 3:
        st.subheader("당신의 빛나는 경험을 들려주세요 ✨")
        st.session_state.exp = st.text_area("🌟 주요 경험", value=st.session_state.exp, height=200, placeholder="프로젝트, 인턴, 대외활동 등 직무와 관련된 경험을 자유롭게 적어주세요.")
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전 단계"): st.session_state.step = 2; st.rerun()
        with col2:
            if st.button("가치 브릿지 생성 🚀"):
                if st.session_state.exp: st.session_state.step = 4; st.rerun()
                else: st.error("경험 내용을 입력해 주세요.")

    # --- 4단계: 결과 리포트 (오류 메시지 구체화) ---
    elif st.session_state.step == 4:
        if not st.session_state.result:
            with st.spinner(f"{st.session_state.target}의 최신 데이터를 분석 중입니다..."):
                try:
                    spec_summary = "보유 자격증 없음" if st.session_state.has_no_spec else ", ".join([s for s in st.session_state.spec_list if s.strip()])
                    
                    prompt = f"""
                    [역할 정의] 당신은 HR 컨설턴트입니다.
                    [지침] 
                    1. 구글 검색으로 {st.session_state.target}의 최신 신년사, 경영방침, 인재상을 조사하세요.
                    2. 지원자 자격증({spec_summary})이 {st.session_state.job} 직무에서 어떤 '실무 스킬'로 쓰이는지 검색하여 변환하세요.
                    
                    [출력 형식]
                    1. 'KEYWORD_DATA_START'와 'KEYWORD_DATA_END' 사이에 기업의 [신년사 키워드 / 비전 / 인재상 / 핵심가치]를 핵심 단어 위주로 나열하세요.
                    2. 'REPORT_START'와 'REPORT_END' 사이에 상세 리포트를 작성하세요. (호칭: 당신)
                    """
                    
                    response = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearchRetrieval())])
                    )
                    full_text = response.text
                    
                    if "KEYWORD_DATA_START" in full_text:
                        st.session_state.keywords = full_text.split("KEYWORD_DATA_START")[1].split("KEYWORD_DATA_END")[0].strip()
                        st.session_state.result = full_text.split("REPORT_START")[1].split("REPORT_END")[0].strip()
                    else:
                        st.session_state.result = full_text
                except Exception as e:
                    # [수정됨] 단순 오류 메시지 대신 실제 에러 내용을 출력하여 원인 파악
                    st.error(f"분석 중 문제가 발생했습니다. (Error: {e})")
                    st.info("💡 팁: API 키가 올바른지 확인하거나, 잠시 후 다시 시도해 주세요.")

        # --- 결과 화면 ---
        if st.session_state.result:
            st.subheader("🎯 분석 결과 요약")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div class='result-header'>👤 지원자 정보</div>", unsafe_allow_html=True)
                st.write(f"**학교/전공:** {st.session_state.school} {st.session_state.major}")
                st.write(f"**자격증:** {'없음' if st.session_state.has_no_spec else ', '.join(st.session_state.spec_list)}")
                st.write(f"**핵심 경험:** {st.session_state.exp[:30]}...")

            with col2:
                st.markdown("<div class='result-header'>🏢 목표 기업/직무</div>", unsafe_allow_html=True)
                st.write(f"**기업명:** {st.session_state.target}")
                st.write(f"**지원 직무:** {st.session_state.job}")

            st.write("")
            with st.container():
                st.markdown("<div class='result-header'>🔑 AI가 수집한 기업 핵심 키워드</div>", unsafe_allow_html=True)
                st.info(st.session_state.keywords if st.session_state.keywords else "기업 데이터 분석 완료")

            st.divider()

            st.markdown("### 📄 상세 컨설팅 리포트")
            with st.expander("리포트 전체 보기 (클릭)", expanded=True):
                st.markdown(st.session_state.result)
            
            st.write("")
            # [수정됨] 밝은 민트색 기프티콘 버튼
            st.markdown("""
                <a href="https://docs.google.com/forms/d/e/1FAIpQLSd7cYP6QwTthzoEdlAyObugotZWGOYgqk7eJ323tvspGA0AGA/viewform" target="_blank" class="gift-button">
                🎁 수요조사 참여하고 기프티콘 받기! (클릭)
                </a>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button("🔄 처음부터 다시 하기"):
                for k in ['school','major','target','job','exp','result','keywords']: st.session_state[k] = ""
                st.session_state.spec_list = [""]; st.session_state.has_no_spec = False; st.session_state.step = 1; st.rerun()

st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")