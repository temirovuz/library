from django.urls import path

from book.views import BookCreateListAPIView, BookDetailAPIView, GenreCreateListAPIView, GenreBooksListAPIView, \
    AuthorCreateListAPIVew, AuthorBooksListAPIView


urlpatterns = [
    path('books/', BookCreateListAPIView.as_view(), name='books'),
    path('book/<int:pk>', BookDetailAPIView.as_view(), name='book'),
    path('genre/', GenreCreateListAPIView.as_view(), name='genre'),
    path('genre/<int:pk>', GenreBooksListAPIView.as_view(), name='genre-books'),
    path('author/', AuthorCreateListAPIVew.as_view(), name='author'),
    path('author/<int:pk>', AuthorBooksListAPIView.as_view(), name='author-books'),
]
