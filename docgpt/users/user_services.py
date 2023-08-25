from rest_framework import status
from rest_framework.response import Response

from users.user_serializer import UserSignUpSerializer, UserProfileUpdateSerializer
from django.contrib.auth.models import User


def register_user(request_data):
    serializer = UserSignUpSerializer(data=request_data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({"response": serializer.data, "message": "Registration successful"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_user_profile(user_instance, request_data):
    serializer = UserProfileUpdateSerializer(
        user_instance, data=request_data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({"response": serializer.data, "message": "Profile updated successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": f"User with ID {user_id} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
