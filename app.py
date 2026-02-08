import streamlit as st
from google import genai
from google.genai import types
import streamlit_analytics2 as streamlit_analytics

# 1. [설정] 페이지 설정
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# --- 디자인 테마 (PPT 스타일 둥근 카드 & 가독성 최적화) ---
st.markdown("""
    <style>
    /* 전체 배경 흰색 고정 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 1. 텍스트 가독성 (진한 검정) */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown {
        color: #191F28 !important;
        font-family: 'Pretendard', sans-serif !important;
    }
    
    /* 2. PPT 스타일 둥근 카드 (쉐도우 & 라운드) */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        /* 이 부분은 컨테이너에 적용됩니다 */
    }
    
    /* Streamlit 컨테이너(카드) 스타일 커스텀 */
    [data-testid="stVerticalBlock"] .st-emotion-cache-1r6slb0, 
    [data-testid="stVerticalBlock"] .st-emotion-cache-12w0qpk {
        background-color: #F8F9FA !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
        padding: 20px !important;
        border: 1px solid #E5E8EB !important;
    }

    /* 3. 입력창 디자인 */
    input, textarea, [data-baseweb="input"] {
        color: #191F28 !important;
        background-color: #F2F4F6 !important;
        border-radius: 12px !important;
        border: 1px solid #E5E8EB !important;
    }
    input::placeholder, textarea::placeholder {
        color: #8B95A1 !important;
        opacity: 1 !important;
    }

    /* 4. 버튼 스타일 (브랜드 컬러 블루) */
    .stButton>button {
        background-color: #3182F6 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 0.8rem 1rem !important;
        font-weight: 700 !important;
        border: none !important;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #1B64DA !important;
        transform: scale(1.02);
    }

    /* 5. 익스펜더(상세 리포트) 스타일 */
    .stExpander {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E5E8EB !important;
        box-shadow: none !important;
    }
    .stExpander summary {
        color: #333333 !important;
        font-weight: 600 !important;
    }
    .stExpander summary:hover {
        color: #3182F6 !important;
    }
    
    /* 카드 제목 스타일 */
    .card-header {
        color: #3182F6 !important;
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# API 설정
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 로컬 테스트용 키 (배포 시 삭제하거나 secrets에 넣으세요)
    API_KEY = "YOUR_API_KEY" 

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite" 

# 2. [상태 관리] 초기화
if 'step' not in st.session_state: st.session_state.step = 1
if 'spec_list' not in st.session_state: st.session_state.spec_list = [""]
if 'has_no_spec' not in st.session_state: st.session_state.has_no_spec = False
# 상태 변수 초기화 (에러 방지)
for key in ['school', 'major', 'target', 'job', 'exp', 'result', 'corp_data', 'keywords']:
    if key not in st.session_state: st.session_state[key] = ""

# 3. [메인 로직]
with streamlit_analytics.track():
    # --- 메인 이미지 (브릿지 사진) ---
    # Unsplash의 고화질 다리 이미지 사용 (원하는 이미지 URL로 교체 가능)
    st.image("https://images.unsplash.com/photo-1513506003013-02f837332d94?q=80&w=2000&auto=format&fit=crop", use_column_width=True)
    
    st.title("Value Bridge")
    st.caption("당신의 경험과 기업의 가치를 연결하는 AI 커리어 솔루션")

    # 관리자 접속 코드
    if st.query_params.get("analytics") == "on":
        if st.text_input("🔒 관리자 암호", type="password") != "value1234":
            st.warning("접근 권한이 없습니다.")
            st.stop()
    
    # 단계 진행 바
    st.progress(st.session_state.step / 4)

    # --- 1단계: 신원 정보 ---
    if st.session_state.step == 1:
        with st.container(border=True):
            st.markdown('<p class="card-header">🎓 소속 정보 입력</p>', unsafe_allow_html=True)
            st.session_state.school = st.text_input("대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
            st.session_state.major = st.text_input("전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        st.write("")
        if st.button("내 가치 연결 시작하기 →", type="primary"):
            if st.session_state.school and st.session_state.major:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("학교와 전공을 모두 입력해 주세요.")

    # --- 2단계: 목표 및 자격증 ---
    elif st.session_state.step == 2:
        with st.container(border=True):
            st.markdown('<p class="card-header">🏢 목표 설정</p>', unsafe_allow_html=True)
            st.session_state.target = st.text_input("목표 기업", value=st.session_state.target, placeholder="예: 한국은행, 삼성전자")
            st.session_state.job = st.text_input("목표 직무", value=st.session_state.job, placeholder="예: 데이터 분석, 영업관리")
        
        with st.container(border=True):
            st.markdown('<p class="card-header">📜 자격증 / 어학</p>', unsafe_allow_html=True)
            st.session_state.has_no_spec = st.checkbox("보유 자격증 없음", value=st.session_state.has_no_spec)
            
            if not st.session_state.has_no_spec:
                for i in range(len(st.session_state.spec_list)):
                    st.session_state.spec_list[i] = st.text_input(f"자격증 {i+1}", value=st.session_state.spec_list[i], key=f"spec_{i}", placeholder="예: AFPK, 토익 900")
                if st.button("➕ 자격증 추가"):
                    st.session_state.spec_list.append("")
                    st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전 단계"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("다음 단계 →", type="primary"):
                if st.session_state.target and st.session_state.job:
                    st.session_state.step = 3; st.rerun()
                else: st.error("기업과 직무를 입력해 주세요.")

    # --- 3단계: 경험 기술 ---
    elif st.session_state.step == 3:
        with st.container(border=True):
            st.markdown('<p class="card-header">✨ 핵심 경험 기술</p>', unsafe_allow_html=True)
            st.info("💡 TIP: 단순 나열보다 '어떤 문제를 어떻게 해결했는지' 적으면 분석이 더 정확해집니다.")
            st.session_state.exp = st.text_area("경험/활동 내용", value=st.session_state.exp, height=250, 
                                              placeholder="예: 캡스톤 디자인 프로젝트에서 팀장으로서...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전 단계"): st.session_state.step = 2; st.rerun()
        with col2:
            if st.button("🚀 가치 브릿지 분석 시작", type="primary"):
                if st.session_state.exp:
                    st.session_state.step = 4; st.rerun()
                else: st.error("경험 내용을 입력해 주세요.")

    # --- 4단계: 결과 리포트 (PPT 스타일 카드 UI) ---
    elif st.session_state.step == 4:
        st.subheader("🎯 직무 맞춤형 분석 결과")
        
        # 분석 로직
        if not st.session_state.result:
            with st.spinner(f"🔍 {st.session_state.target}의 최신 신년사, 인재상, 비전을 검색하고 분석 중입니다..."):
                try:
                    spec_summary = "보유 자격증 없음" if st.session_state.has_no_spec else ", ".join([s for s in st.session_state.spec_list if s.strip()])
                    
                    # --- [최종 통합 프롬프트 적용] ---
                    prompt = f"""
                    [역할 정의]
                    당신은 대기업 및 금융권 채용을 정밀 분석하는 **'HR 컨설턴트 겸 애널리스트'**입니다. 
                    당신의 임무는 지원자의 스펙을 요약하고, 구글 검색을 통해 **목표 기업의 최신 동향**과 **자격증의 실무적 가치**를 직접 조사하여 둘을 논리적으로 연결하는 **[VALUE BRIDGE 리포트]**를 작성하는 것입니다.

                    [필수 행동 지침: 실시간 데이터 조사]
                    1. **기업 데이터 조사:** 구글 검색을 통해 {st.session_state.target}의 **최신 신년사, 경영방침, 인재상, 비전, 핵심가치**를 직접 조사하세요.
                    2. **자격증 실무 가치 조사:** 지원자의 자격증({spec_summary})이 **{st.session_state.job} 직무**에서 구체적으로 어떤 실무 스킬로 쓰이는지 검색하세요.

                    [지원자 정보]
                    - 소속: {st.session_state.school} {st.session_state.major}
                    - 직무: {st.session_state.job}
                    - 스펙: {spec_summary}
                    - 경험: {st.session_state.exp}

                    [출력 형식 - 섹션 분리]
                    1. 먼저 'KEYWORD_DATA_START'와 'KEYWORD_DATA_END' 사이에 해당 기업에서 찾은 [신년사 키워드 / 비전 / 인재상 / 핵심가치]를 아주 짧은 단어 형태로만 나열하세요.
                    2. 이후 'REPORT_START'와 'REPORT_END' 사이에 아래 목차로 상세 리포트를 작성하세요.
                       - 1) 스펙 요약 (Fact Only)
                       - 2) 지원 회사/직무 요약 (Evidence Only)
                       - 3) 브릿지 단문 키워드
                       - 4) 브릿지 키워드 연결 리포트
                    3. 호칭은 반드시 '당신'으로 통일하세요.
                    """
                    
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
                        )
                    )
                    full_text = response.text
                    
                    # 파싱
                    if "KEYWORD_DATA_START" in full_text:
                        st.session_state.keywords = full_text.split("KEYWORD_DATA_START")[1].split("KEYWORD_DATA_END")[0].strip()
                        st.session_state.result = full_text.split("REPORT_START")[1].split("REPORT_END")[0].strip()
                    else:
                        st.session_state.result = full_text
                        
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {e}")
                    st.stop()

        # --- UI 구성 (PPT 스타일 카드 배치) ---
        
        # 1. 상단 정보 카드 (2열 배치)
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                st.markdown('<p class="card-header">👤 당신의 프로필</p>', unsafe_allow_html=True)
                st.write(f"**📍 소속:** {st.session_state.school} {st.session_state.major}")
                st.write(f"**📜 스펙:** {'자격증 없음' if st.session_state.has_no_spec else ', '.join(st.session_state.spec_list)}")
                st.write(f"**🌟 경험:** {st.session_state.exp[:40]}...")
        
        with col2:
            with st.container(border=True):
                st.markdown(f'<p class="card-header">🏢 {st.session_state.target} 데이터</p>', unsafe_allow_html=True)
                st.write(f"**🎯 지원 직무:** {st.session_state.job}")
                # AI가 검색한 실제 키워드 표시
                st.info(f"🔑 **분석 키워드:** {st.session_state.keywords if st.session_state.keywords else '기업 데이터 분석 완료'}")

        # 2. 핵심 요약 카드
        st.write("")
        with st.container(border=True):
            st.markdown('<p class="card-header">💡 가치 연결 핵심 무기</p>', unsafe_allow_html=True)
            st.write("AI가 분석한 당신의 경험과 기업의 교집합입니다.")
            # 리포트에서 키워드만 추출해서 보여주거나 전체 리포트 유도
            st.success("👇 아래 상세 리포트에서 **[브릿지 단문 키워드]**를 확인하세요!")

        # 3. 상세 리포트 (익스펜더)
        st.divider()
        with st.expander("📄 상세 컨설팅 리포트 전체 보기", expanded=True):
            st.markdown(st.session_state.result)
        
        # 4. 하단 버튼
        st.divider()
        st.link_button("🎁 수요조사 참여하고 기프티콘 받기", "https://docs.google.com/forms/d/e/1FAIpQLSd7cYP6QwTthzoEdlAyObugotZWGOYgqk7eJ323tvspGA0AGA/viewform")
        
        if st.button("🔄 처음부터 다시 분석하기"):
            for k in ['school','major','target','job','exp','result','keywords']: st.session_state[k] = ""
            st.session_state.step = 1
            st.rerun()

st.divider()
st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")