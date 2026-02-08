import streamlit as st
from google import genai
from google.genai import types
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# --- 디자인 테마 (CSS 수정: 배경 박스 제거, 버튼 스타일 분리) ---
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 기본 폰트 및 배경 */
    .stApp { background-color: #F9FAFB !important; font-family: 'Pretendard', sans-serif !important; }

    /* Hero Section - 글씨색 완전 하얀색 고정 */
    .hero-section {
        background: linear-gradient(135deg, #4854e0 0%, #6b74e8 100%);
        padding: 50px 30px;
        border-radius: 0 0 40px 40px;
        text-align: center;
        margin: -60px -100px 30px -100px;
        box-shadow: 0 10px 30px rgba(72, 84, 224, 0.2);
    }
    .hero-title { 
        font-size: 2.5rem !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important;
        margin-bottom: 10px; 
    }
    .hero-sub { 
        font-size: 1rem !important; 
        color: #FFFFFF !important;
        opacity: 0.9;
    }

    /* 커스텀 진행 바 스타일 */
    .progress-container {
        width: 100%;
        background-color: #E5E7EB;
        border-radius: 20px;
        margin-bottom: 25px;
        height: 12px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #4854e0 0%, #6b74e8 100%);
        border-radius: 20px;
        transition: width 0.5s ease-in-out;
    }
    .progress-text {
        text-align: right;
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 5px;
        font-weight: 600;
    }

    /* [중요 수정] 이제 'st.container(border=True)'를 쓴 곳만 카드로 변합니다 */
    /* 기존의 광범위한 div:has(div.stMarkdown) 규칙 삭제됨 */
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
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

    /* [수정] 자격증 체크박스 글씨 - 밝은 브랜드 컬러 */
    [data-testid="stCheckbox"] label p {
        color: #4854e0 !important; 
        font-weight: 700 !important;
        font-size: 1rem !important;
    }

    /* 1. 메인 버튼 (Primary) - 그라디언트 & 흰색 글씨 */
    [data-testid="baseButton-primary"] {
        background: linear-gradient(90deg, #4854e0 0%, #6b74e8 100%) !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100%;
        transition: 0.3s;
    }
    [data-testid="baseButton-primary"]:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 6px 20px rgba(72, 84, 224, 0.4) !important; 
    }

    /* 2. 서브 버튼 (Secondary - 자격증 추가용) - 투명 배경 & 보라색 글씨 */
    [data-testid="baseButton-secondary"] {
        background: transparent !important;
        border: 1px solid #4854e0 !important;
        color: #4854e0 !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        width: 100%;
    }
    [data-testid="baseButton-secondary"]:hover {
        background-color: #F5F7FF !important;
    }
    /* 버튼 내부 텍스트 색상 강제 지정 */
    [data-testid="baseButton-secondary"] p {
        color: #4854e0 !important;
    }

    /* [이전 버튼] 회색 스타일 (별도 처리) */
    div[data-testid="column"] .stButton>button:has(div:contains("이전")) {
        background: #F3F4F6 !important;
        color: #4B5563 !important;
        box-shadow: none !important;
        border: none !important;
    }
    div[data-testid="column"] .stButton>button:has(div:contains("이전")) p {
        color: #4B5563 !important;
    }

    /* 익스펜더(상세 리포트) 스타일 */
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E8EB !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    .stExpander details summary {
        color: #3182F6 !important;
        font-weight: 700 !important;
        background-color: #F9FAFB !important;
        border-radius: 16px !important;
        padding: 15px !important;
    }

    /* 결과 화면 카드 헤더 */
    .result-header {
        font-size: 1.1rem;
        font-weight: 800;
        color: #4854e0 !important;
        margin-bottom: 10px;
        border-bottom: 2px solid #F3F4F6;
        padding-bottom: 5px;
    }

    /* 요약 태그 스타일 */
    .summary-tag {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .tag-major { background-color: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; }
    .tag-corp { background-color: #F0FDF4; color: #16A34A; border: 1px solid #BBF7D0; }
    .tag-bridge { background-color: #FFF7ED; color: #EA580C; border: 1px solid #FED7AA; font-size: 1rem; padding: 8px 16px; }
    
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
for key in ['school', 'major', 'target', 'job', 'exp', 'result', 'summary_major', 'summary_corp', 'summary_bridge']:
    if key not in st.session_state: st.session_state[key] = ""

# [기능 함수] 커스텀 진행바 렌더링
def render_progress_bar(step, total_steps):
    percent = int((step / total_steps) * 100)
    st.markdown(f"""
        <div class="progress-text">{step} / {total_steps} 단계 진행 중 ({percent}%)</div>
        <div class="progress-container">
            <div class="progress-bar-fill" style="width: {percent}%;"></div>
        </div>
    """, unsafe_allow_html=True)

# [메인 로직]
with streamlit_analytics.track():
    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">VALUE BRIDGE</h1>
            <p class="hero-sub">AI 기반 개인 맞춤형 커리어 로드맵 설계 솔루션</p>
        </div>
    """, unsafe_allow_html=True)

    render_progress_bar(st.session_state.step, 4)

    # --- 1단계: 소속 정보 ---
    if st.session_state.step == 1:
        # [수정] 카드 디자인 적용 (border=True 사용)
        with st.container(border=True):
            st.subheader("먼저, 당신의 소속을 알려주세요 🎓")
            st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
            st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        if st.button("내 가치 연결하기 →", type="primary"):
            if st.session_state.school and st.session_state.major: st.session_state.step = 2; st.rerun()
            else: st.error("정보를 입력해 주세요.")

    # --- 2단계: 목표 및 자격증 ---
    elif st.session_state.step == 2:
        with st.container(border=True):
            st.subheader("어떤 기업에서 어떤 일을 하고 싶으신가요? 🏢")
            st.session_state.target = st.text_input("🏢 목표 기업", value=st.session_state.target, placeholder="예: 한국은행, 신한은행")
            st.session_state.job = st.text_input("🎯 목표 직무", value=st.session_state.job, placeholder="예: 금융상품 기획, 리스크 관리")
            
            # [수정] 배경 박스 없이 라벨만 깔끔하게 표시
            st.markdown("""
                <div style="font-size: 14px; font-weight: 400; color: #31333F; margin-bottom: 8px; margin-top: 20px;">
                📜 보유 자격증/어학 성적
                </div>
            """, unsafe_allow_html=True)
            
            st.session_state.has_no_spec = st.checkbox("보유한 자격증이 없습니다 (없음)", value=st.session_state.has_no_spec)
            
            if not st.session_state.has_no_spec:
                for i in range(len(st.session_state.spec_list)):
                    st.session_state.spec_list[i] = st.text_input(f"자격증 {i+1}", value=st.session_state.spec_list[i], key=f"s_{i}", label_visibility="collapsed", placeholder="예: AFPK, ADsP, 토익 900")
                
                # [수정] 버튼 스타일 변경 (type="secondary" -> 투명 배경/보라색 글씨)
                if st.button("＋ 자격증 추가", type="secondary"): 
                    st.session_state.spec_list.append("")
                    st.rerun()
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전"): st.session_state.step = 1; st.rerun()
        with col2:
            go_next = st.button("다음으로 →", type="primary")
            
        if go_next:
            if st.session_state.target and st.session_state.job: st.session_state.step = 3; st.rerun()
            else: st.error("목표 기업과 직무를 입력해 주세요.")

    # --- 3단계: 경험 기술 ---
    elif st.session_state.step == 3:
        with st.container(border=True):
            st.subheader("당신의 가장 빛나는 경험을 들려주세요 ✨")
            st.session_state.exp = st.text_area("🌟 주요 경험 및 활동", value=st.session_state.exp, height=200, placeholder="예: 프로젝트, 인턴십, 아르바이트 등 드러내고 싶은 경험")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전"): st.session_state.step = 2; st.rerun()
        with col2:
            create_report = st.button("가치 브릿지 생성 🚀", type="primary")
            
        if create_report:
            if st.session_state.exp: st.session_state.step = 4; st.rerun()
            else: st.error("경험 내용을 입력해 주세요.")

    # --- 4단계: 결과 리포트 (하얀 공백 박스 해결) ---
    elif st.session_state.step == 4:
        if not st.session_state.result:
            with st.spinner(f"{st.session_state.target}의 최신 데이터를 분석 중입니다..."):
                try:
                    spec_summary = "보유 자격증 없음" if st.session_state.has_no_spec else ", ".join([s for s in st.session_state.spec_list if s.strip()])
                    
                    # [프롬프트 유지]
                    prompt = f"""
                    [역할 정의]
                    당신은 대기업 및 금융권 채용을 정밀 분석하는 **'HR 컨설턴트 겸 애널리스트'**입니다. 구글 검색을 통해 목표 기업의 최신 동향과 보유 자격증의 실무적 가치를 조사하여 **[VALUE BRIDGE 리포트]**를 작성하세요.

                    [필수 행동 지침: 실시간 데이터 조사]
                    기업 데이터: {st.session_state.target}의 최신 신년사, 경영방침, 인재상, 비전을 검색하세요.
                    자격증 분석: {spec_summary}이(가) {st.session_state.job} 직무에서 어떤 실무 스킬로 쓰이는지 검색하세요.

                    [수행 원칙]
                    1. 호칭은 '당신'으로 통일하세요.
                    2. 모든 제목은 **굵게(Bold)** 처리하세요.
                    3. 세세한 항목 사이에는 반드시 줄바꿈을 넣어 가독성을 높이세요.
                    
                    [지원자 정보]
                    - 전공: {st.session_state.major}
                    - 기업: {st.session_state.target} / 직무: {st.session_state.job}
                    - 스펙: {spec_summary}
                    - 경험: {st.session_state.exp}

                    ----------------------------------------------------------------
                    [출력 형식] - **아래 형식을 정확히 지켜주세요**

                    [[SUMMARY_START]]
                    전공기반역량: {st.session_state.major} 기반 핵심 지식 (3~5개, 쉼표로 구분)
                    인재상핵심가치: 검색된 기업 인재상/가치 키워드 (3~5개, 쉼표로 구분)
                    브릿지단문키워드: 기업 가치와 개인 역량이 일치하는 핵심 키워드 (4~6개, 쉼표로 구분)
                    [[SUMMARY_END]]

                    [[REPORT_START]]
                    ## 1. 스펙 요약 (Fact Only)
                    **전공:** {st.session_state.major}
                    **보유 자격:** {spec_summary}
                    **핵심 경험:** {st.session_state.exp[:30]}...
                    
                    (줄바꿈)
                    ## 2. {st.session_state.target} 분석 (Evidence Only)
                    **인재상 및 핵심가치:** (검색된 내용)
                    **최신 신년사 및 전략:** (검색된 내용)
                    **직무 핵심 요구:** (검색된 내용)

                    (줄바꿈)
                    ## 3. 가치 연결 브릿지 리포트
                    
                    **키워드 1: {{Bridge Keyword}}**
                    - **회사 근거:** (실시간 검색 내용)
                    - **당신의 스펙 근거:** (지원자 정보 및 자격증 분석)
                    - **연결 논리:** (경제적/전략적 분석)
                    - **적용 시나리오:** (입사 후 포부)

                    (줄바꿈)
                    **키워드 2: {{Bridge Keyword}}**
                    - **회사 근거:** ...
                    - **당신의 스펙 근거:** ...
                    - **연결 논리:** ...
                    - **적용 시나리오:** ...
                    
                    (나머지 키워드도 동일하게 반복)
                    [[REPORT_END]]
                    """
                    
                    response = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearchRetrieval())])
                    )
                    full_text = response.text
                    
                    if "[[SUMMARY_START]]" in full_text:
                        summary_part = full_text.split("[[SUMMARY_START]]")[1].split("[[SUMMARY_END]]")[0]
                        for line in summary_part.split('\n'):
                            if "전공기반역량:" in line: st.session_state.summary_major = line.split(":", 1)[1].strip()
                            if "인재상핵심가치:" in line: st.session_state.summary_corp = line.split(":", 1)[1].strip()
                            if "브릿지단문키워드:" in line: st.session_state.summary_bridge = line.split(":", 1)[1].strip()
                    
                    if "[[REPORT_START]]" in full_text:
                        st.session_state.result = full_text.split("[[REPORT_START]]")[1].split("[[REPORT_END]]")[0].strip()
                    else:
                        st.session_state.result = full_text.strip()
                        
                except Exception as e:
                    st.error(f"분석 중 문제가 발생했습니다. (Error: {e})")
                    st.info("💡 팁: 잠시 후 다시 시도해 주세요.")

        # --- [결과 화면 UI: 불필요한 공백 제거] ---
        st.subheader("🎯 분석 결과 요약")

        # 1. 기본 정보 (카드 적용)
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("<div class='result-header'>👤 지원자 정보</div>", unsafe_allow_html=True)
                st.write(f"**학교/전공:** {st.session_state.school} {st.session_state.major}")
                st.write(f"**자격증:** {'없음' if st.session_state.has_no_spec else ', '.join(st.session_state.spec_list)}")
        with col2:
            with st.container(border=True):
                st.markdown("<div class='result-header'>🏢 목표 정보</div>", unsafe_allow_html=True)
                st.write(f"**기업명:** {st.session_state.target}")
                st.write(f"**직무:** {st.session_state.job}")

        # 2. 키워드 요약 (카드 적용)
        with st.container(border=True):
            st.markdown("<div class='result-header'>🔑 AI 분석 핵심 키워드</div>", unsafe_allow_html=True)
            
            k_col1, k_col2 = st.columns(2)
            with k_col1:
                st.markdown(f"**📘 {st.session_state.major} 핵심 역량**")
                if st.session_state.summary_major:
                    for tag in st.session_state.summary_major.split(','):
                        st.markdown(f"<span class='summary-tag tag-major'>{tag.strip()}</span>", unsafe_allow_html=True)
            
            with k_col2:
                st.markdown(f"**🏢 {st.session_state.target} 핵심 가치**")
                if st.session_state.summary_corp:
                    for tag in st.session_state.summary_corp.split(','):
                        st.markdown(f"<span class='summary-tag tag-corp'>{tag.strip()}</span>", unsafe_allow_html=True)

            st.markdown("---")
            
            st.markdown("**🚀 가치 연결 브릿지 키워드 (핵심)**")
            if st.session_state.summary_bridge:
                for tag in st.session_state.summary_bridge.split(','):
                    st.markdown(f"<span class='summary-tag tag-bridge'>{tag.strip()}</span>", unsafe_allow_html=True)
            else:
                st.info("데이터 분석 중입니다...")

        st.divider()

        st.markdown("### 📄 상세 컨설팅 리포트")
        with st.expander("리포트 전체 보기 (클릭하여 열기)", expanded=False):
            st.markdown(st.session_state.result)
        
        st.markdown("""
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSd7cYP6QwTthzoEdlAyObugotZWGOYgqk7eJ323tvspGA0AGA/viewform" target="_blank" class="gift-button">
            🎁 수요조사 참여하고 기프티콘 받기! (클릭)
            </a>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 처음부터 다시 하기"):
            for k in ['school','major','target','job','exp','result','summary_major','summary_corp','summary_bridge']: st.session_state[k] = ""
            st.session_state.spec_list = [""]; st.session_state.has_no_spec = False; st.session_state.step = 1; st.rerun()

st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")