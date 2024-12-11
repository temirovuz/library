from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from book.models import Book
from book.permissions import IsAmin
from book.serializer import BookSerializer


class BookCreateListAPIView(ListCreateAPIView):
    queryset = Book.objects.all()
    permission_classes = [IsAuthenticated, IsAmin]
    serializer_class = BookSerializer


class BookDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    permission_classes = [IsAuthenticated, IsAmin]
    serializer_class = BookSerializer
