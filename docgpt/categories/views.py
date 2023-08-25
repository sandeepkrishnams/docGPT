from django.contrib.auth.decorators import permission_required, login_required
from categories.models import Category
from categories.category_serializer import CategorySerializer, CategoryUpdateSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from categories.permissions import SuperuserPermission


class CategoryListView(APIView):

    authentication_classes = [JWTAuthentication]

    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, SuperuserPermission]
        super().initial(request, *args, **kwargs)

    def post(self, request):
        serializer = CategoryUpdateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"response": serializer.data, "message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id=None):
        if id is not None:
            try:
                category = Category.objects.get(id=id)
                serializer = CategorySerializer(category)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id=None):
        if id is not None:
            try:
                category = Category.objects.get(id=id)
                category.delete()
                return Response(f"Category '{category.category}' Deleted.", status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response(f"Category with ID '{id}' doesn't exist.", status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "No id Provided in url"}, status=status.HTTP_404_NOT_FOUND)
