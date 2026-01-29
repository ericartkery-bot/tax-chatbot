from google import genai

# 👇 형님의 API 키를 여기에 붙여넣으세요!
GOOGLE_API_KEY = "AIzaSyBODluuyHqzYWu-6701R5t7zUf3jZwosg8"

client = genai.Client(api_key=GOOGLE_API_KEY)

print("============== [내 API 키로 사용 가능한 모델 목록] ==============")
try:
    # 사용 가능한 모델들을 다 불러와서 보여달라는 명령어입니다.
    for m in client.models.list():
        if "generateContent" in m.supported_actions:
            print(f"모델 이름: {m.name}")
            
    print("===============================================================")
    print("위 목록에 있는 이름 중 하나를 골라 app.py에 적으면 100% 됩니다.")

except Exception as e:
    print(f"에러가 발생했습니다: {e}")