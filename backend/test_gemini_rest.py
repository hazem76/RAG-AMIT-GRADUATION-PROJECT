"""Test Gemini API with REST endpoint - matches JavaScript SDK behavior"""
import requests
import json

API_KEY = "AIzaSyBT25clT3GCbpiHkvJcgb1qHkYTIbV5CDk"
MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

def test_gemini():
    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Say who is the public arabic football player"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 1024
            }
        }

        url = f"{API_URL}?key={API_KEY}"

        print(f"[INFO] Testing Gemini API with REST endpoint")
        print(f"[INFO] Model: {MODEL}")
        print(f"[INFO] URL: {API_URL}")

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        print(f"[INFO] Status code: {response.status_code}")

        if response.status_code == 200:
            response_json = response.json()
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                candidate = response_json["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    if len(candidate["content"]["parts"]) > 0:
                        text = candidate["content"]["parts"][0].get("text", "")
                        if text:
                            print("\n[+] SUCCESS!")
                            print(f"Response:\n{text}")
                            return True

        print(f"\n[-] ERROR:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return False

    except requests.Timeout:
        print("[-] ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"[-] ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini()
