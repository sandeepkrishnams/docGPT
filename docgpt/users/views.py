from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from docgpt.utils import get_paginated_response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.utils import (
    generate_otp,
    encrypt_token,
    sent_mail_user,
    decrypt_token,
    is_expired
)
from users.user_serializer import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ResetPasswordSerializer,
    UserPasswordUpdateSerializer,
    UserSerializer
)
from users.user_services import (
    register_user,
    delete_user,
    update_user_profile
)


class UserManager(APIView):
    def post(self, request):
        return register_user(request.data)


class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request, id=None):
        paginator = self.pagination_class()
        if request.user.is_superuser:
            if id is None:
                users = User.objects.all().exclude(is_superuser=True).order_by('id')
            else:
                users = User.objects.filter(id=id).exclude(
                    is_superuser=True).order_by('id')
                if not users:
                    return Response({"message": "Invalid ID"}, status=status.HTTP_400_BAD_REQUEST)
            paginated_data = paginator.paginate_queryset(
                users, request)
            serializer = UserSerializer(paginated_data, many=True)
            paginated_response = get_paginated_response(
                paginator, data=serializer.data)
            return Response(paginated_response, status=status.HTTP_200_OK)
        else:
            user = request.user
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)

    def delete(self, request, id=None):
        if request.user.is_superuser:
            if id is None:
                return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            return delete_user(user_id=id)
        if id is not None:
            return Response({"message": "Need admin previlages"}, status=status.HTTP_401_UNAUTHORIZED)
        return delete_user(user_id=request.user.id)

    def put(self, request, id=None):
        if request.user.is_superuser:
            if id is None:
                return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            user_instance = get_object_or_404(User, id=id)
            return update_user_profile(user_instance, request.data)
        else:
            if id is not None:
                return Response({"message": "Need admin previlages"}, status=status.HTTP_401_UNAUTHORIZED)
            return update_user_profile(request.user, request.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserUpdatePassword(APIView):
    # Authentication of the User
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserPasswordUpdateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            old_password = serializer.validated_data['old_password']            # type: ignore # nopep8
            new_password = serializer.validated_data['new_password']            # type: ignore # nopep8

            if not user.check_password(old_password):
                return Response({"error": "password is incorrect"}, status=status.HTTP_403_FORBIDDEN)

            user.set_password(new_password)
            user.save()
            return Response({"Success": "Password Updated Successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):

    def post(self, request):
        username = request.data.get('username')

        user = get_object_or_404(User, username=username)

        otp = generate_otp()
        expire_minutes = settings.FORGOT_TOKEN_EXPIRE_TIME

        # Token creation using utility function
        token = encrypt_token(email=username, otp=otp,
                              expire_minutes=expire_minutes)

        # Send Mail to the user with generated OTP
        if not sent_mail_user(email=username, otp=otp):
            return Response({"error": "Something went wrong with Emailing OTP",
                             "error_code": "SMTP_ERROR"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({"token": token},
                        status=status.HTTP_200_OK)


class ResetPassword(APIView):

    def put(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.data.get('otp')
            new_password = serializer.data.get('new_password')

            token = request.data.get('token')
            token_email, token_otp, expiration_time = decrypt_token(token)
            if token_email is None or token_otp is None or expiration_time is None:
                return Response({"error": "Token in invalid",
                                 "error_code": "INVALID_TOKEN"},
                                status=status.HTTP_401_UNAUTHORIZED)

            expiration_time = datetime.strptime(expiration_time, settings.EXPIRE_TIME_FORMAT)  # type: ignore # nopep8

            user = get_object_or_404(User, username=token_email)

            if not is_expired(expiration_time):
                return Response({"error": "Token expired",
                                 "error_code": "EXPIRED_TOKEN"},
                                status=status.HTTP_401_UNAUTHORIZED)

            if token_otp != otp:
                return Response({"error": "invalid OTP",
                                 "error_code": "INVALID_OTP"},
                                status=status.HTTP_401_UNAUTHORIZED)
            user.set_password(new_password)
            user.save()
            return Response({"Success": "Password Updated Successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
