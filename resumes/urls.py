from django.urls import path
from .views import ResumeUploadView , ResumeRankView

urlpatterns = [
    path("upload/", ResumeUploadView.as_view(), name="resume_upload"),
    path("rank/", ResumeRankView.as_view(), name="resume_ranking"),
]
