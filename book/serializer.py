from datetime import timedelta

from django.utils import timezone
from rest_framework.fields import IntegerField, DateTimeField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from book.models import Book, Genre, Author, Basket, Assessment, Rental, User


# -------------------------------------------------------------------------------------------------------------- #

class BookSerializer(ModelSerializer):
    author = PrimaryKeyRelatedField(queryset=Author.objects.all())
    genre = PrimaryKeyRelatedField(queryset=Genre.objects.all())

    class Meta:
        model = Book
        fields = ['id', 'name', 'description', 'author', 'genre', 'daily_price', 'available_copies', 'is_available']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.name
        representation['genre'] = instance.genre.name
        return representation


# -------------------------------------------------------------------------------------------------------------- #

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


# -------------------------------------------------------------------------------------------------------------- #

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


# -------------------------------------------------------------------------------------------------------------- #

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


# -------------------------------------------------------------------------------------------------------------- #

class AssessmentSerializer(ModelSerializer):
    book = SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ['user', 'book', 'rating', 'comment']
        read_only_fields = ['user']

    def get_book(self, obj):
        return {"book": obj.book.name}


class BookReviewsSerializer(ModelSerializer):
    book = PrimaryKeyRelatedField(queryset=Book.objects.all())
    all = SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ['book', 'rating', 'comment', 'all']

    def get_all(self, obj):
        alls = Assessment.objects.filter(book_id=obj)
        return AssessmentSerializer(alls, many=True).data

    def to_representation(self, instance):
        representation = uper().to_representation(instance)
        representation['book'] = instance.book.name


# -------------------------------------------------------------------------------------------------------------- #

class RentalSerializer(ModelSerializer):
    book = PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Rental
        fields = ['book', 'start_date', 'end_date', 'status', 'penalty']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['book'] = instance.book.name
        return representation


class RentalCreateSerializer(ModelSerializer):
    class Meta:
        model = Rental
        fields = ['book']

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise ValidationError("Foydalanuvchi autentifikatsiyadan o'tmagan")

        if Rental.calculate_user_debt(user) > 0:
            raise ValidationError("Sizda qarzdorlik bo'lgani uchun kitob bron qilolmaysiz.")

        if Rental.objects.filter(user=user, book=data['book']).exists():
            raise ValidationError(f"'{data['book'].name}' kitobi allaqachon sizda ijarada.")

        return data


class RentalUpdateSerializer(ModelSerializer):
    id = IntegerField(write_only=True)
    start_date = DateTimeField(read_only=True)
    end_date = IntegerField(write_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'start_date', 'end_date']

    def validate(self, data):
        id = data.get('id')
        if not Rental.objects.filter(id=id).exists():
            raise ValidationError({'rental_id': 'Bunday buyurtma mavjud emas'})

        end_date = data.get('end_date')
        if not isinstance(end_date, int) or end_date <= 0:
            raise ValidationError({'end_date': 'Tugash sanasi kamida 1 kun yoki 1 kundan kop bolishi kerak.'})

        return data

    def update(self, instance, validated_data):
        instance.start_date = timezone.now()
        days_to_add = validated_data.get('end_date')
        instance.end_date = instance.start_date + timedelta(days=days_to_add)
        instance.status = 'ijara'
        instance.save()
        return instance


class RentalListSerializer(ModelSerializer):
    book = PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Rental
        fields = ['book', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['book'] = instance.book.name
        return representation


class RentalDetailSerializer(ModelSerializer):
    book = PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Rental
        fields = ['book', 'start_date', 'end_date', "penalty", 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['book'] = instance.book.name
        return representation


# -------------------------------------------------------------------------------------------------------------- #

class SearchSerializer(ModelSerializer):
    author = AuthorSerializer()
    genre = GenreSerializer()

    class Meta:
        model = Book
        fields = ['name', 'author', 'genre', 'available_copies']
