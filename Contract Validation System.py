import os
import hashlib
import pytesseract
from pypdf import PdfReader
from langchain_ollama import ChatOllama

# Direct hook into your Windows Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def extract_text_from_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception:
        pass
        
    # Windows OCR Fallback for scanned paper documents or phone photos saved as PDF
    if len(text.strip()) < 50:
        try:
            text = pytesseract.image_to_string(file_path)
        except Exception:
            text = "[OCR Failed: Image unreadable]"
            
    return text

def run_personal_audit(folder_path="./my_personal_contracts"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"📁 Created folder at '{folder_path}'.")
        print("👉 Drop your PDFs (e.g., apartment lease, job offer, subscription terms) in there and run again!")
        return

    # Initialize the local AI brain (Fully Private - your sensitive personal contracts never leave your machine)
    print("🧠 Waking up your local AI Legal Advisor (Llama 3.1)...")
    llm = ChatOllama(model="llama3.1", temperature=0)
    
    seen_hashes = set()

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            
            # Security & Speed check: Skip if we already analyzed this exact file signature
            f_hash = get_file_hash(file_path)
            if f_hash in seen_hashes:
                continue
            seen_hashes.add(f_hash)
            
            print(f"\n🔍 Extracting text from: {file_name}...")
            contract_text = extract_text_from_pdf(file_path)
            
            if not contract_text.strip() or "[OCR Failed" in contract_text:
                print(f"❌ Could not read text layers from {file_name}. Skipping.")
                continue

            print(f"🔬 Auditing {file_name} for hidden risks...")
            
            # Prompt tailored explicitly to protect individual consumers/workers
            personal_audit_prompt = f"""
            You are a protective, highly cynical personal legal advisor helping an individual review a document they are about to sign.
            Your job is to spot traps, sneaky clauses, or unfavorable terms hidden in the text.

            Analyze this contract snippet specifically for:
            1. MONEY RISKS: Hidden fees, auto-renewals, unexpected price hikes, or unrefundable deposits.
            2. ESCAPE RISKS: Strict cancellation policies, long notice periods, or penalties for leaving/terminating early.
            3. RIGHTS RISKS: Does the individual lose ownership of their content, work, data, intellectual property, or right to sue (e.g., forced arbitration)?

            Contract Text:
            {contract_text[:4000]}

            Provide a clear, easy-to-read assessment for the user. Use this exact formatting:
            🔴 RED FLAGS (Critical dangers to watch out for or renegotiate):
            🟡 YELLOW FLAGS (Cautions, tricky phrasing, or things to ask clarity on):
            🟢 GOOD NEWS (Terms that are fair or protect the user):
            """
            
            response = llm.invoke(personal_audit_prompt)
            
            print(f"\n==================================================")
            print(f"📋 PERSONAL RISK REPORT FOR: {file_name.upper()}")
            print(f"==================================================")
            print(response.content)
            print(f"==================================================\n")

if __name__ == "__main__":
    run_personal_audit()
