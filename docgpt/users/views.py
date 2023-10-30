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
    is_expired,
    delete_solr_user_data,
    encrypt_user_token,
    decrypt_user_token,
)
from users.user_serializer import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ResetPasswordSerializer,
    UserPasswordUpdateSerializer,
    UserSerializer,
    IsActiveSerializer,
    UserSignUPVerifierSerializer
)
from users.user_services import (
    register_user,
    delete_user,
    update_user_profile
)
from django.db.models import Q
from datetime import datetime


class UserManager(APIView):
    def post(self, request):
        return register_user(request.data)


class UserSignUPManager(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        is_user_exists = User.objects.filter(username=username).exists()

        if is_user_exists:
            return Response("User already exists.", status=status.HTTP_409_CONFLICT)

        otp = generate_otp()
        if not sent_mail_user(email=username, otp=otp):
            return Response({"error": "Something went wrong with Emailing OTP",
                             "error_code": "SMTP_ERROR"},
                            status=status.HTTP_400_BAD_REQUEST)
        expire_minutes = settings.SIGNUP_TOKEN_EXPIRE_TIME
        token = encrypt_user_token(
            username, password, first_name, last_name, otp, expire_minutes)
        return Response(token, status=status.HTTP_200_OK)


class UserSignUPVerifier(APIView):
    def post(self, request):
        serializer = UserSignUPVerifierSerializer(data=request.data)
        if serializer.is_valid():
            user_otp = request.data.get('otp')
            token = request.data.get('token')
            try:
                username, password, first_name, last_name, otp, expiration_time = decrypt_user_token(
                    token)
                print(username, password, first_name,
                      last_name, otp, expiration_time)
                if None in (username, password, first_name, last_name, otp, expiration_time):
                    return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception:
                return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
            expiration_time = datetime.strptime(
                expiration_time, settings.EXPIRE_TIME_FORMAT)

            if not is_expired(expiration_time):
                return Response({"error": "Token expired",
                                 "error_code": "EXPIRED_TOKEN"},
                                status=status.HTTP_401_UNAUTHORIZED)
            if otp != user_otp:
                return Response({"error": "wrong OTP",
                                 "error_code": "WRONG OTP"},
                                status=status.HTTP_401_UNAUTHORIZED)
            user_data = {
                'username': username,
                'password': password,
                'first_name': first_name,
                'last_name': last_name
            }
            return register_user(user_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request, id=None):
        paginator = self.pagination_class()
        if request.user.is_superuser:
            if id is None:
                query_params = request.query_params
                search_term = query_params.get('search')
                start_date = query_params.get('start_date')
                end_date = query_params.get('end_date')
                sortparam = query_params.get('sortparam')
                sortdorder = query_params.get('sortorder')

                users = User.objects.filter(
                    ~Q(is_superuser=True))

                if sortdorder == 'asc':
                    sort_order = ''
                else:
                    sort_order = '-'

                if sortparam == 'username':
                    users = users.order_by(f'{sort_order}username')
                elif sortparam == 'first_name':
                    users = users.order_by(f'{sort_order}first_name')
                else:
                    users = users.order_by(f'{sort_order}date_joined')

                if search_term:
                    users = users.filter(Q(username__icontains=search_term) | Q(
                        first_name__icontains=search_term))

                if start_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    users = users.filter(Q(date_joined__gte=start_date))

                if end_date:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    users = users.filter(Q(date_joined__lte=end_date))

            else:
                users = User.objects.filter(id=id).exclude(
                    is_superuser=True).order_by('first_name')
                if not users:
                    return Response({"message": "Invalid ID"}, status=status.HTTP_400_BAD_REQUEST)

            paginated_data = paginator.paginate_queryset(users, request)
            serializer = UserSerializer(paginated_data, many=True)
            paginated_response = get_paginated_response(
                paginator, data=serializer.data)

            superuser = User.objects.filter(is_superuser=True).filter(
                id=request.user.id).order_by('first_name')
            superuser_serializer = UserSerializer(superuser, many=True)

            response_data = {
                'superuser': superuser_serializer.data,
                'regular_users': paginated_response,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            user = request.user
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)

    def delete(self, request, id=None):
        if request.user.is_superuser:
            if id is None:
                return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            delete_solr_user_data(id)
            return delete_user(user_id=id)
        if id is not None:
            return Response({"message": "Need admin previlages"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            res = delete_solr_user_data(request.user.id)
            print(f'solr : {res}')
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
            try:
                token_email, token_otp, expiration_time = decrypt_token(token)
                if None in (token_email, token_otp, expiration_time):
                    return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception:
                return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

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


class UserUpdateIsActiveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if pk is None:
            raise Http404
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = IsActiveSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
