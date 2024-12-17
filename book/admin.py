from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from book.models import User, Book, Author, Genre, Basket, Rental


@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'full_name', 'phone_number', 'role')
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name", 'phone_number', 'role')}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ['id','name', 'cleaned_name']
    search_fields = ['name', 'cleaned_name']
    search_help_text = "Nom bo'yicha qidirish"


@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ['id','name', 'cleaned_name']
    search_fields = ['name', 'cleaned_name']
    search_help_text = "Nom bo'yicha qidirish"


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ['id','name','cleaned_name', 'author', 'genre_id', 'daily_price', 'available_copies', 'is_available']
    search_fields = ['name', 'cleaned_name', 'author', 'genre_id']
    search_help_text = "Nom, author, genre bo'yicha qidirish"


@admin.register(Basket)
class BasketAdmin(ModelAdmin):
    list_display = ['id','user_id', 'book_id']


@admin.register(Rental)
class RentalAdmin(ModelAdmin):
    list_display = ['id','user', 'book', 'start_date', 'end_date', 'penalty', 'status']
    search_fields = ['status']
    search_help_text = "Status bo'yicha qidirish"
