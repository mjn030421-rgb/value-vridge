import streamlit as st
from google import genai
import streamlit_analytics2 as streamlit_analytics
from google.genai import types

# =================================================================
# 1. [설정] API 키 및 모델 설정
# =================================================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 로컬 테스트 시에는 실제 API 키를 여기에 넣으세요 (GitHub 업로드 전 삭제 필수)
    API_KEY = "YOUR_ACTUAL_API_KEY_HERE" 

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite" 

# =================================================================
# 2. [UI & 로직] 모든 과정을 track() 하나로 통합
# =================================================================
st.set_page_config(page_title="Value Bridge Demo", page_icon="Bridge", layout="centered")

st.markdown("""
    <style>
    /* 1. 전체 배경색 (밝은 회색) */
    .stApp {
        background-color: #F8F9FA !important;
    }
    
    /* 2. 모든 기본 글자색을 짙은 회색(#31333F)으로 고정 */
    .stApp, .stMarkdown, p, li, span, label {
        color: #31333F !important;
    }

    /* 3. 제목(Title)과 소제목(Header) 색상 강조 */
    h1, h2, h3, h4 {
        color: #003D7C !important; /* 한양대 블루 */
        font-weight: 800 !important;
    }

    /* 4. 입력창 내부 글자색 및 배경 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        color: #31333F !important;
        background-color: #FFFFFF !important;
        border: 1px solid #DDE1E6 !important;
    }

    /* 5. 버튼 디자인 (배경은 진하게, 글자는 하얗게) */
    .stButton>button {
        background-color: #003D7C !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
    }

    /* 6. 결과창(Success/Info) 내부 글자색 수정 */
    .stAlert p {
        color: #31333F !important;
    }
    </style>
    """, unsafe_allow_html=True)

with streamlit_analytics.track():
    st.title("Value Bridge")
    st.markdown("#### **경험을 기업의 언어로, '벨류 브릿지'**")
    st.write("사용자의 대학 생활과 스펙을 분석하여 핵심 키워드로 변환해 드립니다.")

    st.divider()

    # 1. 폼(with st.form)을 제거하고 일반 레이아웃으로 변경
    st.info("💡 모든 항목을 입력할수록 더 정확한 분석 결과가 나옵니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        school = st.text_input("📍 학교", placeholder="예: 한양대학교 ERICA")
        major = st.text_input("📚 전공", placeholder="예: 경제학부")
    with col2:
        target_company = st.text_input("🏢 목표 기업", placeholder="예: 한국은행, 신한은행")
        spec = st.text_input("📜 보유 자격증/어학", placeholder="예: AFPK, ADsP, 토익 900")

    experience = st.text_area("🌟 주요 경험 및 활동", 
                              placeholder="예: 노동경제학 수업 중 파이썬을 활용한 데이터 분석 프로젝트 수행")

    # 2. st.form_submit_button 대신 일반 st.button 사용 (key 필수!)
    # 이 방식이 streamlit-analytics에서 가장 카운트가 잘 올라갑니다.
    submit_button = st.button("🔑 핵심 키워드 브릿지 생성", key="real_generate_button")
   
   
   # 버튼 클릭 시 실행될 단 하나의 로직
    if submit_button:
        if not (school and major and target_company and experience):
            st.error("분석을 위해 모든 항목을 입력해 주세요.")
        else:
            with st.spinner("최신 Gemini 모델이 당신의 가치를 분석 중입니다..."):
                try:
                    prompt_text = f"""
                    당신은 대학생의 역량을 기업의 핵심가치와 연결하는 전문가입니다.
                    아래 사용자의 정보를 바탕으로, {target_company} 지원 시 가장 경쟁력 있는 [핵심 키워드] 5개를 도출하세요.

                    [사용자 정보]
                    - 학교/전공: {school} {major}
                    - 보유 스펙: {spec}
                    - 주요 활동: {experience}

                    [요구사항]
                    1. 결과는 반드시 [키워드1, 키워드2, 키워드3, 키워드4, 키워드5] 형태의 리스트로 시작하세요.
                    2. 각 키워드별로 이 키워드가 왜 도출되었는지 자소서 작성 팁을 한 줄씩 덧붙여주세요.
                    3. {target_company}의 최신 채용 트렌드와 직무 역량을 반영하세요.
                    """

                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt_text
                    )

                    # 결과 출력
                    st.success(f"✅ {target_company} 합격을 위한 키워드 브릿지 완성!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    st.info("✨ 분석 결과가 도움이 되셨나요? 정식 버전 출시를 위해 의견을 남겨주세요!")
                    st.link_button("수요조사 참여하고 알림 받기", "https://forms.gle/your_actual_link")

                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {str(e)}")

# 하단 푸터 (track 밖으로 빼서 깔끔하게 마무리)
st.divider()
st.caption("© 2026 Value Bridge Project. All rights reserved.")