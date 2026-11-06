import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not api_key:
    print("ERROR: GROQ_API_KEY not found in .env")
    raise SystemExit(1)

print("Groq API key found.")
print("Testing model:", model)

try:
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Reply in Telugu: Explain why cotton leaves turn yellow."
            }
        ],
        temperature=0.3,
        max_tokens=300
    )

    print("\nGROQ CONNECTION SUCCESSFUL!")
    print("\nAI RESPONSE:")
    print(response.choices[0].message.content)

except Exception as error:
    print("\nGROQ CONNECTION FAILED")
    print("Error type:", type(error).__name__)
    print("Error details:", str(error))