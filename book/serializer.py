from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from book.models import Book, Genre, Author, Basket, Assessment


class BookSerializer(ModelSerializer):
    author = SerializerMethodField()
    genre = SerializerMethodField()

    class Meta:
        model = Book
        fields = ['name', 'description', 'author', 'genre', 'daily_price', 'available_copies', 'is_available']

    def get_author(self, obj):
        return obj.author.name

    def get_genre(self, obj):
        return obj.genre.name


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
