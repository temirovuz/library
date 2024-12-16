import re

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView, \
    ListAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.cache import cache
from django.db.models import Q

from book.models import Book, Genre, Author, Basket, Assessment, Rental
from book.permissions import IsAmin
from book.serializer import BookSerializer, GenreSerializer, GenreBookSerializer, AuthorSerializer, \
    AuthorBookSerializer, BasketSerializer, AssessmentSerializer, RentalSerializer, RentalCreateSerializer, \
    RentalUpdateSerializer, RentalListSerializer, RentalDetailSerializer,BookReviewsSerializer


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


class BookReviewsList(ListAPIView):
    queryset = Assessment.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookReviewsSerializer


# --------------------------------------------------------------------------------------------------------------- #
class RentalCreateListAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated, IsAmin]

    def post(self, request, *args, **kwargs):
        serializer = RentalUpdateSerializer(data=request.data)

        if serializer.is_valid():
            rental_id = serializer.validated_data.get('rental_id')
            try:
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


class RentalListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RentalListSerializer

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user, status__in=['bron', 'ijara'])


class RentalDetailAPIView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RentalDetailSerializer

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user, status__in=['bron', 'ijara'])

    def perform_destroy(self, instance):
        if instance.status == 'bron':
            instance.status = 'bekor'
            instance.book.available_copies += 1
            instance.book.save()
            instance.save()
            return Response({'detail': 'Bron bekor qilindi.'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Faqat bron qilingan kitobni o‘chirish mumkin.'}, status=status.HTTP_400_BAD_REQUEST)


def clean_query(query):
    query = query.replace("'", "")
    query = re.sub(r"[^a-zA-Z0-9\s]", "", query)
    return query.strip().lower()


class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def perform_search(self, query):
        cleaned_query = clean_query(query)
        cache_key = f"book_search_{cleaned_query}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        books = Book.objects.filter(
            Q(cleaned_name__icontains=cleaned_query) |
            Q(author__cleaned_name__icontains=cleaned_query) |
            Q(genre__cleaned_name__icontains=cleaned_query)
        )
        serializer = BookSerializer(books, many=True)
        cache.set(cache_key, serializer.data, timeout=300)
        return serializer.data

    def get(self, request):
        query = request.query_params.get("search", None)
        if not query:
            return Response({"error": "Biror nom kiriting"}, status=status.HTTP_400_BAD_REQUEST)

        result = self.perform_search(query)
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        query = request.data.get("search", None)
        if not query:
            return Response({"error": "Biror nom kiriting"}, status=status.HTTP_400_BAD_REQUEST)

        result = self.perform_search(query)
        return Response(result, status=status.HTTP_200_OK)
