from categories.models import Category
from categories.category_serializer import CategorySerializer, CategoryUpdateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from categories.permissions import SuperuserPermission
from documents.models import Document
from rest_framework.pagination import PageNumberPagination
from docgpt.utils import get_paginated_response


class CategoryListView(APIView):
    pagination_class = PageNumberPagination
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
        sort = request.query_params.get('sort')
        order = request.query_params.get('order')
        if order == 'asc':
            modified_order = ''
        else:
            modified_order = '-'
        print(f'{modified_order}{sort}')
        paginator = self.pagination_class()
        if id is not None:
            try:
                category = Category.objects.get(id=id).order_by('category')
            except Category.DoesNotExist:
                return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            if sort and order:
                categories = Category.objects.all().order_by(
                    f'{modified_order}{sort}')
            else:
                categories = Category.objects.all().order_by('-created_at')
            paginated_data = paginator.paginate_queryset(categories, request)
            serializer = CategorySerializer(paginated_data, many=True)
            paginated_response = get_paginated_response(
                paginator, data=serializer.data)
            return Response(paginated_response, status=status.HTTP_200_OK)

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
