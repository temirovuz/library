from django.urls import path

from book.views import BookCreateListAPIView, BookDetailAPIView

urlpatterns = [
    path('books/', BookCreateListAPIView.as_view(), name='books'),
    path('book/<int:pk>', BookDetailAPIView.as_view(), name='book'),
]
