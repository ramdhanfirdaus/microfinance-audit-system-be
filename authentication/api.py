from django.forms import ValidationError
from django.http import HttpResponse

from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import Auditor
from .serializer import RegisterSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

#Register API

class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]
    
    def post(self, request, *args,  **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return HttpResponse(serializer.errors)

        user = serializer.save()

        auditor = Auditor(user=User.objects.get(username=user))
        auditor.save()

        return Response({
            "user": UserSerializer(user,    context=self.get_serializer_context()).data,
            "message": "User Created Successfully.  Now perform Login to get your token",
        })

class InfoTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['is_staff'] = self.user.is_staff
        return data


class InfoTokenObtainPairView(TokenObtainPairView):
    serializer_class = InfoTokenObtainPairSerializer