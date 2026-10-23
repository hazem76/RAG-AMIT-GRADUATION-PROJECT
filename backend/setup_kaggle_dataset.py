"""Script to download and process Kaggle dataset for RAG knowledge base."""
import os
import json
import subprocess
import sys
from pathlib import Path

def setup_kaggle():
    """Set up Kaggle API credentials."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"

    if not kaggle_json.exists():
        print("\n" + "="*60)
        print("KAGGLE API SETUP REQUIRED")
        print("="*60)
        print("\nTo download datasets from Kaggle, you need to:")
        print("1. Go to https://www.kaggle.com/settings/account")
        print("2. Click 'Create New API Token'")
        print("3. This downloads kaggle.json")
        print(f"4. Place it at: {kaggle_json}")
        print("="*60 + "\n")
        return False
    return True

def install_kaggle():
    """Install kaggle package if not installed."""
    try:
        __import__('kaggle')
        print("[+] Kaggle package already installed")
        return True
    except ImportError:
        print("[*] Installing kaggle package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q"])
        print("[+] Kaggle package installed")
        return True

def download_dataset():
    """Download a medical/support dataset from Kaggle."""
    from kaggle.api.kaggle_api_extended import KaggleApi

    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()

    # Dataset choice: Medical Chatbot dataset
    dataset_name = "tawfikelzoubi/medical-chatbot"
    output_dir = "./downloads"

    print(f"\nDownloading dataset: {dataset_name}")
    print(f"Output directory: {output_dir}")

    os.makedirs(output_dir, exist_ok=True)

    try:
        api.dataset_download_files(dataset_name, path=output_dir, unzip=True)
        print(f"[+] Dataset downloaded successfully to {output_dir}")
        return output_dir
    except Exception as e:
        print(f"[-] Failed to download dataset: {e}")
        print("\nAlternative: Using local sample data...")
        return create_sample_dataset()

def create_sample_dataset():
    """Create a sample dataset if Kaggle download fails."""
    output_dir = "./downloads"
    os.makedirs(output_dir, exist_ok=True)

    # Create sample medical/support FAQ document
    sample_content = """Medical Support FAQ and Guidelines

1. GENERAL HEALTH ADVICE
Q: What should I do if I have a fever?
A: If you have a fever above 100.4°F (38°C), follow these steps:
- Rest and stay hydrated
- Take over-the-counter fever reducers like acetaminophen or ibuprofen
- Wear light clothing
- Monitor your temperature
- Contact a doctor if it persists for more than 3 days or reaches 103°F (39.4°C)

Q: How can I prevent the flu?
A: To prevent the flu:
- Get vaccinated annually, preferably before flu season (September-October)
- Wash hands frequently and thoroughly
- Avoid touching your face
- Stay away from sick individuals
- Maintain good nutrition and exercise
- Get adequate sleep
- Cover your cough and sneezes with a tissue

2. INJURY TREATMENT
Q: What is the RICE method for treating injuries?
A: RICE stands for:
- Rest: Stop the activity that caused the injury
- Ice: Apply ice for 15-20 minutes every 2-3 hours for the first 48 hours
- Compression: Use a bandage to reduce swelling
- Elevation: Keep the injured area above heart level

Q: When should I seek medical attention for an injury?
A: Seek immediate medical attention if you experience:
- Severe pain or swelling
- Inability to move the injured part
- Numbness or tingling
- Signs of infection (fever, redness, warmth)
- Suspected fracture or dislocation
- Injury to the head, neck, or spine

3. COMMON MEDICATIONS
Q: What over-the-counter pain relievers are available?
A: Common OTC pain relievers include:
- Ibuprofen (Advil, Motrin): Reduces pain, fever, and inflammation
- Acetaminophen (Tylenol): Reduces pain and fever (not anti-inflammatory)
- Aspirin: Pain relief, fever reduction, and blood thinning
- Naproxen (Aleve): Long-lasting pain and inflammation relief

Q: How should I take antibiotics?
A: Important antibiotic guidelines:
- Always take as prescribed, even if you feel better
- Complete the full course of antibiotics
- Take at the same time each day
- Do not skip doses
- Do not share antibiotics with others
- Report any allergic reactions immediately

4. MENTAL HEALTH
Q: What are signs of depression?
A: Common signs of depression include:
- Persistent sadness or empty mood
- Loss of interest in activities
- Changes in appetite or sleep
- Fatigue or low energy
- Difficulty concentrating
- Feelings of worthlessness or guilt
- Thoughts of death or suicide

Q: What can I do to manage stress?
A: Stress management techniques:
- Practice deep breathing exercises
- Exercise regularly
- Maintain a regular sleep schedule
- Limit caffeine and alcohol
- Practice mindfulness or meditation
- Talk to a therapist or counselor
- Maintain social connections
- Engage in hobbies and relaxation activities

5. NUTRITION AND WELLNESS
Q: What does a balanced diet consist of?
A: A balanced diet should include:
- Fruits and vegetables (50% of plate)
- Whole grains (25% of plate)
- Protein sources (25% of plate)
- Limited saturated fats and sodium
- Adequate water intake (8-10 glasses daily)
- Moderate portion sizes

Q: What are the health benefits of exercise?
A: Regular exercise provides:
- Improved cardiovascular health
- Better weight management
- Stronger bones and muscles
- Enhanced mental health and mood
- Reduced risk of chronic diseases
- Better sleep quality
- Increased energy levels

Recommendation: Aim for 150 minutes of moderate aerobic activity weekly, plus strength training 2 days per week.

6. PREVENTIVE CARE
Q: What vaccinations do I need as an adult?
A: Common adult vaccinations include:
- Influenza (annual)
- Pneumonia (65+ or with certain conditions)
- Tdap (tetanus, diphtheria, pertussis)
- Shingles vaccine (50+)
- COVID-19 vaccine
- Consult your doctor for your specific needs

Q: How often should I have health screenings?
A: Recommended screening frequencies:
- Blood pressure: Annually or as advised
- Cholesterol: Every 4-6 years (more often if elevated)
- Diabetes screening: Starting at age 45, then every 3 years
- Cancer screenings: Follow age and risk-based guidelines
- Comprehensive physical exam: Annually

7. EMERGENCY SITUATIONS
Q: What should I do in case of a heart attack?
A: Signs and immediate response:
- Call emergency services (911) immediately
- Chew aspirin if not allergic (unless contraindicated)
- Stop physical activity and rest
- Loosen tight clothing
- Remain calm
- Open the door for emergency responders
- Don't drive yourself to the hospital

Q: How do I perform CPR?
A: Basic CPR steps:
1. Check for responsiveness and call emergency services
2. Place person on firm, flat surface
3. Position your hands: Place heel of one hand on chest center
4. Push hard and fast at 100-120 compressions per minute
5. Give 30 compressions
6. Give 2 rescue breaths (tilt head, lift chin, seal mouth)
7. Continue until help arrives or person shows signs of life

Note: Proper CPR training is recommended for all adults.

8. CHRONIC DISEASE MANAGEMENT
Q: How should I manage diabetes?
A: Diabetes management involves:
- Regular blood sugar monitoring
- Taking prescribed medications as directed
- Following a healthy diet
- Regular exercise
- Weight management
- Regular check-ups with healthcare provider
- Foot care and skin care
- Managing stress
- Getting adequate sleep

Q: What are lifestyle changes for managing hypertension?
A: Blood pressure management:
- Reduce salt intake (less than 2,300mg daily)
- Exercise regularly (150 minutes/week)
- Maintain healthy weight
- Limit alcohol consumption
- Reduce stress through relaxation techniques
- Eat heart-healthy diet (DASH diet recommended)
- Monitor blood pressure regularly
- Take medications as prescribed

These guidelines are for informational purposes and should not replace professional medical advice.
For personalized medical advice, please consult with a qualified healthcare provider."""

    sample_file = os.path.join(output_dir, "medical_support_faq.txt")
    with open(sample_file, 'w') as f:
        f.write(sample_content)

    print(f"[+] Sample dataset created at {sample_file}")
    return output_dir

def convert_to_txt(downloads_dir):
    """Convert dataset files to TXT format for processing."""
    uploads_dir = "./uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    txt_files = []

    # Process existing files in downloads directory
    if os.path.exists(downloads_dir):
        for file in os.listdir(downloads_dir):
            file_path = os.path.join(downloads_dir, file)

            if file.endswith('.txt'):
                # Copy existing TXT files
                dest = os.path.join(uploads_dir, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
                    content = src.read()
                    with open(dest, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                txt_files.append(dest)
                print(f"[+] Processed: {file}")

            elif file.endswith('.json'):
                # Convert JSON to TXT
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    content = json.dumps(data, indent=2)
                    txt_file = os.path.join(uploads_dir, f"{os.path.splitext(file)[0]}.txt")
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    txt_files.append(txt_file)
                    print(f"[+] Converted: {file} -> {os.path.basename(txt_file)}")
                except Exception as e:
                    print(f"[-] Error processing {file}: {e}")

    return txt_files

def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("KAGGLE DATASET SETUP FOR RAG")
    print("="*60)

    # Install kaggle package
    if not install_kaggle():
        sys.exit(1)

    # Set up Kaggle credentials
    if not setup_kaggle():
        print("\nNote: Setting up Kaggle credentials is optional.")
        print("Without them, a sample medical FAQ dataset will be used.\n")

    # Download dataset
    downloads_dir = download_dataset()

    # Convert to TXT files
    print("\nProcessing dataset files...")
    txt_files = convert_to_txt(downloads_dir)

    if txt_files:
        print(f"\n[+] Successfully prepared {len(txt_files)} file(s):")
        for f in txt_files:
            print(f"  - {f}")

        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Start the backend: python -m uvicorn app.main:app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Login to the application")
        print("4. Go to /knowledge-base and upload the files:")
        for f in txt_files:
            print(f"     - {os.path.basename(f)}")
        print("5. Go to /chat and start asking questions!")
        print("="*60 + "\n")
    else:
        print("\n[-] No files could be processed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
