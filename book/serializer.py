from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField

from book.models import Book, Genre


class BookSerializer(ModelSerializer):
    author = StringRelatedField()
    genre_id = StringRelatedField()
    class Meta:
        model = Book
        fields = ['name', 'description', 'author', 'genre_id', 'daily_price', 'available_copies', 'is_available']


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
