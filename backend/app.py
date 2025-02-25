import os
import datetime
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from flask_cors import CORS
from openai import OpenAI

# Load environment variables first
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Add JSON error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Configure app settings
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["UPLOAD_LIMIT"] = 5 * 1024 * 1024  # 5MB

# Initialize OpenAI client globally
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize services with connection checks
try:
    # Initialize MongoDB
    mongo = PyMongo(app)
    mongo.db.command("ping")  # Test connection immediately
    print("✅ MongoDB connection successful!")

except Exception as e:
    print(f"❌ Service initialization failed: {str(e)}")
    raise RuntimeError(f"Service initialization failed: {str(e)}") from e


# Helper functions
def extract_text(file_content, filename):
    try:
        if filename.endswith(".pdf"):
            pdf = PdfReader(BytesIO(file_content))
            text = "\n".join(
                [page.extract_text() for page in pdf.pages if page.extract_text()]
            )
        elif filename.endswith(".docx"):
            doc = Document(BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs if para.text])
        else:
            raise ValueError(
                "Unsupported file format. Only PDF and DOCX files are allowed."
            )
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text: {str(e)}")


def extract_skills(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Extract only technical skills from this resume. Return comma-separated values:\n{text}",
                }
            ],
        )
        skills = response.choices[0].message.content.split(",")
        return [s.strip() for s in skills if s.strip()]
    except Exception as e:
        raise RuntimeError(f"AI processing error: {str(e)}")


# Routes
@app.route("/")
def home():
    return "Backend is running! 🚀"


@app.route("/upload", methods=["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Check file size
        file_content = file.read()
        if len(file_content) > app.config["UPLOAD_LIMIT"]:
            return jsonify({"error": "File size exceeds 5MB limit"}), 413

        # Process file
        text = extract_text(file_content, file.filename)
        skills = extract_skills(text)

        # Save to MongoDB
        result = mongo.db.resumes.insert_one(
            {
                "filename": file.filename,
                "skills": skills,
                "text": text,
                "timestamp": datetime.datetime.utcnow(),
            }
        )

        return jsonify(
            {"success": True, "skills": skills, "document_id": str(result.inserted_id)}
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    print("🔄 Starting Flask server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
    print("🚀 Server is running at http://localhost:5000")
