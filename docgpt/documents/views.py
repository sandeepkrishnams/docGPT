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
from documents.utils import create_renamed, get_file_hash, get_content, add_content_to_solr, search_solr_content
from documents.document_serializer import DocumentListSerializer, DocumentUploadSerializer


media_url = settings.MEDIA_URL

# TODO :create readme.md


class DocumentManager(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request, id=None):
        """
        Filter or Search
        Filter the Documents by catedory id
        Search a string in the user document contents also filter the search results by category and a date range

        Query params 
        c : category of the documents needed to filter
        s : string to be seached in the documents contents 
        sc : search result filtering by category id 
        st : search result filtering by type of the file 
        ssd : search result filtering start date
        sed : search result filtering end date 
        """
        query_params = request.query_params
        is_superuser = request.user.is_superuser
        id = request.user.id
        query_dict = {}
        response = None

        page = query_params.get('page')
        start = 0
        if page:
            try:
                start = max(int(page) - 1, 0)
            except ValueError:
                start = 0
        # To filter the search results
        filter_queries = []
        solr_response_key_list = ['id', 'type', 'date']
        solr_params = {'q.op': 'AND', 'rows': settings.SOLR_PAGINATION_ROWS,
                       'start': start}
        user_id = query_params.get('uid')
        category = query_params.get('c')
        search_string = query_params.get('s')
        search_filter_category = query_params.get('sc')
        search_filter_type = query_params.get('st')
        search_filter_startdate = query_params.get('ssd')
        search_filter_enddate = query_params.get('sed')

        if is_superuser:
            # if the user is a superuser then
            # show all the users document details or superuser specified user id(uid) else show only the request users documents
            solr_response_key_list.append('user_id')
            # show all or the user_id provided by superuser
            query_dict['user_id'] = user_id if user_id else '*'
        else:
            query_dict['user_id'] = id

        if category:
            query_dict['category_id'] = category
        if search_string:
            query_dict['content'] = search_string
            solr_response_key_list.append('category_id')

            # if a search filter category present and that to solr filterlist
            if search_filter_category:
                filter_queries.append(f'category_id:{search_filter_category}')

            # if a search filter type present and that to solr filterlist
            if search_filter_type:
                filter_queries.append(f'type:{search_filter_type}')

            # filter search based both start and end date
            if search_filter_startdate or search_filter_enddate:
                if search_filter_startdate:
                    search_filter_startdate = search_filter_startdate+'T00:00:00Z'
                else:
                    search_filter_startdate = '*'

                if search_filter_enddate:
                    search_filter_enddate = search_filter_enddate+'T24:00:00Z'
                else:
                    search_filter_enddate = 'NOW'
                # create the query which is accepted by the solr db ex:[2023-09-12T00:00:00Z TO 2023-09-12T24:00:00Z]
                query = f'[{search_filter_startdate} TO {search_filter_enddate}]'
                filter_queries.append(f'date:{query}')
        response = search_solr_content(
            query_dict, solr_params, solr_response_key_list, filter_query=filter_queries)
        return Response(response, status=status.HTTP_200_OK)

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
                renamed_document = existing_document.upload
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
            document_content = get_content(file_url)

            if response:
                data = {
                    'user_id': response.user_id,
                    'id': response.id,
                    'type': response.upload.name.split('.')[-1],
                    'name': response.upload.name,
                    'content': document_content,
                    'date': response.created_at.isoformat(),
                    'category_id': response.category_id,
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
