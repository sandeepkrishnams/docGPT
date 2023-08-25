from rest_framework import serializers


from documents.models import Document
from users.user_serializer import UserProfileSerializer


class DocumentListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Document
        fields = [
            'user',
            'username',
            'id',
            'name',
            'type',
            'category',
            'upload',
            'created_at',
            'updated_at'
        ]

    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop('exclude_fields', None)
        super().__init__(*args, **kwargs)

        if exclude_fields:
            for field_name in exclude_fields:
                self.fields.pop(field_name)


class DocumentUploadSerializer(serializers.ModelSerializer):
    upload = serializers.FileField(max_length=10000, allow_empty_file=False)

    class Meta:
        model = Document
        fields = [
            'user',
            'category',
            'upload',
            'name',
            'type',
            'file_hash'
        ]
        require_fields = fields

        def validate(self, data):
            if 'upload' not in data:
                raise serializers.ValidationError(
                    "Please provide a file using form-data with a  'upload' key.")

            return data
