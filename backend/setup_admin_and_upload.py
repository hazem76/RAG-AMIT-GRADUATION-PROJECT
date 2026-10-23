"""Setup admin user and automatically upload knowledge base documents."""
import os
import sys
import json
import time
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import User, Base
from app.core.security import hash_password
import requests

# Admin credentials
ADMIN_EMAIL = "admin@supportmind.ai"
ADMIN_PASSWORD = "Admin123!@#"
ADMIN_NAME = "Admin User"

# Backend API settings
API_BASE_URL = "http://localhost:8000/api"
BACKEND_HOST = "localhost"
BACKEND_PORT = 8000

def wait_for_backend(max_retries=30):
    """Wait for backend to be ready."""
    print("[*] Waiting for backend to start...")
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/auth/me", timeout=2)
            # Will return 401 since no token, but connection works
            if response.status_code in [401, 403]:
                print("[+] Backend is ready!")
                return True
        except:
            if attempt < max_retries - 1:
                print(f"    Attempt {attempt + 1}/{max_retries}: Waiting...")
                time.sleep(1)
    print("[-] Backend did not start in time")
    return False

def create_admin_user():
    """Create admin user in database."""
    print("\n[*] Setting up admin user...")

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if existing_admin:
            print(f"[+] Admin user already exists: {ADMIN_EMAIL}")
            db.close()
            return ADMIN_EMAIL, ADMIN_PASSWORD

        # Create admin user
        admin_user = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print(f"[+] Admin user created successfully!")
        print(f"    Email: {ADMIN_EMAIL}")
        print(f"    Password: {ADMIN_PASSWORD}")
        db.close()
        return ADMIN_EMAIL, ADMIN_PASSWORD

    except Exception as e:
        print(f"[-] Error creating admin user: {e}")
        db.close()
        return None, None

def login_and_get_token(email, password):
    """Login and get JWT token."""
    print(f"\n[*] Logging in as {email}...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("[+] Login successful, got access token")
            return token
        else:
            print(f"[-] Login failed: {response.status_code}")
            print(f"    Response: {response.text}")
            return None
    except Exception as e:
        print(f"[-] Error logging in: {e}")
        return None

def upload_document(token, file_path):
    """Upload document to knowledge base via API."""
    filename = os.path.basename(file_path)
    print(f"\n[*] Uploading document: {filename}")

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            headers = {'Authorization': f'Bearer {token}'}

            response = requests.post(
                f"{API_BASE_URL}/knowledge-base/upload",
                files=files,
                headers=headers,
                timeout=30
            )

        if response.status_code == 200:
            doc_data = response.json()
            print(f"[+] Document uploaded successfully!")
            print(f"    ID: {doc_data.get('id')}")
            print(f"    Filename: {doc_data.get('filename')}")
            print(f"    Chunks: {doc_data.get('chunk_count')}")
            return True
        else:
            print(f"[-] Upload failed: {response.status_code}")
            print(f"    Response: {response.text}")
            return False
    except Exception as e:
        print(f"[-] Error uploading document: {e}")
        return False

def list_documents(token):
    """List uploaded documents."""
    print("\n[*] Listing uploaded documents...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f"{API_BASE_URL}/knowledge-base",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            documents = response.json()
            print(f"[+] Found {len(documents)} document(s):")
            for doc in documents:
                print(f"    - {doc['filename']} ({doc['chunk_count']} chunks)")
            return documents
        else:
            print(f"[-] Failed to list documents: {response.status_code}")
            return []
    except Exception as e:
        print(f"[-] Error listing documents: {e}")
        return []

def main():
    """Main setup function."""
    print("\n" + "="*70)
    print("SUPPORTMIND AI - ADMIN SETUP & DOCUMENT UPLOAD")
    print("="*70)

    # Step 1: Create admin user
    email, password = create_admin_user()
    if not email:
        print("\n[-] Failed to create admin user, exiting...")
        return False

    # Step 2: Wait for backend
    if not wait_for_backend():
        print("\n[-] Backend is not running!")
        print("[*] Start the backend with:")
        print("    python -m uvicorn app.main:app --reload")
        return False

    # Step 3: Login and get token
    token = login_and_get_token(email, password)
    if not token:
        print("\n[-] Failed to get authentication token")
        return False

    # Step 4: Find and upload documents
    uploads_dir = "./uploads"
    if not os.path.exists(uploads_dir):
        print(f"\n[-] Uploads directory not found: {uploads_dir}")
        print("[*] Run setup_kaggle_dataset.py first to prepare documents")
        return False

    # Get all files to upload
    files_to_upload = []
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(file)
            if ext.lower() in ['.txt', '.pdf', '.docx']:
                files_to_upload.append(file_path)

    if not files_to_upload:
        print(f"\n[-] No documents found in {uploads_dir}")
        print("[*] Supported formats: .txt, .pdf, .docx")
        return False

    print(f"\n[*] Found {len(files_to_upload)} document(s) to upload")

    # Step 5: Upload each document
    uploaded_count = 0
    for file_path in files_to_upload:
        if upload_document(token, file_path):
            uploaded_count += 1
            time.sleep(1)  # Small delay between uploads

    # Step 6: List uploaded documents
    documents = list_documents(token)

    # Summary
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print(f"\n[+] Admin Account Created:")
    print(f"    Email: {email}")
    print(f"    Password: {password}")
    print(f"\n[+] Documents Uploaded: {uploaded_count}/{len(files_to_upload)}")
    print(f"\n[+] Total Documents in Knowledge Base: {len(documents)}")

    print("\n[*] NEXT STEPS:")
    print("    1. Start frontend: npm run dev (in frontend directory)")
    print("    2. Open http://localhost:5173 in your browser")
    print("    3. Login with:")
    print(f"       Email: {email}")
    print(f"       Password: {password}")
    print("    4. Go to /chat and start asking questions!")

    print("\n[+] Example questions to try:")
    print("    - 'What should I do if I have a fever?'")
    print("    - 'How do I perform CPR?'")
    print("    - 'What are the benefits of exercise?'")

    print("\n" + "="*70 + "\n")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[-] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
