from django.urls import path
from categories import views


urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category-list'),
    path('<int:id>', views.CategoryListView.as_view(), name='category-delete'),
]
