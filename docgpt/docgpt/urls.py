from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('user/', include('users.urls'), name='user-main'),
    path('documents/', include('documents.urls')),
    path('categories/', include('categories.urls')),
    path('interactions/', include('interactions.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
