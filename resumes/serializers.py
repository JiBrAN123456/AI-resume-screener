from rest_framework import serializers
from .models import Resume

class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'user', 'file' , "uploaded_at"]

    def assign(self,validated_data):

        validated_data['user'] = self.context["request"].user
        return super().create(validated_data)
     