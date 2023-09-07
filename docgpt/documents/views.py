import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from docgpt.utils import get_paginated_response
from documents.models import Document
from documents.utils import create_renamed, get_file_hash, get_content, add_content_to_solr
from documents.document_serializer import DocumentListSerializer, DocumentUploadSerializer


media_url = settings.MEDIA_URL


class DocumentManager(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request, id=None):
        exclude_fields = []
        kwargs = {}
        if not request.user.is_superuser:
            id = request.user.id
            exclude_fields = ['username', 'id']
        query_params = request.query_params

        search_params = query_params.get('search')
        filter_params = query_params.get('filter')

        if id:
            filtered_documents = Document.objects.filter(user=id)
        else:
            filtered_documents = Document.objects.all()

        if search_params:
            kwargs['name__icontains'] = search_params
        if filter_params:
            kwargs['category_id'] = filter_params

        filtered_data = filtered_documents.filter(**kwargs)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(filtered_data, request)

        serializer = DocumentListSerializer(
            paginated_data, many=True, exclude_fields=exclude_fields)
        if not serializer.data:
            return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

        paginated_response = get_paginated_response(
            paginator, data=serializer.data)

        return Response(paginated_response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            document = request.FILES['upload']
        except KeyError:
            return Response('Upload file not provided.', status=status.HTTP_400_BAD_REQUEST)

        renamed_document = create_renamed(document)
        file_hash = get_file_hash(renamed_document)

        existing_documents = Document.objects.filter(file_hash=file_hash)

        for existing_document in existing_documents:
            if existing_document.user == request.user:
                return Response('Document is already uploaded', status=status.HTTP_400_BAD_REQUEST)

        serializer_data = {
            'user': request.user.id,
            'name': document.name,
            'type': renamed_document.content_type,
            'category': request.data['category'],
            'file_hash': file_hash,
        }

        if not existing_documents.exists():
            serializer_data['upload'] = renamed_document
        else:
            existing_document = existing_documents.first()
            if existing_document:
                serializer_data['upload'] = existing_document.upload
        serializer = DocumentUploadSerializer(
            data=serializer_data)  # type: ignore

        if serializer.is_valid():
            response = serializer.save()

            file_relative_path = str(renamed_document)
            file_url = settings.MEDIA_URL + file_relative_path

            response_data = {
                'message': 'Document uploaded successfully.',
                'file_name': document.name,
                'file_type': document.content_type,
                'file_url': file_url,
            }

            document_content = get_content('docgpt/' + file_url)

            if response:
                data = {
                    'id': response.id,
                    'type': response.upload.name.split('.')[-1],
                    'name': response.upload.name,
                    'content': document_content,
                }
                solr_data = json.dumps(data)
                add_content_to_solr(data)

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None, format=None):
        try:
            query = {'id': id}
            if not request.user.is_superuser:
                query['user'] = request.user
            document = Document.objects.get(**query)
            existing_documents = Document.objects.filter(
                file_hash=document.file_hash)

            for existing_document in existing_documents:
                document_path = existing_document.upload.path
                if os.path.exists(document_path):
                    os.remove(document_path)
                existing_document.delete()

            return Response({'message': f"Document with ID '{id}' is deleted"}, status=status.HTTP_204_NO_CONTENT)

        except Document.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
