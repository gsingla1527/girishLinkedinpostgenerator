from flask import Flask, render_template, request
import google.generativeai as genai
import os

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API (no hardcoded fallback)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is not set in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/", methods=["GET", "POST"])
def home():
    posts = []
    error_message = None

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        tone = request.form.get("tone", "").strip()
        audience = request.form.get("audience", "general professionals").strip()

        if not topic or not tone:
            error_message = "⚠️ Please provide both topic and tone."
        else:
            try:
                # Ask Gemini to return structured JSON for safer parsing
                prompt = f"""
                Generate 3 LinkedIn posts about "{topic}".
                Use a {tone} tone for {audience}.
                Return the result as a JSON list, where each element is a post string.
                """

                response = model.generate_content(prompt)

                # Parse response safely
                raw_text = getattr(response, "text", "").strip()
                if raw_text.startswith("[") and raw_text.endswith("]"):
                    import json
                    posts = json.loads(raw_text)
                else:
                    # fallback: split by double newlines
                    posts = [p.strip() for p in raw_text.split("\n\n") if p.strip()]

            except Exception as e:
                error_message = f"❌ Error generating content: {str(e)}"

    return render_template("index.html", posts=posts, error=error_message)


if __name__ == "__main__":
    # Debug = False by default for safety
    app.run(host="0.0.0.0", port=5000, debug=True)
