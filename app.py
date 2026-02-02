import streamlit as st
from google import genai
from data import TAX_KNOWLEDGE
import base64

# ==========================================
# 🔐 API 키 설정 (Secrets 사용)
# ==========================================
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    # 로컬 테스트를 위해 임시로 적어둘 경우 (배포 전 삭제 권장)
    # GOOGLE_API_KEY = "여기에_형님_API_키를_넣으세요" 
    st.error("🚨 API 키가 없습니다! 스트림릿 Secrets 설정을 확인해주세요.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)

# ==========================================
# 🎨 [디자인 마법] 배경화면 및 스타일 설정
# ==========================================
st.set_page_config(
    page_title="에릭 공인중개사 부동산 세무사 AI Pro", 
    page_icon="🏛️",
    layout="wide" # 화면을 넓게 씁니다
)

# 이미지를 불러와서 웹에서 쓸 수 있게 변환하는 함수
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 배경화면 적용 시도 (파일이 없어도 에러 안 나게 처리)
try:
    bin_str = get_base64_of_bin_file('background.jpg')
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    /* 채팅창 배경을 반투명하게 해서 글씨가 잘 보이게 */
    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ 배경 이미지(background.jpg)를 찾을 수 없습니다. 기본 배경으로 실행합니다.")


# ==========================================
# 🏠 메인 화면 구성
# ==========================================
st.title("🏛️ AI 부동산 세무사 (Pro Ver.)")
st.markdown("### 🤖 :blue[24시간] 당신 곁의 든든한 세무 파트너")
st.caption("복잡한 세법, 이제 AI에게 물어보세요. 왼쪽 사이드바에서 상황을 설정해주세요!")

# ---------------------------------------------------------
# 🎛️ 사이드바: 컨트롤 패널 (아이콘 적용!)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 내 정보 설정")
    st.write("정확한 상담을 위해 기초 정보를 입력해주세요.")
    st.markdown("---")
    
    # 1) 주택 수 (아이콘 추가)
    st.subheader("🏠 보유 주택 수")
    my_house_count = st.radio(
        "현재 보유 주택 수 (매수 예정 포함)",
        ["1주택 (첫 구매)", "2주택", "3주택", "4주택 이상"],
        index=1 # 기본값 2주택
    )
    
    st.markdown("---")
    
    # 2) 매수 지역 (아이콘 추가)
    st.subheader("📍 매수 예정 지역")
    target_area = st.selectbox(
        "규제 지역 여부를 선택하세요",
        ["✅ 비조정대상지역 (대부분)", "🚫 조정대상지역 (강남3구, 용산)"]
    )
    
    st.markdown("---")
    
    # 3) 매수 가격 (아이콘 추가)
    st.subheader("💰 매수 예정 가격")
    price = st.number_input(
        "단위: 억 원", 
        min_value=1.0, max_value=100.0, value=8.5, step=0.1, format="%.1f"
    )
    
    st.markdown("---")
    
    # ✨ [디자인 UP] 초기화 버튼 아이콘화
    # 스트림릿 기본 버튼에 이모지를 넣어서 아이콘처럼 보이게 합니다.
    if st.button("🔄 대화 내용 초기화", type="primary"): 
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 💬 채팅 인터페이스
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []
    # 첫 인사말 자동 추가
    with st.chat_message("assistant"):
        st.markdown("안녕하세요! 어떤 세금 문제가 고민이신가요? 왼쪽에서 상황을 설정해주시면 더 정확히 답변드릴게요. 😊")
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 어떤 세금 문제가 고민이신가요? 왼쪽에서 상황을 설정해주시면 더 정확히 답변드릴게요. 😊"})


# 이전 대화 표시
for message in st.session_state.messages[1:]: # 첫 인사말 중복 방지
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 질문 입력
if prompt := st.chat_input("예: 3주택자 취득세율 알려줘"):
    
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
    당신은 20년 경력의 친절하고 명쾌한 'AI 부동산 세무사'입니다.
    
    [지시사항]
    1. 아래 [사용자 현재 상황]을 핵심 근거로 삼으세요.
    2. 답변은 [세법 지식]에 기반하여 정확하게 하세요.
    3. 계산이 필요하면 '계산 과정'을 보여주고 최종 예상 세액을 제시하세요.
    4. 어려운 용어는 쉽게 풀어서 설명하고, 중요한 부분은 볼드체(**)로 강조하세요.
    
    {user_context}
    
    [세법 지식]
    {TAX_KNOWLEDGE}
    
    [고객 질문]
    {prompt}
    """

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("세법책 뒤적이는 중... 📚"): # 답변 기다릴 때 로딩 표시
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash", # 또는 형님이 찾으신 모델명
                    contents=full_prompt
                )
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
