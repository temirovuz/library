from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from book.models import Book, Genre, Author
from book.permissions import IsAmin
from book.serializer import BookSerializer, GenreSerializer, GenreBookSerializer, AuthorSerializer, AuthorBookSerializer


class BookCreateListAPIView(ListCreateAPIView):
    queryset = Book.objects.all()
    permission_classes = [IsAuthenticated, IsAmin]
    serializer_class = BookSerializer


class BookDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    permission_classes = [IsAuthenticated, IsAmin]
    serializer_class = BookSerializer


class GenreCreateListAPIView(ListCreateAPIView):
    queryset = Genre.objects.all()
    permission_classes = [IsAuthenticated, IsAmin]
    serializer_class = GenreSerializer


class GenreBooksListAPIView(RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreBookSerializer
    permission_classes = [IsAuthenticated]


class AuthorCreateListAPIVew(ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsAmin]


class AuthorBooksListAPIView(RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorBookSerializer
    permission_classes = [IsAuthenticated]
