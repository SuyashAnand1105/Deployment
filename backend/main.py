from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import os
import io
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI / NexusAI client
client = OpenAI(
    api_key=os.environ["NEXUS_API_KEY"],
    base_url="https://apidev.navigatelabsai.com"
)

@app.get("/")
def root():
    return {"message": "NexusAI Resume Parser Backend is running"}

@app.post("/api/parse")
async def parse_resume(resume: UploadFile = File(...)):
    try:
        content = await resume.read()

        text = ""

        if resume.filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text += (page.extract_text() or "") + "\n"
        else:
            try:
                text = content.decode("utf-8")
            except:
                raise HTTPException(status_code=400, detail="Only PDF supported")

        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty resume text")

        system_prompt = """
        You are an expert AI resume parser.
        Return ONLY valid JSON in this structure:
        {
          "personalInfo": {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedIn": ""
          },
          "summary": "",
          "skills": [],
          "experience": [],
          "education": []
        }
        """

        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )

        result_text = response.choices[0].message.content.strip()

        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "")

        parsed_data = json.loads(result_text)

        return {"success": True, "data": parsed_data}

    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON from model"}
    except Exception as e:
        return {"success": False, "error": str(e)}