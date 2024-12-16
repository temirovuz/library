from django.urls import path

# from book.views import BookCreateListAPIView, BookDetailAPIView, GenreCreateListAPIView, GenreBooksListAPIView, \
#     AuthorCreateListAPIVew, AuthorBooksListAPIView, BasketCreateListAPIView, RentalCreateListAPIView, \
#     RentalUpdateAPIView, SearchAPIView

from book.views import BookCreateListAPIView, BookDetailAPIView, GenreCreateListAPIView, GenreBooksListAPIView, \
    AuthorCreateListAPIVew, AuthorBooksListAPIView, BasketCreateListAPIView, RentalCreateListAPIView, \
    RentalUpdateAPIView, SearchAPIView, RentalListAPIView, RentalDetailAPIView

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
    path('bron/', RentalCreateListAPIView.as_view(), name='bron'),
    path('take-away/', RentalUpdateAPIView.as_view(), name='take-away'),
    path('rentals/', RentalListAPIView.as_view(), name='rentals'),
    path('rental/<int:pk>', RentalDetailAPIView.as_view(), name='rentals'),

    # search
    path('search/', SearchAPIView.as_view(), name='search')
]
