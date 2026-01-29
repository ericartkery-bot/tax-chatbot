import streamlit as st
from google import genai
from data import TAX_KNOWLEDGE

# ==========================================
# 🔐 API 키 보안 설정 (Secrets에서 가져오기)
# ==========================================
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("🚨 API 키가 없습니다! 스트림릿 Secrets 설정을 확인해주세요.")
    st.stop() # 키 없으면 여기서 멈춤

# 클라이언트 연결
client = genai.Client(api_key=GOOGLE_API_KEY)

# 화면 구성
st.set_page_config(page_title="Eric Hee Sang 공인중개사 사무소와 세무사 AI", page_icon="🏠")

st.title("🏠 AI 부동산 세무사 (Pro Ver.)")
st.caption("왼쪽 사이드바에서 내 상황을 설정하고 질문하세요!")

# ---------------------------------------------------------
# 🎨 사이드바: 설정 패널
# ---------------------------------------------------------
with st.sidebar:
    st.header("📝 내 정보 설정")
    
    # 1) 주택 수
    my_house_count = st.radio(
        "현재 보유 주택 수 (매수 예정 포함)",
        ["1주택 (무주택자가 첫 구매)", "2주택", "3주택", "4주택 이상"]
    )
    
    st.markdown("---")
    
    # 2) 매수 지역
    target_area = st.selectbox(
        "매수하려는 집의 위치",
        ["비조정대상지역 (대부분의 지역)", "조정대상지역 (강남3구, 용산)"]
    )
    
    st.markdown("---")
    
    # 3) 매수 가격
    price = st.number_input(
        "매수 가격 (단위: 억 원)", 
        min_value=1.0, 
        max_value=50.0, 
        value=6.0, 
        step=0.1
    )
    
    st.markdown("---")
    
    # ✨ [NEW] 대화 초기화 버튼
    if st.button("🗑️ 대화내용 지우기 (초기화)"):
        st.session_state.messages = [] # 대화 기록 삭제
        st.rerun() # 화면 새로고침

# ---------------------------------------------------------
# 💬 채팅 인터페이스
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 질문 입력
if prompt := st.chat_input("궁금한 점을 물어보세요!"):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 사이드바 정보 주입
    user_context = f"""
    [사용자 현재 상황]
    - 보유 주택 수: {my_house_count}
    - 매수 예정 지역: {target_area}
    - 매수 예정 가격: {price}억 원
    """

    full_prompt = f"""
    당신은 20년 경력의 베테랑 부동산 세무사입니다. 
    
    1. 먼저 아래 [사용자 현재 상황]을 반드시 참고하여 맞춤형으로 답변하세요.
    2. 답변의 근거는 [세법 지식]에서만 찾으세요.
    3. 계산이 필요하면 구체적인 숫자로 계산해서 보여주세요.
    
    {user_context}
    
    [세법 지식]
    {TAX_KNOWLEDGE}
    
    [고객 질문]
    {prompt}
    """

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash-001", 
                contents=full_prompt
            )
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")