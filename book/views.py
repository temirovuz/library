from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from book.models import Book, Genre, Author, Basket, Assessment, Rental
from book.permissions import IsAmin
from book.serializer import BookSerializer, GenreSerializer, GenreBookSerializer, AuthorSerializer, \
    AuthorBookSerializer, BasketSerializer, AssessmentSerializer, RentalSerializer, RentalCreateSerializer, \
    RentalUpdateSerializer


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


class RentalCreateListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                "error": "Foydalanuvchi autentifikatsiyadan o'tmagan"
            }, status=status.HTTP_401_UNAUTHORIZED)

        rentals = Rental.objects.filter(user=request.user).all()
        serializer = RentalSerializer(rentals, many=True)
        return Response({"books": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "error": "Foydalanuvchi autentifikatsiyadan o'tmagan"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Basketdagi barcha kitoblarni olish
        basket_items = Basket.objects.filter(user=user).all()
        if not basket_items.exists():
            return Response({
                "error": "Savat bo'sh."
            }, status=status.HTTP_400_BAD_REQUEST)

        rentals = []
        for item in basket_items:
            serializer = RentalCreateSerializer(data={"book": item.book.id}, context={"request": request})
            serializer.is_valid(raise_exception=True)
            rental = serializer.save(user=user)
            rentals.append(rental)

        # Savatni tozalash
        basket_items.delete()

        response_serializer = RentalSerializer(rentals, many=True)
        return Response({"message": "Savatdagi kitoblar bron qilindi.", "rentals": response_serializer.data},
                        status=status.HTTP_201_CREATED)


class RentalUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RentalUpdateSerializer(data=request.data)

        if serializer.is_valid():
            rental_id = serializer.validated_data.get('rental_id')
            try:
                # Rental obyektini olish
                rental = Rental.objects.get(id=rental_id)

                # Ma'lumotlarni yangilash
                serializer.update(rental, serializer.validated_data)

                return Response({
                    'message': 'Rental updated successfully.',
                    'data': {
                        'rental_id': rental.id,
                        'start_date': rental.start_date,
                        'end_date': rental.end_date,
                        'status': rental.status,
                    }
                }, status=status.HTTP_200_OK)

            except Rental.DoesNotExist:
                return Response({'error': 'Rental not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
