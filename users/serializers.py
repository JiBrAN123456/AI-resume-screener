from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',  'email', 'company', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ['id',  'email', 'company', 'role']

    def create(self, validated_data):
        user = User.onjects.create_user(**validated_data)
        return user    
    

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only= True)

    def validate(self , data):
        user = User.objects.filter(email = data['email']).first()    
        if user and user.check_password(data['password']):
            tokens = RefreshToken.for_user(user)
            return {
                'refresh' : str(tokens),
                'access' : str(tokens.access_token),
                'user' : UserSerializer(user).data,
            }
        raise serializers.ValidationError("Invalid credentials")