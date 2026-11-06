import requests
import base64

url = "http://127.0.0.1:8000/api/voice/conversation"

with open("telugu_test.wav", "rb") as audio_file:
    files = {
        "audio": (
            "rythuvoicetest_telugu.wav",
            audio_file,
            "audio/wav"
        )
    }

    data = {
        "language": "te-IN"
    }

    response = requests.post(
        url,
        files=files,
        data=data,
        timeout=180
    )

if response.status_code == 200:
    result = response.json()

    print("\nFARMER QUESTION:")
    print(result["farmer_question"])

    print("\nAI RESPONSE:")
    print(result["ai_response"])

    audio_bytes = base64.b64decode(result["audio_base64"])

    with open("conversation_response.wav", "wb") as output:
        output.write(audio_bytes)

    print("\nAudio saved as conversation_response.wav")

else:
    print("Error:", response.status_code)
    print(response.text)