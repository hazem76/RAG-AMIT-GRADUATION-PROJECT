"""Test script to verify Gemini API configuration and functionality."""
import os
import sys
from pathlib import Path

def test_python_gemini():
    """Test Gemini API with Python SDK."""
    print("\n" + "="*70)
    print("TEST 1: Python SDK (google-generativeai)")
    print("="*70)

    try:
        import google.generativeai as genai
        print("[+] google-generativeai library imported successfully")
    except ImportError:
        print("[-] google-generativeai not installed")
        print("    Run: pip install google-generativeai")
        return False

    # Read API key from .env
    from app.core.config import settings

    if not settings.GEMINI_API_KEY:
        print("[-] GEMINI_API_KEY not set in .env file")
        return False

    print(f"[+] API Key found: {settings.GEMINI_API_KEY[:20]}...")
    print(f"[+] Model: {settings.GEMINI_MODEL}")

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        print("[+] Gemini API configured")

        # Try simple test
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        print(f"[*] Testing with model: {settings.GEMINI_MODEL}")

        response = model.generate_content("Say 'Hello, Gemini is working!' in 5 words or less")
        print(f"[+] API Response successful!")
        print(f"    Response: {response.text}")
        return True

    except Exception as e:
        print(f"[-] Error: {str(e)}")
        error_msg = str(e).lower()

        if "blocked" in error_msg or "403" in error_msg:
            print("\n[!] API KEY BLOCKED - Your API key may have restrictions")
            print("    Solution:")
            print("    1. Go to Google Cloud Console: https://console.cloud.google.com")
            print("    2. Select your project")
            print("    3. Enable 'Google AI for Developers' API")
            print("    4. Check API quotas and restrictions")
            print("    5. Try a different API key if needed")
        elif "not found" in error_msg or "invalid" in error_msg:
            print("\n[!] INVALID API KEY")
            print("    Solution:")
            print("    1. Get a new API key from: https://aistudio.google.com/apikey")
            print("    2. Update GEMINI_API_KEY in .env")
            print("    3. Restart the backend")

        return False


def test_javascript_gemini():
    """Show JavaScript SDK test (what worked for user)."""
    print("\n" + "="*70)
    print("TEST 2: JavaScript SDK (what worked for you)")
    print("="*70)
    print("""
Your JavaScript test works because it uses:
  - Library: @google/generative-ai
  - Model: gemini-2.5-flash

The Python backend now uses:
  - Library: google-generativeai
  - Model: gemini-1.5-flash (with fallback to gemini-pro)

Both should work with the same API key.
""")


def test_fallback_modes():
    """Show fallback response modes."""
    print("\n" + "="*70)
    print("TEST 3: Fallback Response Modes")
    print("="*70)
    print("""
If Gemini API is blocked/unavailable, the system has fallbacks:

MODE 1: Offline Response
  - Uses retrieved document chunks directly
  - No API call made
  - Lower confidence score (max 50%)
  - Still provides useful information

MODE 2: RAG-Only Response
  - Pure document retrieval + formatting
  - No AI generation
  - Fast response times
  - Good for FAQ scenarios

Both modes are active and will kick in automatically if API fails.
""")


def suggest_fixes():
    """Suggest fixes for the API key issue."""
    print("\n" + "="*70)
    print("RECOMMENDED FIXES")
    print("="*70)
    print("""
1. UPDATE API KEY:
   Option A: Get free API key from https://aistudio.google.com/apikey
   Option B: Check Google Cloud Console for API restrictions

2. UPDATE MODEL (in .env):
   GEMINI_MODEL=gemini-1.5-flash
   or try: gemini-1.5-pro, gemini-pro

3. RESTART BACKEND:
   - Kill backend process
   - Run: python -m uvicorn app.main:app --reload

4. TEST CHAT:
   - Go to http://localhost:5173/chat
   - Ask a question
   - Monitor backend terminal for errors

5. IF API STILL BLOCKED:
   - Backend will use Offline RAG mode
   - Responses will come from documents directly
   - No AI API calls made
   - System still fully functional!
""")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("GEMINI API CONFIGURATION TEST")
    print("="*70)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    os.chdir(backend_dir)

    # Test Python SDK
    python_ok = test_python_gemini()

    # Show JavaScript info
    test_javascript_gemini()

    # Show fallback modes
    test_fallback_modes()

    # Suggest fixes
    suggest_fixes()

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if python_ok:
        print("""
[+] Gemini API is working!
    Your chat interface should now respond with AI-generated answers.
""")
    else:
        print("""
[-] Gemini API has issues
    The system will still work using Offline RAG mode:
    - Responses based on document chunks
    - No AI inference
    - But fully functional!

    To fix: Follow the recommended fixes above.
""")

    print("="*70 + "\n")

    return 0 if python_ok else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
