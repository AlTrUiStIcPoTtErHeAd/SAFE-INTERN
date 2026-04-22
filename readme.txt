🛡️ SAFE-INTERN

SAFE-INTERN is an AI-powered internship scam detection platform designed to help students identify suspicious internship offers, fake recruiters, fraudulent HR messages, phishing emails, fake offer letters, and scam job postings.

The platform combines Machine Learning, rule-based pattern detection, OCR support, PDF/DOCX parsing, and risk scoring to analyze internship-related content and classify it as Safe, Low Risk, Medium Risk, High Risk, or Scam Likely.

⸻

🚀 Features

* Internship scam detection using Machine Learning + rule-based scoring
* Detects fake HR messages, phishing emails, and suspicious recruiters
* Supports pasted text, emails, PDFs, DOCX files, screenshots, and offer letters
* OCR support for uploaded screenshots and images
* Detects:
    * Registration fee scams
    * Security deposit scams
    * UPI payment requests
    * OTP requests
    * Aadhaar / PAN / Passport requests
    * Suspicious bank details and IFSC codes
    * Gmail/Yahoo recruiter emails
    * Fake offer letters
    * Fake LinkedIn recruiters
    * Telegram / WhatsApp scams
    * Unrealistic salary promises
    * “Limited seats” / “Pay now” urgency tactics
* Downloadable JSON report
* Clean Streamlit UI with tabs, risk badges, progress bars, and detailed breakdowns

⸻

🧠 Tech Stack

Category	Technologies
Frontend	Streamlit
Backend	Python 3.11
Machine Learning	Scikit-learn, TF-IDF, Logistic Regression
NLP	SpaCy
OCR	Pytesseract, Pillow
File Parsing	PyMuPDF, python-docx
Optional Integrations	Gemini API, CrewAI

⸻

📂 Project Structure

SAFE-INTERN/
│
├── agents/
│   ├── ml_agent.py
│   ├── planner_agent.py
│
├── utils/
│   ├── file_parser.py
│   ├── pattern_detector.py
│
├── ml/
│   ├── model.pkl
│   ├── vectorizer.pkl
│
├── screenshots/
│   ├── home.png
│   ├── high_risk_detection.png
│   ├── low_risk_detection.png
│   ├── ml_risk_breakdown.png
│   ├── scam_indicators_found.png
│
├── app.py
├── requirements.txt
├── smoke_test.py
└── README.md

⸻

⚙️ Installation

Clone the repository:

git clone <your-repository-link>
cd SAFE-INTERN

Create virtual environment:

python3 -m venv venv

Activate virtual environment:

macOS / Linux

source venv/bin/activate

Windows

venv\Scripts\activate

Install dependencies:

python3 -m pip install -r requirements.txt

Run the Streamlit application:

python3 -m streamlit run app.py

The app will run at:

http://localhost:8501

⸻

## Screenshots

### Home Dashboard
![Home Dashboard](Screenshots/home.png)

### Low Risk Detection
![Low Risk Detection](Screenshots/low_risk_detection.png)

### High Risk Detection
![High Risk Detection](Screenshots/high_risk_detection.png)

### ML Risk Breakdown
![ML Risk Breakdown](Screenshots/ml_risk_breakdown.png)

### Scam Indicators Found
![Scam Indicators Found](Screenshots/scam_indicators_found.png)

⸻

🔍 Scam Patterns Detected

SAFE-INTERN can identify several common internship scam patterns:

Scam Pattern	Example
Registration Fee Scam	“Pay ₹1999 to confirm your internship seat”
Security Deposit Scam	“Refundable deposit required before joining”
Fake Recruiter Scam	“HR contacting from Gmail instead of company email”
Telegram / WhatsApp Scam	“Continue on Telegram for selection process”
Fake Offer Letter Scam	“Offer letter sent before interview”
OTP Scam	“Share OTP to verify account”
UPI Payment Scam	“Send payment to abc@upi”
Document Theft Scam	“Send Aadhaar, PAN, Passport immediately”
Urgency Scam	“Limited seats available, pay now”
Unrealistic Salary Scam	“₹90,000/month for freshers with no interview”

⸻

🧮 Risk Labels

Risk Score	Label
0–19	Safe
20–39	Low Risk
40–64	Medium Risk
65–84	High Risk
85–100	Scam Likely

⸻

📄 Supported File Types

File Type	Supported
Text Messages	Yes
Emails	Yes
PDFs	Yes
DOCX Files	Yes
Screenshots / Images	Yes
Offer Letters	Yes
Internship Certificates	Yes

⸻

🛠 Example Scam Message

Congratulations! You are selected for a work-from-home internship.
Pay ₹2,499 registration fee via UPI to confirm your seat.
Send Aadhaar, PAN, and bank details immediately.

✅ Example Safe Message

Interview scheduled through official company email.
No registration fee is required.
Please bring your resume and portfolio.

⸻

🔐 Safety Disclaimer

SAFE-INTERN provides risk guidance and scam detection support. It should not be treated as legal, financial, or cybersecurity advice.

Always verify recruiters through:

* Official company website
* Verified LinkedIn profiles
* Official company email domain
* Placement cell or faculty references

Never share:

* Aadhaar number
* PAN card
* OTP
* UPI PIN
* Bank details
* Passport information

⸻

📌 Future Improvements

* Real-time recruiter verification
* Domain reputation checking
* VirusTotal integration for suspicious links
* Email authenticity detection
* More advanced NLP models
* Better OCR for blurred screenshots
* Dashboard analytics for institutions

⸻

👨‍💻 Author

Built with Python, Streamlit, and Machine Learning to help students stay safe from internship scams.

If you found this project useful, consider giving it a star.
