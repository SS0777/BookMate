from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('categories/', views.category_list, name='category_list'),
    path('<int:id>/<slug:slug>/', views.book_detail, name='book_detail'),
    path('category/<slug:category_slug>/', views.book_list, name='book_list_by_category'),
    path('search/', views.search_results, name='search_results'),
    path('book/<str:book_id>/', views.api_book_detail, name='api_book_detail'),
    path('recommendations/', views.recommendations, name='recommendations'),
]
