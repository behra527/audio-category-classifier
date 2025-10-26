# 🔊 Audio Category Classifier  
> 🎧 *AI-powered speech analysis system for call center automation*

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey?logo=flask)
![SpaCy](https://img.shields.io/badge/SpaCy-NLP-green?logo=spacy)
![Whisper](https://img.shields.io/badge/OpenAI-Whisper-orange?logo=openai)
![License](https://img.shields.io/badge/License-MIT-blue)

---

### 🧩 Overview

**Audio Category Classifier** is an intelligent system that listens to **customer call recordings**, converts them into **text**, and automatically classifies them into meaningful categories such as:

> 📅 Appointment Booked · ❌ Not Booked · ⚙️ Complaint · 💬 General Inquiry · 📞 Follow-Up · 🧾 Meeting Scheduled

Built for **call center automation**, it helps companies analyze thousands of calls efficiently — understanding customer intent in real-time.

## 🚀 Features

✅ **Speech-to-Text Conversion**   Accurate transcription with OpenAI Whisper  
✅ **NLP Categorization**          Detects intent and classifies using SpaCy  
✅ **Rule + ML Hybrid Logic**      Easy to modify and retrain  
✅ **Automatic File Organization** Moves audio into category folders  
✅ **Flask REST API** For real-time use with any front-end    
✅ **Scalable Architecture** Ready for production or cloud deployment  


🛠️ Tech Stack
Layer	Technology
Language	Python
Backend	Flask
NLP Engine	SpaCy
Speech Model	OpenAI Whisper
Data Tools	Pandas

## ⚙️ Installation & Setup

### 🪜 1️⃣ Clone Repository
```bash

git clone https://github.com/yourusername/audio-category-classifier.git
cd audio-category-classifier

💻 2️⃣ Create Virtual Environment
bash

Copy code
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

📦 3️⃣ Install Dependencies
bash

Copy code
pip install -r requirements.txt

🧠 4️⃣ Download SpaCy Model
bash

Copy code
python -m spacy download en_core_web_sm
🧾 Example requirements.txt
ini
Copy code
Flask==3.1.0
openai-whisper==20240918
spacy==3.7.2
pandas==2.2.3
psycopg2-binary==2.9.9

🚦 Run the Project
▶️ Run Flask API
bash

Copy code
python app.py
Now open your browser and visit:
👉 http://127.0.0.1:5000/

🎧 Test on Local Audio File
bash

Copy code
python classify_audio.py --file data/samples/call_1.wav

📁 Project Structure
bash

Copy code
audio-category-classifier/
│
├── app.py                  # Flask REST API
├── classify_audio.py        # Main script for classification
├── models/
│   ├── whisper_model.py     # Whisper STT logic
│   ├── nlp_pipeline.py      # NLP analysis
│   └── categorizer.py       # Category matching logic
├── data/
│   ├── samples/             # Input audio files
│   └── categorized/         # Output folders (by category)          
├── requirements.txt
└── README.md

📝 Transcription:

“Hi, I would like to book an appointment for next Tuesday at 10 AM.”

🏷️ Detected Category: Appointment Booked

📦 JSON Response:

json
Copy code
{
  "file_name": "call_102.wav",
  "transcript": "Hi, I would like to book an appointment for next Tuesday at 10 AM.",
  "category": "Appointment Booked",
  "keywords": ["book", "appointment", "Tuesday"],
  "status": "classified"
}

🔮 Future Enhancements
🔊 Speaker Diarization — detect multiple speakers

🗣️ Sentiment Analysis — detect tone and mood

🧾 Automatic Call Summaries using LLMs

📈 Dashboard Analytics using React or Streamlit

🤝 Contributing
Pull requests and suggestions are welcome!
Please open an issue first to discuss changes or improvements.

📜 License
Licensed under the MIT License.
See the LICENSE file for details.

👨‍💻 Author
Muhammad Behram Hassan
📧 muhammadbehramhassan@gmail.com
🌐 GitHub

⭐ If you found this project helpful, please give it a star!








