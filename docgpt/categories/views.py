from categories.models import Category
from categories.category_serializer import CategorySerializer, CategoryUpdateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from categories.permissions import SuperuserPermission
from documents.models import Document


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
                category = Category.objects.get(id=id).order_by('category')
            except Category.DoesNotExist:
                return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            categories = Category.objects.all().order_by('category')
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if id is not None:
            try:
                category = Category.objects.get(id=id)
            except Category.DoesNotExist:
                return Response(f"Category with ID '{id}' doesn't exist.", status=status.HTTP_404_NOT_FOUND)

            if Document.objects.filter(category_id=id).exists():
                return Response(
                    {"message": f"Category '{category.category}' is in use and cannot be deleted."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category.delete()
            return Response(f"Category '{category.category}' Deleted.", status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "No id Provided in url"}, status=status.HTTP_404_NOT_FOUND)
