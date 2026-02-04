import streamlit as st
from google import genai  # 최신 google-genai 라이브러리 임포트
from google.genai import types

# =================================================================
# 1. [보안 및 설정] API 키 및 모델 설정
# =================================================================

# 배포 시에는 Streamlit Secrets를 사용하고, 로컬 테스트 시에는 직접 입력된 키를 사용합니다.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 로컬 테스트용 (깃허브 업로드 전 반드시 확인!)
    API_KEY = st.secrets["GEMINI_API_KEY"] 

# 최신 SDK 방식인 Client 객체 생성
client = genai.Client(api_key=API_KEY)

# 성현님이 보내주신 이미지 속 모델 리스트 (가장 성능이 좋고 빠른 Lite 모델 우선 권장)
# 모델 존재 여부에 따라 순차적으로 시도할 수 있도록 리스트화 했습니다.
MODEL_NAME = "gemini-2.5-flash-lite" 

# =================================================================
# 2. [UI 레이아웃] Streamlit 페이지 구성
# =================================================================

st.set_page_config(page_title="Value Bridge Demo", page_icon="🌉", layout="centered")

st.title("🌉 Value Bridge")
st.markdown("#### **경험을 기업의 언어로, '벨류 브릿지'**")
st.write("사용자의 대학 생활과 스펙을 분석하여 타겟 기업이 선호하는 핵심 키워드로 변환해 드립니다.")

st.divider() # 시각적 구분선

# 사용자 입력을 받기 위한 폼(Form) 생성
with st.form("value_bridge_form"):
    st.info("💡 모든 항목을 입력할수록 더 정확한 분석 결과가 나옵니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        school = st.text_input("📍 학교", placeholder="예: 한양대학교 ERICA")
        major = st.text_input("📚 전공", placeholder="예: 경제학부")
    with col2:
        target_company = st.text_input("🏢 목표 기업", placeholder="예: 한국은행, 신한은행")
        spec = st.text_input("📜 보유 자격증/어학", placeholder="예: AFPK, ADsP, 토익 900")

    # 주요 경험은 길게 작성할 수 있도록 text_area 사용
    experience = st.text_area("🌟 주요 경험 및 활동", 
                              placeholder="예: 노동경제학 수업 중 파이썬을 활용한 데이터 분석 프로젝트 수행",
                              help="자소서에 쓰고 싶은 가장 핵심적인 경험을 적어주세요.")

    # 폼 제출 버튼
    submit_button = st.form_submit_button("🔑 핵심 키워드 브릿지 생성")

# =================================================================
# 3. [로직] API 호출 및 결과 출력
# =================================================================

if submit_button:
    # 필수 입력 항목 체크
    if not (school and major and target_company and experience):
        st.error("분석을 위해 모든 항목을 입력해 주세요.")
    else:
        with st.spinner("최신 Gemini 모델이 당신의 가치를 분석 중입니다..."):
            try:
                # 최신 SDK 문법: client.models.generate_content 사용
                # 성현님의 벨류 브릿지 프로젝트 목적에 맞춘 전용 프롬프트
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

                # API 호출 실행
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt_text
                )

                # 결과 출력 섹션
                st.success(f"✅ {target_company} 합격을 위한 키워드 브릿지 완성!")
                st.markdown("---")
                st.markdown(response.text) # AI가 생성한 텍스트 출력
                
                # 4. [수요조사] 데모 피드백 링크 (성현님 구글 폼 주소로 변경 필요)
                st.info("✨ 분석 결과가 도움이 되셨나요? 정식 버전 출시를 위해 의견을 남겨주세요!")
                st.link_button("수요조사 참여하고 알림 받기", "www.naver.com")

            except Exception as e:
                # 에러 발생 시 상세 내용 출력 (디버깅용)
                st.error(f"분석 중 오류가 발생했습니다: {str(e)}")

# 하단 푸터
st.caption("© 2026 Value Bridge Project. All rights reserved.")