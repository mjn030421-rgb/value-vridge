import streamlit as st
from google import genai
from google.genai import types
import streamlit_analytics2 

# 1. [설정] 페이지 설정 및 API 연결
st.set_page_config(page_title="Value Bridge", page_icon="🌉", layout="centered")

# 디자인 테마 (검정 글씨 및 가독성 최우선 강화)
st.markdown("""
    <style>
    /* 전체 배경 흰색 고정 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 1. 모든 일반 텍스트 및 레이블 검정색 고정 */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown {
        color: #191F28 !important;
    }
    
    /* 2. 입력창 디자인: 배경은 연회색, 글자는 진한 검정 */
    input, textarea, [data-baseweb="input"] {
        color: #191F28 !important;
        background-color: #F2F4F6 !important;
        border-radius: 12px !important;
    }

    /* 3. 가장 중요한 '예시 문구(Placeholder)' 색상 강제 지정 */
    input::placeholder, textarea::placeholder {
        color: #757575 !important;
        opacity: 1 !important; /* 투명도 제거 */
    }

    /* 4. 서비스 소개 박스 글씨색 보정 */
    .intro-box {
        background-color: #E8F3FF !important;
        padding: 20px;
        border-radius: 16px;
        border-left: 6px solid #3182F6;
        margin-bottom: 25px;
    }
    .intro-box strong { color: #1B64DA !important; }
    .intro-box p { color: #2D3436 !important; font-weight: 500; }

    /* 5. 버튼 스타일 (파란 배경에 흰 글씨) */
    .stButton>button {
        background-color: #3182F6 !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        width: 100%;
        border: none !important;
    }
    
    /* 성공/정보 메시지 박스 내부 글자색 */
    .stAlert p { color: #191F28 !important; }
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
# 기존 track 부분을 아래와 같이 수정 (password 인자를 뺍니다)
with streamlit_analytics.track():
    st.title("Value Bridge")
    
    # 관리자 모드(?analytics=on)일 때만 비밀번호를 한 번 더 물어봄
    if st.query_params.get("analytics") == "on":
        admin_pass = st.text_input("데이터 보호를 위해 비밀번호를 입력하세요", type="value1234")
        if admin_pass != "value1234":
            st.warning("비밀번호가 일치하지 않아 통계 데이터를 숨깁니다.")
            st.stop() # 비밀번호가 틀리면 여기서 실행 중단
    
    # 진행 바
    st.progress(st.session_state.step / 4, text=f"{st.session_state.step} / 4 단계 진행 중")

    # --- 1단계: 서비스 정의 및 신원 정보 ---
    if st.session_state.step == 1:
        st.markdown(f"""
        <div class="intro-box">
            <strong>Value Bridge란?</strong>
            <p>당신의 대학 시절 경험이 목표 기업의 가치와 어떻게 연결되는지 분석해주는 서비스입니다. 
            기업의 <b>실시간 인재상, 최신 신년사, 비전</b> 데이터를 기반으로 당신의 가치를 재해석합니다.</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("먼저, 당신의 소속을 알려주세요 🎓")
        st.session_state.school = st.text_input("📍 대학교", value=st.session_state.school, placeholder="예: 한양대학교 ERICA")
        st.session_state.major = st.text_input("📚 전공", value=st.session_state.major, placeholder="예: 경제학부")
        
        st.write("")
        if st.button("내 가치 연결하기 →", key="step1_next"):
            if st.session_state.school and st.session_state.major:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("분석을 위해 정보를 입력해 주세요!")

    # --- 2단계: 목표 및 동적 자격증 입력 ---
    elif st.session_state.step == 2:
        st.subheader("어떤 기업에서 어떤 일을 하고 싶으신가요? 🏢")
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
                    key=f"spec_input_{i}",
                    placeholder="예: AFPK, ADsP, 토익 900"
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
        st.subheader("당신의 가장 빛나는 경험을 들려주세요 ✨")
        st.session_state.exp = st.text_area("🌟 주요 경험 및 활동", value=st.session_state.exp, 
                                          placeholder="예: 프로젝트, 인턴십, 아르바이트 등 드러내고 싶은 경험", height=200)
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 이전"): st.session_state.step = 2; st.rerun()
        with col2:
            if st.button("가치 브릿지 생성 🚀"):
                if st.session_state.exp:
                    st.session_state.step = 4; st.rerun()
                else: st.error("분석할 경험을 입력해 주세요.")

    # --- 4단계: 실시간 검색 기반 결과 리포트 ---
    elif st.session_state.step == 4:
        st.subheader("🎯 당신을 위한 직무 맞춤형 리포트")
        
        with st.spinner(f"{st.session_state.target}의 최신 동향을 분석 중입니다..."):
            try:
                if not st.session_state.result:
                    spec_summary = "보유 자격증 없음" if st.session_state.has_no_spec else ", ".join([s for s in st.session_state.spec_list if s.strip()])
                    
                    prompt = f"""
                    당신은 전문 채용 컨설턴트입니다. 구글 검색을 활용해 {st.session_state.target}의 '2026년 신년사', '인재상', '비전'을 확인하고 분석하세요.

                    [지원자 정보]
                    - 소속: {st.session_state.school} {st.session_state.major}
                    - 직무: {st.session_state.job}
                    - 스펙: {spec_summary}
                    - 경험: {st.session_state.exp}

                    [요구사항]
                    1. 기업의 최신 경영 방침(신년사 등)과 지원자의 경험을 연결하여 5가지 핵심 역량을 도출하세요.
                    2. 자격증이 있다면 지식과의 연결고리를, 없다면 실무 역량 강조법을 제시하세요.
                    3. {st.session_state.major} 전공자로서 이 직무에서 가질 수 있는 차별화된 시각을 설명하세요.
                    4. 호칭은 반드시 '당신'으로 통일하여 리포트를 작성하세요.
                    """
                    
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
                        )
                    )
                    st.session_state.result = response.text
                
                st.markdown(f"### **{st.session_state.target} | {st.session_state.job} 분석 결과**")
                st.markdown(st.session_state.result)
                
                st.divider()
                st.link_button("수요조사 참여하고 분석 결과 저장하기", "https://forms.gle/your_link")
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

        if st.button("처음부터 다시 하기"):
            for k in ['school','major','target','job','exp','result']: st.session_state[k] = ""
            st.session_state.spec_list = [""]; st.session_state.has_no_spec = False; st.session_state.step = 1; st.rerun()

st.divider()
st.caption("© 2026 Value Bridge Project. Hanyang Univ ERICA Economics.")