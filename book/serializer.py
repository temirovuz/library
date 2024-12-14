from datetime import timedelta

from django.utils.timezone import now
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from book.models import Book, Genre, Author, Basket, Assessment, Rental, User


class BookSerializer(ModelSerializer):
    author = PrimaryKeyRelatedField(queryset=Author.objects.all())
    genre = PrimaryKeyRelatedField(queryset=Genre.objects.all())

    class Meta:
        model = Book
        fields = ['name', 'description', 'author', 'genre', 'daily_price', 'available_copies', 'is_available']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.name
        representation['genre'] = instance.genre.name
        return representation


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class GenreBookSerializer(ModelSerializer):
    books = SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['name', 'books']

    def get_books(self, obj):
        books = Book.objects.filter(genre_id=obj)
        return BookSerializer(books, many=True).data


class AuthorSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']


class AuthorBookSerializer(ModelSerializer):
    books = SerializerMethodField()

    class Meta:
        model = Author
        fields = ['name', 'books']

    def get_books(self, obj):
        books = Book.objects.filter(author_id=obj)
        return BookSerializer(books, many=True).data


class BasketSerializer(ModelSerializer):
    class Meta:
        model = Basket
        fields = ['user', 'book']
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        book = data['book']
        if Basket.objects.filter(user=user, book=book).exists():
            raise ValidationError("Siz bu kitobni allaqachon savatchaga qo'shgansiz.")

        return data


class AssessmentSerializer(ModelSerializer):
    book = SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ['user', 'book', 'rating', 'comment']
        read_only_fields = ['user']

    def get_book(self, obj):
        return {"book": obj.book.name}


class RentalSerializer(ModelSerializer):
    class Meta:
        model = Rental
        fields = ['user', 'book']
        read_only_fields = ['user', 'book']

    def validate(self, data):
        user = self.context['request'].user
        book = data.get('book')
        if not book:
            raise ValidationError({"book": "Kitob ma'lumotlarini kiritish majburiy."})

        # Check if the user already rented or reserved this book
        if Rental.objects.filter(user=user, book=book, status__in=['bron', 'ijarada']).exists():
            raise ValidationError("Siz ushbu kitobni allaqachon bron qilgansiz yoki ijaraga olgansiz.")

        # Check if the user has debt
        if Rental.calculate_user_debt(user) > 0:
            raise ValidationError("Sizda qarzdorlik bo'lgani uchun kitob bron qilolmaysiz yoki olib ketolmaysiz.")

        # Check if there are available copies of the book
        if book.available_copies <= 0:
            raise ValidationError("Kitobning mavjud nusxalari qolmagan.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        book = validated_data['book']

        # Update book's available copies
        book.available_copies -= 1
        book.save()

        # Set additional fields
        validated_data['user'] = user
        validated_data['status'] = 'bron'
        return super().create(validated_data)


class RentalPickupSerializer(ModelSerializer):
    class Meta:
        model = Rental
        fields = ['id', 'status']

    def update(self, instance, validated_data):
        if Rental.calculate_user_debt(instance.user) > 0:
            return ValidationError("Sizda qarzdorlik bolgani uchun kitob bron qila olmaysiz")

        if instance.status != 'bron':
            return ValidationError("Bu kitob bron qilinmagan")

        instance.start_date = now()
        rental_days = self.context['request'].data.get('rental_days')
        if not rental_days or int(rental_days) <= 0:
            raise ValidationError("Iltimos, to'g'ri ijaraga olish muddatini kiriting.")

        rental_days = int(rental_days)
        instance.end_date = instance.start_date + timedelta(days=rental_days)

        instance.status = 'ijara'
        instance.save()
        return instance
