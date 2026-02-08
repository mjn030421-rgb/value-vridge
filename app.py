import streamlit as st
from google import genai
from google.genai import types
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# --- 디자인 테마 (CSS: 버튼 가독성, 익스펜더 스타일, 빈 공간 제거) ---
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

    /* 둥근 카드 스타일 */
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

    /* [수정됨] 버튼 스타일 - 글씨색 흰색 강제 고정 (#FFFFFF) */
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
    /* 버튼 내부의 모든 텍스트 요소도 흰색으로 강제 */
    .stButton>button * {
        color: #FFFFFF !important;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 6px 20px rgba(72, 84, 224, 0.4) !important; 
        color: #FFFFFF !important;
    }

    /* [이전 버튼] 회색 스타일 */
    div[data-testid="column"] .stButton>button:has(div:contains("이전")) {
        background: #F3F4F6 !important;
        color: #4B5563 !important; /* 회색 글씨 */
        box-shadow: none !important;
    }
    div[data-testid="column"] .stButton>button:has(div:contains("이전")) * {
        color: #4B5563 !important;
    }

    /* [수정됨] 익스펜더(상세 리포트) 스타일 - 밝은 배경 */
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E8EB !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    .stExpander details summary {
        color: #3182F6 !important; /* 파란색 글씨 */
        font-weight: 700 !important;
        background-color: #F9FAFB !important; /* 아주 연한 회색 헤더 */
        border-radius: 16px !important;
    }
    .stExpander details summary:hover {
        color: #1B64DA !important;
        background-color: #F0F4FF !important;
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

    /* 요약 태그 스타일 */
    .summary-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .tag-major { background-color: #E0E7FF; color: #4338CA; }
    .tag-corp { background-color: #DCFCE7; color: #15803D; }
    .tag-bridge { background-color: #FFEDD5; color: #C2410C; border: 1px solid #F97316; }
    
    /* 기프티콘 버튼 */
    .gift-button {
        display: block; width: 100%;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #005F4F; text-align: center; padding: 15px;
        border-radius: 16px; text-decoration: none; font-weight: 800;
        font-size: 1.1rem; box-shadow: 0 4px 15px rgba(0, 201, 255, 0.3);
        transition: 0.3s;
    }
    .gift-button:hover { transform: scale(1.02); color: #004D40; }
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
# 데이터 파싱용 변수 추가
for key in ['school', 'major', 'target', 'job', 'exp', 'result', 'summary_major', 'summary_corp', 'summary_bridge']:
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
        
        if st.button("내 가치 연결하기 →"):
            if st.session_state.school and st.session_state.major: st.session_state.step = 2; st.rerun()
            else: st.error("정보를 입력해 주세요.")

    # --- 2단계: 목표 및 자격증 ---
    elif st.session_state.step == 2:
        st.subheader("목표 기업과 보유 자격증을 입력하세요 🏢")
        st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target)
        st.session_state.job = st.text_input("🎯 목표 직무", value=st.session_state.job)
        
        st.markdown("##### 📜 자격증 / 어학")
        st.session_state.has_no_spec = st.checkbox("보유한 자격증이 없습니다", value=st.session_state.has_no_spec)
        
        if not st.session_state.has_no_spec:
            for i in range(len(st.session_state.spec_list)):
                st.session_state.spec_list[i] = st.text_input(f"자격증 {i+1}", value=st.session_state.spec_list[i], key=f"s_{i}", label_visibility="collapsed", placeholder="자격증 명을 입력하세요")
            if st.button("➕ 자격증 추가"): st.session_state.spec_list.append(""); st.rerun()
            
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
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전 단계"): st.session_state.step = 2; st.rerun()
        with col2:
            if st.button("가치 브릿지 생성 🚀"):
                if st.session_state.exp: st.session_state.step = 4; st.rerun()
                else: st.error("경험 내용을 입력해 주세요.")

    # --- 4단계: 결과 리포트 (통합 프롬프트 + 요약 파싱 적용) ---
    elif st.session_state.step == 4:
        if not st.session_state.result:
            with st.spinner(f"{st.session_state.target}의 데이터를 정밀 분석 중입니다..."):
                try:
                    spec_summary = "보유 자격증 없음" if st.session_state.has_no_spec else ", ".join([s for s in st.session_state.spec_list if s.strip()])
                    
                    # [성현님 요청: 최종 통합 분석 프롬프트 (검색 기능 강화형)]
                    # 요약 섹션을 파싱하기 위해 구분자([[SECTION]])를 추가했습니다.
                    prompt = f"""
                    [역할 정의]
                    당신은 대기업 및 금융권 채용을 정밀 분석하는 **'HR 컨설턴트 겸 애널리스트'**입니다. 당신의 임무는 지원자의 스펙을 요약하고, 구글 검색을 통해 목표 기업의 최신 동향과 보유 자격증의 실무적 가치를 직접 조사하여 둘을 논리적으로 연결하는 **[VALUE BRIDGE 리포트]**를 작성하는 것입니다.

                    [필수 행동 지침: 실시간 데이터 조사]
                    기업 데이터 조사: 분석 시작 전, 반드시 구글 검색을 통해 {st.session_state.target}의 최신 신년사, 경영방침, 인재상, 비전, 핵심가치를 직접 조사하세요. 검색된 실제 문장을 근거로 사용해야 합니다.
                    자격증 실무 가치 조사: 지원자가 입력한 각 자격증이 해당 직무에서 구체적으로 어떤 업무에 쓰이는지, 어떤 기술적/법률적 지식을 증명하는지 구글에서 검색하세요. 이를 바탕으로 자격증을 '실무 스킬'로 변환하여 기술하세요.

                    [수행 원칙]
                    호칭 통일: 모든 문장에서 지원자를 반드시 **'당신'**으로 지칭합니다.
                    사실 기반: 추상적인 수식어(성실, 열정 등)를 배제하고 데이터와 행동 중심으로 기술합니다.
                    회사 관점: 지원자의 역량이 회사의 이익과 현재 과제 해결에 어떻게 기여할지 철저히 회사 입장에서 판단합니다.
                    표준화: 모든 역량 키워드는 반드시 직무 현장에서 평가 가능한 **'직무 언어'**로 변환합니다.
                    
                    [지원자 정보]
                    - 전공: {st.session_state.major}
                    - 기업: {st.session_state.target} / 직무: {st.session_state.job}
                    - 스펙: {spec_summary}
                    - 경험: {st.session_state.exp}

                    ----------------------------------------------------------------
                    [작업 절차 및 출력 형식] - **반드시 이 형식을 지켜주세요**

                    먼저, 상단 요약용 데이터를 아래 구분자 사이에 작성하세요.
                    [[SUMMARY_START]]
                    전공기반역량: {st.session_state.major} 기반의 핵심 지식 및 도구 활용 능력 (3~5개, 쉼표로 구분)
                    인재상핵심가치: 실시간 검색된 기업의 인재상/가치 실제 문구와 키워드 (3~5개, 쉼표로 구분)
                    브릿지단문키워드: 기업 가치와 개인 역량이 일치하는 핵심 키워드 (4~6개, 쉼표로 구분)
                    [[SUMMARY_END]]

                    그 다음, 상세 리포트를 아래 구분자 사이에 작성하세요.
                    [[REPORT_START]]
                    [VALUE BRIDGE 리포트]
                    1) 스펙 요약 (Fact Only)
                    ... (상세 내용 작성)
                    
                    2) 지원 회사/직무 요약 (Evidence Only)
                    ... (상세 내용 작성)

                    3) 브릿지 단문 키워드 (4~6개)
                    [키워드 리스트]

                    4) 브릿지 키워드 연결 리포트
                    키워드: {{Bridge Keyword}}
                    회사 근거: ...
                    당신의 스펙 근거: ...
                    연결 논리: ...
                    당신의 적용 시나리오: ...
                    [[REPORT_END]]
                    """
                    
                    response = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearchRetrieval())])
                    )
                    full_text = response.text
                    
                    # [데이터 파싱 로직]
                    # 1. 요약 데이터 추출
                    if "[[SUMMARY_START]]" in full_text:
                        summary_part = full_text.split("[[SUMMARY_START]]")[1].split("[[SUMMARY_END]]")[0]
                        for line in summary_part.split('\n'):
                            if "전공기반역량:" in line: st.session_state.summary_major = line.split(":", 1)[1].strip()
                            if "인재상핵심가치:" in line: st.session_state.summary_corp = line.split(":", 1)[1].strip()
                            if "브릿지단문키워드:" in line: st.session_state.summary_bridge = line.split(":", 1)[1].strip()
                    
                    # 2. 리포트 본문 추출
                    if "[[REPORT_START]]" in full_text:
                        st.session_state.result = full_text.split("[[REPORT_START]]")[1].split("[[REPORT_END]]")[0].strip()
                    else:
                        st.session_state.result = full_text.strip()
                        
                except Exception as e:
                    st.error(f"분석 중 문제가 발생했습니다. (Error: {e})")
                    st.info("💡 팁: 잠시 후 다시 시도해 주세요.")

        # --- [결과 화면 UI 구성] ---
        st.subheader("🎯 분석 결과 요약")

        # 1. 기본 정보 카드 (2열)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='result-header'>👤 지원자 정보</div>", unsafe_allow_html=True)
            st.write(f"**학교/전공:** {st.session_state.school} {st.session_state.major}")
            st.write(f"**자격증:** {'없음' if st.session_state.has_no_spec else ', '.join(st.session_state.spec_list)}")
            st.write(f"**경험:** {st.session_state.exp[:20]}...")

        with col2:
            st.markdown("<div class='result-header'>🏢 목표 정보</div>", unsafe_allow_html=True)
            st.write(f"**기업명:** {st.session_state.target}")
            st.write(f"**직무:** {st.session_state.job}")
            st.info("✅ 2026 신년사 및 인재상 분석 완료")

        # 2. [NEW] 핵심 요약 존 (노란색 빈 공간 대체)
        # 빈 공간 대신, 파싱한 핵심 키워드들을 예쁘게 보여줍니다.
        st.markdown("")
        with st.container():
            st.markdown("<div class='result-header'>🔑 AI 분석 핵심 키워드</div>", unsafe_allow_html=True)
            
            # 전공 역량
            st.caption(f"📘 {st.session_state.major} 핵심 역량")
            if st.session_state.summary_major:
                for tag in st.session_state.summary_major.split(','):
                    st.markdown(f"<span class='summary-tag tag-major'>{tag.strip()}</span>", unsafe_allow_html=True)
            
            st.markdown("")
            # 기업 가치
            st.caption(f"🏢 {st.session_state.target} 핵심 가치 (Real-time)")
            if st.session_state.summary_corp:
                for tag in st.session_state.summary_corp.split(','):
                    st.markdown(f"<span class='summary-tag tag-corp'>{tag.strip()}</span>", unsafe_allow_html=True)

            st.markdown("")
            # 브릿지 키워드 (강조)
            st.caption("🚀 가치 연결 브릿지 키워드")
            if st.session_state.summary_bridge:
                for tag in st.session_state.summary_bridge.split(','):
                    st.markdown(f"<span class='summary-tag tag-bridge'>{tag.strip()}</span>", unsafe_allow_html=True)
            else:
                st.info("데이터 분석 중입니다...")

        st.divider()

        # 3. 상세 리포트 (밝은 익스펜더 적용)
        st.markdown("### 📄 상세 컨설팅 리포트")
        # 프롬프트 그대로 자세한 내용이 들어있는 리포트
        with st.expander("리포트 전체 보기 (클릭하여 열기/닫기)", expanded=True):
            st.markdown(st.session_state.result)
        
        st.write("")
        # 기프티콘 버튼
        st.markdown("""
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSd7cYP6QwTthzoEdlAyObugotZWGOYgqk7eJ323tvspGA0AGA/viewform" target="_blank" class="gift-button">
            🎁 수요조사 참여하고 기프티콘 받기! (클릭)
            </a>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("🔄 처음부터 다시 하기"):
            for k in ['school','major','target','job','exp','result','summary_major','summary_corp','summary_bridge']: st.session_state[k] = ""
            st.session_state.spec_list = [""]; st.session_state.has_no_spec = False; st.session_state.step = 1; st.rerun()

st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")