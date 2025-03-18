from django.shortcuts import render
import pdfplumber
import PyPDF2
import spacy
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Resume
from .serializers import ResumeUploadSerializer

# Create your views here.


nlp = spacy.load("en_core_web_sm")


class ResumeUploadView(generics.CreateAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def extract_text_from_pdf(self,pdf_file):
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    

    def extract_info(self,text):

        doc = nlp(text)
        email = None
        phone = None
        name = None
        skills = []
        experience = []
        education = []

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
            elif ent.label_ == "EMAIL":
                email = ent.text
            elif ent.label_ == "PHONE":
                phone = ent.text

        known_skills = {"Python", "Django", "React", "SQL", "Machine Learning"}
        skills = [token.text for token in doc if token.text in known_skills]

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": ", ".join(skills),
            "experience": "Experience data (To be improved)",  # Placeholder
            "education": "Education data (To be improved)"  # Placeholder
        }        
    


    def post(self,request , *args, **kwargs):
        file_obj = request.FILES["file"]
        resume = Resume.objects.create(user=request.user, file = file_obj)


        if file_obj.name.endswith(".pdf"):
            text = self.extract_text_from_pdf(file_obj)
        else:
            text = "unsupported format"


        extracted_info = self.extract_info(text)


        resume.extracted_text = text
        resume.name = extracted_info["name"]
        resume.email = extracted_info["email"]
        resume.phone = extracted_info["phone"]
        resume.skills = extracted_info["skills"]
        resume.experience = extracted_info["experience"]
        resume.education = extracted_info["education"]
        resume.save()

        return Response({"message": "Resume uploaded & processed", "data": extracted_info}, status=status.HTTP_201_CREATED)        