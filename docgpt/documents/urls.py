from django.urls import path
from documents import views


urlpatterns = [
    path('', views.DocumentManager.as_view(), name='doc_manager'),
    path('<int:id>', views.DocumentManager.as_view(), name='doc_manager'),
]
