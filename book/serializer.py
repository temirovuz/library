from rest_framework.serializers import ModelSerializer

from book.models import Book


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ['name', 'description', 'author', 'genre_id', 'daily_price', 'available_copies', 'is_available']
