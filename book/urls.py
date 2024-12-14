from django.urls import path

from book.views import BookCreateListAPIView, BookDetailAPIView, GenreCreateListAPIView, GenreBooksListAPIView, \
    AuthorCreateListAPIVew, AuthorBooksListAPIView, BasketCreateListAPIView, RentalCreateListAPIViews, RentalPickupView

urlpatterns = [
    # Books
    path('books/', BookCreateListAPIView.as_view(), name='books'),
    path('book/<int:pk>', BookDetailAPIView.as_view(), name='book'),

    # genre
    path('genre/', GenreCreateListAPIView.as_view(), name='genre'),
    path('genre/<int:pk>', GenreBooksListAPIView.as_view(), name='genre-books'),

    # author
    path('author/', AuthorCreateListAPIVew.as_view(), name='author'),
    path('author/<int:pk>', AuthorBooksListAPIView.as_view(), name='author-books'),

    # basket
    path('basket/', BasketCreateListAPIView.as_view(), name='basket'),

    # rental
    path('bron/', RentalCreateListAPIViews.as_view(), name='born'),
    path('pickup/', RentalPickupView.as_view(), name='pickup')
]
