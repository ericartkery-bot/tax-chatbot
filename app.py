import streamlit as st
from google import genai
from data import TAX_KNOWLEDGE
import base64
import os

# ==========================================
# 🔐 [배포용] API 키 보안 설정 (Secrets 사용)
# ==========================================
# 깃허브에 올릴 때는 절대 실제 키를 적지 않습니다!
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("🚨 API 키가 없습니다! 스트림릿 Secrets 설정을 확인해주세요.")
    st.stop()

# 클라이언트 연결
try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"API 키 연결 실패: {e}")
    st.stop()

# ==========================================
# 🎨 디자인 (다크 모드 스타일)
# ==========================================
st.set_page_config(
    page_title="에릭 공인중개사 AI", 
    page_icon="🏛️",
    layout="wide"
)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 배포 환경에서도 background.jpg 파일이 같이 올라가 있어야 합니다!
background_image_path = 'background.jpg'

if os.path.exists(background_image_path):
    try:
        bin_str = get_base64_of_bin_file(background_image_path)
        page_bg_img = f"""
        <style>
        /* 1. 전체 배경 이미지 설정 */
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* 2. [핵심] 사이드바 글씨를 '하얀색'으로 강제 변경 */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label {{
            color: #FFFFFF !important; /* 완전 하얀색 */
        }}

        /* 3. 사이드바 배경을 '검은색 반투명'으로 설정 */
        section[data-testid="stSidebar"] > div {{
            background-color: rgba(0, 0, 0, 0.7) !important;
        }}

        /* 4. 메인 화면(채팅창 쪽) 글씨 설정 */
        .main h1, .main h2, .main h3 {{
             color: #FFFFFF !important;
             text-shadow: 2px 2px 4px #000000;
        }}
        
        /* 채팅창 배경 (어둡게 + 하얀 글씨) */
        .stChatMessage {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: #FFFFFF !important;
            border: 1px solid #444444;
            border-radius: 15px;
        }}
        
        .stChatMessage p {{
            color: #FFFFFF !important;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except Exception as e:
         st.warning(f"배경 이미지 적용 중 오류 발생: {e}")
else:
    # 혹시 이미지가 안 올라갔을 때를 대비한 메시지
    st.warning("⚠️ 배경 이미지를 찾을 수 없습니다. (GitHub에 background.jpg를 올렸는지 확인하세요!)")


# ==========================================
# 🏠 메인 화면
# ==========================================
st.title("🤖 AI 부동산 세무 상담소")
st.caption("✅ 왼쪽 사이드바에서 조건을 설정하고 질문해주세요.")

# ---------------------------------------------------------
# 🎛️ 사이드바
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 상담 조건 설정")
    st.write("---")
    
    st.subheader("🏠 보유 주택 수")
    my_house_count = st.radio(
        "현재 보유 주택 수",
        ["1주택 (첫 구매)", "2주택", "3주택", "4주택 이상"],
        index=1
    )
    st.write("---")
    
    st.subheader("📍 매수 예정 지역")
    target_area = st.selectbox(
        "규제 지역 여부",
        ["✅ 비조정대상지역 (대부분)", "🚫 조정대상지역 (강남3구, 용산)"]
    )
    st.write("---")
    
    st.subheader("💰 매수 예정 가격")
    price = st.number_input(
        "단위: 억 원", 
        min_value=0.1, max_value=200.0, value=8.5, step=0.1, format="%.1f"
    )
    st.write("---")
    
    if st.button("🔄 대화 내용 초기화", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 💬 채팅 인터페이스
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.chat_message("assistant"):
        st.markdown("안녕하세요! **에릭 공인중개사** AI 파트너입니다. 무엇을 도와드릴까요? 😊")
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! **에릭 공인중개사** AI 파트너입니다. 무엇을 도와드릴까요? 😊"})

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("궁금한 내용을 입력하세요"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    user_context = f"""
    [사용자 현재 상황 설정]
    - 보유 주택 수: {my_house_count}
    - 매수 예정 지역: {target_area}
    - 매수 예정 가격: {price}억 원
    """

    full_prompt = f"""
    당신은 '에릭 공인중개사'의 유능한 AI 세무 파트너입니다.
    
    [지시사항]
    1. 반드시 아래 [사용자 현재 상황 설정]을 반영하여 답변하세요.
    2. 모든 답변의 근거는 [세법 지식] 데이터에서만 찾으세요.
    3. 계산이 필요한 경우, 계산 과정을 명확히 보여주고 최종 예상 세액을 제시하세요.
    4. 전문적이지만 고객이 이해하기 쉬운 친절한 어투를 사용하세요.
    
    {user_context}
    
    [세법 지식 데이터]
    {TAX_KNOWLEDGE}
    
    [고객 질문]
    {prompt}
    """

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("분석 중... 📚"):
            try:
                # 형님이 성공했던 모델 버전 유지
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=full_prompt
                )
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
