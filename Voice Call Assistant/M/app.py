from flask import Flask, request, jsonify, render_template
import whisper
import spacy
from spacy.matcher import PhraseMatcher
from werkzeug.utils import secure_filename
import os
import subprocess
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment
import rapidfuzz

# === Whisper local cache path (for offline use) ===
os.environ["XDG_CACHE_HOME"] = os.path.abspath("whisper_cache")
os.environ["PATH"] += os.pathsep + os.path.join(
    os.getcwd(), "ffmpeg-7.1.1-essentials_build", "ffmpeg-7.1.1-essentials_build", "bin"
)

# === Set ffmpeg path for pydub ===
AudioSegment.converter = os.path.join(
    os.getcwd(), "ffmpeg-7.1.1-essentials_build", "ffmpeg-7.1.1-essentials_build", "bin", "ffmpeg.exe"
)

# === Flask setup ===
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# === Load models at startup ===
print("\U0001F501 Loading Whisper model and spaCy...")
whisper_model = whisper.load_model("base")
nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# === Appointment categories (same as your current list) ===
APPOINTMENT_CATEGORIES = {
    "Specific appointment or walk-in time / range within 1 hour": [
        "i'll be there at", "i can come at", "i'll reach by", "i'll be there around", 
        "put me down for", "i'll see you then", "drop it off before", 
        "can i drop off at", "be there in 30 minutes", "i'm on my way now", 
        "being towed there now", "you can come now", "come in now", 
        "ten thirty am works for me", "coming in at", "reaching in 30", 
        "i'm heading over now", "on my way to you", "i'll swing by at"
    ],

    "Unscheduled walk-in or loose appointment time / range exceeding 1 hour": [
        "sometime between twelve and four", "next tuesday", "drop by when i can", 
        "i might walk in", "i'll come sometime", "i might stop by", "maybe around", 
        "not sure what time", "will try to come", "whenever i get a chance", 
        "possibly during the afternoon", "i'll see what time works", 
        "could be around noon", "no fixed time yet", "i'll come by later today"
    ],

    "Appointment requested/mentioned but not set": [
        "i want to schedule", "i want to make an appointment", "can i book something", 
        "looking to schedule", "want to get on the calendar", 
        "i'd like to plan something", "hoping to set an appointment", 
        "i'm planning to get it serviced", "haven't picked a day yet", 
        "just calling to get some info", "do you have anything available", 
        "can i talk to someone about scheduling", "is there any time available", 
        "do you have slots open", "need to schedule", "can i check availability"
    ],

    "No appointment, walk-in, or drop-off discussed": [
        "battery replacement", "how much does battery replacement cost", 
        "check engine light", "my car has a problem", "engine issue", 
        "just wanted to ask about pricing", "what's the cost for", 
        "do you repair", "inquiry about service", "need some information on", 
        "what are your rates", "how much would it cost to fix"
    ],

    "Upcoming scheduled appointment": [
        "already booked", "booked a brake inspection", "have an appointment", 
        "for friday at three pm", "just wanted to confirm", "appointment is at", 
        "scheduled for tomorrow", "i'm coming in on", "my appointment is next week", 
        "already scheduled", "scheduled to come in", "we already have a time"
    ],

    "Vehicle already in service": [
        "car was towed to your shop", "due to a breakdown", "diagnostic has been started", 
        "already towed", "already in service", "car is there already", 
        "vehicle is at your place", "it's already being looked at", 
        "currently in service", "you guys already have my car", 
        "in your shop now", "you started work already"
    ],

    "Not an appointment opportunity": [
        "my bumper got damaged", "minor accident", "do you do body work", 
        "call a collision repair center", "collision", "car wash", 
        "interested in a paint job", "do you offer detailing", 
        "asking about cleaning", "just need cosmetic work", 
        "only need touch up", "no repairs, just asking", "not service related"
    ],

    "Correction: caller never connected to a live, qualified agent": [
        "automated system", "left a voicemail", "voicemail for a call back", 
        "tried calling earlier", "leave a message", "couldn't reach anyone", 
        "just got the answering machine", "no one picked up", 
        "sent a voicemail", "please call me back", "nobody answered"
    ]
}
# === Add patterns to matcher ===
for label, phrases in APPOINTMENT_CATEGORIES.items():
    matcher.add(label, [nlp.make_doc(p) for p in phrases])

# === Audio Chunking Helper ===
def chunk_audio(path, chunk_length_ms=30000):  # 30 seconds
    print("\U0001F9FB Splitting audio into chunks...")
    audio = AudioSegment.from_wav(path)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    chunk_paths = []
    for i, chunk in enumerate(chunks):
        chunk_path = path.replace(".wav", f"_chunk{i}.wav")
        chunk.export(chunk_path, format="wav")
        chunk_paths.append(chunk_path)
    return chunk_paths

# === Routes ===
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def handle_upload():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    converted_path = os.path.join(app.config['UPLOAD_FOLDER'], "converted.wav")
    denoised_path = os.path.join(app.config['UPLOAD_FOLDER'], "denoised.wav")
    file.save(input_path)

    print(f"\U0001F4E5 Uploaded: {input_path}")
    print(f"\U0001F504 Will convert to WAV: {converted_path}")

    try:
        subprocess.run([
            AudioSegment.converter, "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", converted_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("\u2705 FFmpeg conversion complete")
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "FFmpeg conversion failed"}), 500

    try:
        print(f"\U0001F50A Reading WAV file: {converted_path}")
        data, rate = sf.read(converted_path)
        reduced = nr.reduce_noise(y=data, sr=rate)
        sf.write(denoised_path, reduced, rate)
        print(f"\u2705 Denoised WAV saved: {denoised_path}")
    except Exception as e:
        return jsonify({"error": f"Noise reduction failed: {str(e)}"}), 500

    try:
        chunk_paths = chunk_audio(denoised_path)
        final_transcript = ""
        for chunk_path in chunk_paths:
            print(f"\U0001F9E0 Transcribing chunk: {chunk_path}")
            result = whisper_model.transcribe(chunk_path, fp16=False)
            final_transcript += " " + result["text"]
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    doc = nlp(final_transcript.lower())
    matches = matcher(doc)
    best_category = None
    best_score = 0
    # Check spaCy matches and get best fuzzy score for each
    for m_id, _, _ in matches:
        category = nlp.vocab.strings[m_id]
        for phrase in APPOINTMENT_CATEGORIES[category]:
            score = rapidfuzz.fuzz.partial_ratio(final_transcript.lower(), phrase.lower())
            if score > best_score:
                best_score = score
                best_category = category
    # If no spaCy match, do fuzzy matching for all categories
    if not best_category:
        for category, phrases in APPOINTMENT_CATEGORIES.items():
            for phrase in phrases:
                score = rapidfuzz.fuzz.partial_ratio(final_transcript.lower(), phrase.lower())
                if score > best_score:
                    best_score = score
                    best_category = category
    if best_score >= 70 and best_category:
        detected = [f"{best_category} (fuzzy match: {best_score}%)"]
    else:
        detected = ["Other - no match found"]

    print(f"\U0001F3F7️ Categories matched: {detected}")

    return jsonify({
        "transcript": final_transcript.strip(),
        "appointment_categories": detected
    })

# === Run app ===
if __name__ == "__main__":
    app.run(debug=True)
