from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from book.models import Book, Genre, Author, Basket, Assessment, Rental
from book.permissions import IsAmin
from book.serializer import BookSerializer, GenreSerializer, GenreBookSerializer, AuthorSerializer, \
    AuthorBookSerializer, BasketSerializer, AssessmentSerializer


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


class BasketCreateListAPIView(ListCreateAPIView):
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Basket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookAssessmentAPIView(CreateAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        rentals = Rental.objects.filter(user=self.request.user, status='ijara')

        if not rentals.exists():
            return Response({'error': 'Ijarada olingan kitoblar mavjud emas.'}, status=status.HTTP_400_BAD_REQUEST)

        book_id = self.request.data.get('book')
        if not book_id:
            return Response({"error": "Siz kitobni tanlashangiz kerak"})

        try:
            rental = rentals.get(book_id=book_id)
            book = rental.book
        except Rental.DoesNotExist:
            return Response({'error': 'This book is not rented by the user or does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        rating = self.request.data.get('rating')
        comment = self.request.data.get('comment')
        serializer.save(user=self.request.user, book=book, rating=rating, comment=comment)

        rental.status = 'qaytarilgan'
        rental.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data({
            "message": "Baholash muvafaqiyatli yaratildi.",
            "data": response.data
        })
        return response
