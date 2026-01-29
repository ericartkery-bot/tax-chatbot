import streamlit as st
from google import genai
from data import TAX_KNOWLEDGE

# ==========================================
# 👇 형님의 API 키를 여기에 다시 넣어주세요!

# 이제 키를 코드에 직접 안 적습니다!
# st.secrets 라는 금고에서 가져옵니다.
# [수정 전] (이렇게 되어 있어서 걸린 겁니다 ㅠㅠ)
# else:
#     GOOGLE_API_KEY = "AIzaSy..." 

# 👇 [수정 후] (이렇게 바꾸세요! 깔끔하게!)
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    # 에러 메시지를 띄워서 키가 없음을 알려줌
    st.error("API 키가 없습니다. 스트림릿 Secrets 설정을 확인해주세요!")
# ==========================================

# 1. 클라이언트 연결
client = genai.Client(api_key=GOOGLE_API_KEY)

# 2. 화면 구성 (사이드바 추가!)
st.set_page_config(page_title="Eric 부동산 Tax 세무사 AI", page_icon="🏠")

st.title("🏠 AI Eric HeeSang 부동산 세무사 (Pro Ver.)")
st.caption("왼쪽 사이드바에서 내 상황을 먼저 설정해주세요!")

# ---------------------------------------------------------
# 🎨 [NEW] 사이드바: 사용자 상황 설정 패널
# ---------------------------------------------------------
with st.sidebar:
    st.header("📝 내 정보 설정 (기초 상담)")
    st.write("아래 정보를 선택하면 더 정확해집니다.")
    
    # 1) 주택 수 선택 (라디오 버튼)
    my_house_count = st.radio(
        "현재 보유 주택 수 (매수 예정 포함)",
        ["1주택 (무주택자가 첫 구매)", "2주택", "3주택", "4주택 이상"]
    )
    
    st.markdown("---") # 구분선
    
    # 2) 매수하려는 지역 (선택 박스)
    target_area = st.selectbox(
        "매수하려는 집의 위치",
        ["비조정대상지역 (대부분의 지역)", "조정대상지역 (강남3구, 용산)"]
    )
    
    st.markdown("---")
    
    # 3) 매수 가격 (슬라이더)
    price = st.number_input(
        "매수 가격 (단위: 억 원)", 
        min_value=1.0, 
        max_value=50.0, 
        value=6.0,
        step=0.1
    )
    
    st.info(f"💡 설정 확인:\n{my_house_count}\n{target_area}\n{price}억 원 매수 예정")

# ---------------------------------------------------------
# 💬 채팅 인터페이스
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 질문 입력 처리
if prompt := st.chat_input("궁금한 점을 물어보세요!"):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ✨ [핵심 기술] 사이드바 정보를 프롬프트에 몰래 섞어넣기
    # 사용자가 말하지 않아도, AI는 이미 사이드바 정보를 알고 있게 만듭니다.
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
            # 아까 찾으신 정답 모델명 적용!
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=full_prompt
            )
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")