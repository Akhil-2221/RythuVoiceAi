import os
from dotenv import load_dotenv
from gnani.tts import GnaniTTSClient

load_dotenv()

api_key = os.getenv("PRISMA_API_KEY")

client = GnaniTTSClient(api_key=api_key)

text = "నమస్కారం రైతు అన్నా. మీ పంట ఎలా ఉంది?"

audio = client.synthesize(
    text,
    voice="Yukti",
    model="timbre-v2.5",
    language="te-IN"
)

with open("telugu_test.wav", "wb") as file:
    file.write(audio)

print("Telugu audio generated successfully!")