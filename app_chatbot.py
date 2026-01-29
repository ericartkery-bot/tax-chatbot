# app.py
import streamlit as st

# 화면에 제목을 표시하는 코드
st.title("🏠 우리 집 세금 계산기 챗봇")

# 화면에 안내 문구를 표시하는 코드
st.write("반갑습니다! 부동산 세금에 대해 무엇이든 물어보세요.")

# 사용자가 글자를 입력할 수 있는 입력창을 만드는 코드
user_question = st.text_input("질문을 입력해주세요:")

# 만약 사용자가 질문을 입력했다면?
if user_question:
    # 화면에 답변을 보여주는 코드 (지금은 가짜 답변)
    st.write(f"형님이 입력하신 질문은 '{user_question}' 이군요!")
    st.success("아직 AI와 연결되지 않았지만, 곧 제가 멋진 답변을 드릴게요!")

# 사이드바(옆 메뉴) 만드는 코드
with st.sidebar:
    st.header("📌 사용 안내")
    st.write("현재는 프로토타입 버전입니다.")