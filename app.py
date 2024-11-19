import os
import base64
from flask import Flask, request, Response, render_template
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

app = Flask(__name__)

PROJECT_ID = "leafy-unity-436523-a9" 
LOCATION = "us-east1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

MODEL_NAME = "gemini-1.5-flash-002"
GENERATION_CONFIG = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}
SAFETY_SETTINGS = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze-audio", methods=["POST"])
def analyze_audio():
    try:
        if "audioFile" not in request.files:
            return Response("No audio file provided", status=400, mimetype="text/plain")

        audio_file = request.files["audioFile"]

        if audio_file.filename == "":
            return Response("No selected file", status=400, mimetype="text/plain")

        file_path = os.path.join("uploads", audio_file.filename)
        os.makedirs("uploads", exist_ok=True)
        audio_file.save(file_path)

        with open(file_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")

        model = GenerativeModel(MODEL_NAME)
        audio_part = Part.from_data(
            mime_type="audio/wav", data=base64.b64decode(audio_base64)
        )
        prompt = "transcribe and provide a sentiment analysis"
        responses = model.generate_content(
            [audio_part, prompt],
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            stream=True,
        )

        response_text = "".join(response.text for response in responses)
        os.remove(file_path)

        return Response(response_text, mimetype="text/plain")

    except Exception as e:
        return Response(f"Error: {e}", status=500, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
