from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from book.models import Book, Genre
from book.permissions import IsAmin
from book.serializer import BookSerializer, GenreSerializer, GenreBookSerializer


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
