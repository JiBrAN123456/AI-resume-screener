from django.shortcuts import render
import pdfplumber
import spacy
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from fuzzywuzzy import process
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Resume
from .serializers import ResumeUploadSerializer
import nltk

# ✅ Download NLTK resources
nltk.download("punkt")
nltk.download("stopwords")

# ✅ Set the NLTK data path
nltk.data.path.append("C:\\Users\\yunis\\AppData\\Roaming\\nltk_data")

nlp = spacy.load("en_core_web_sm")

# ✅ Predefined skills for fuzzy matching
SKILL_SET = {
    "Python", "Django", "Flask", "FastAPI", "SQL", "PostgreSQL", "MongoDB", "Machine Learning",
    "Deep Learning", "Computer Vision", "NLP", "TensorFlow", "PyTorch", "AWS", "Azure", "Docker",
    "Kubernetes", "React", "Node.js", "Java", "C++", "Data Science", "Big Data", "Hadoop"
}

class ResumeUploadView(generics.CreateAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file."""
        text = ""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return None
        
        text = text.replace("\x00", "")
        return text.strip() if text else None

    def extract_info(self, text):
        """Extract candidate details from resume text."""
        doc = nlp(text)
        email = None
        phone = None
        name = None

        # ✅ Extract Email using Regex
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        if email_match:
            email = email_match.group(0)

        # ✅ Extract Phone Number using Regex (supports international numbers)
        phone_match = re.search(r"\+?\d{1,3}[-.\s]?\(?\d{2,5}\)?[-.\s]?\d{2,5}[-.\s]?\d{2,5}", text)
        if phone_match:
            phone = phone_match.group(0)

        # ✅ Extract Name (First detected PERSON entity)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

        # ✅ Extract Skills using Fuzzy Matching
        words = word_tokenize(text)
        stop_words = set(stopwords.words("english"))
        filtered_words = [word for word in words if word.lower() not in stop_words]
        
        extracted_skills = set()
        for word in filtered_words:
            match, score = process.extractOne(word, SKILL_SET)
            if score > 85:
                extracted_skills.add(match)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": ", ".join(set(extracted_skills)),
            "experience": "Experience data (To be improved)",
            "education": "Education data (To be improved)"
        }        

    def post(self, request, *args, **kwargs):
        """Handle resume file upload and extract details."""
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES["file"]
        
        # ✅ Extract text from PDF
        if file_obj.name.endswith(".pdf"):
            text = self.extract_text_from_pdf(file_obj)
            if not text:
                return Response({"error": "Failed to extract text from PDF"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Unsupported file format. Only PDFs are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Extract resume details
        extracted_info = self.extract_info(text)

        # ✅ Save resume in DB
        serializer = self.get_serializer(data={"user": request.user.id, "file": file_obj})
        if serializer.is_valid():
            resume = serializer.save(
                extracted_text=text,
                name=extracted_info["name"],
                email=extracted_info["email"],
                phone=extracted_info["phone"],
                skills=extracted_info["skills"],
                experience=extracted_info["experience"],
                education=extracted_info["education"],
            )
            return Response({"message": "Resume uploaded & processed", "data": extracted_info}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ResumeRankView(APIView):
    permission_classes = [IsAuthenticated]

    def rank_resume_against_job(self, resume_text, job_description):
        """Rank resume relevance to job description."""
        if not resume_text or not job_description:
            return 0  # ✅ Return 0 if any text is empty
        
        # ✅ Tokenize and convert to lowercase
        resume_tokens = set(word_tokenize(resume_text.lower()))
        job_tokens = set(word_tokenize(job_description.lower()))

        # ✅ Remove stopwords
        stop_words = set(stopwords.words("english"))
        resume_tokens = {word for word in resume_tokens if word not in stop_words}
        job_tokens = {word for word in job_tokens if word not in stop_words}

        # ✅ Avoid division by zero
        if not job_tokens:
            return 0  

        # ✅ Calculate relevance score
        matching_keywords = resume_tokens.intersection(job_tokens)
        score = (len(matching_keywords) / len(job_tokens)) * 100  

        return round(score, 2)

    def post(self, request):
        """Rank all resumes against job description."""
        job_description = request.data.get("job_description")
        if not job_description:
            return Response({"error": "Job description is required"}, status=400)
        
        resumes = Resume.objects.all()
        ranked_resumes = []

        for resume in resumes:
            score = self.rank_resume_against_job(resume.extracted_text, job_description)
            ranked_resumes.append({
                "id": str(resume.id),
                "name": resume.name,
                "email": resume.email,
                "phone": resume.phone,
                "skills": resume.skills,
                "score": score
            })

        # ✅ Sort resumes by score **outside** the loop
        ranked_resumes = sorted(ranked_resumes, key=lambda x: x["score"], reverse=True)

        return Response({"ranked_resumes": ranked_resumes}, status=200)
