import re
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import now


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User')
    ]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=13, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    first_name = None
    last_name = None
    username = None

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"Email: {self.email}\nRole: {self.role}"


# ---------------------------------------------  Genre ------------------------------------------------------- #
class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cleaned_name = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def save(self, *args, **kwargs):
        self.cleaned_name = re.sub(r"[^a-zA-Z0-9\s]", "", self.name).lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---------------------------------------------  Author ------------------------------------------------------- #
class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cleaned_name = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def save(self, *args, **kwargs):
        self.cleaned_name = re.sub(r"[^a-zA-Z0-9\s]", "", self.name).lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---------------------------------------------  Book ------------------------------------------------------- #
class Book(models.Model):
    name = models.CharField(max_length=255)
    cleaned_name = models.CharField(max_length=255,  blank=True)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_copies = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.cleaned_name = re.sub(r"[^a-zA-Z0-9\s]", "", self.name).lower().strip()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.name


# ---------------------------------------------  Basket ------------------------------------------------------- #
class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Basket'
        verbose_name_plural = 'Baskets'

    def __str__(self):
        return f"User - {self.user.email} Book - {self.book.name}"


# ---------------------------------------------  Rental ------------------------------------------------------- #
class Rental(models.Model):
    STATUS_CHOICE = [
        ('ijara', 'Ijara'),
        ('qaytarilgan', 'Qaytarilgan'),
        ('bron', 'Bron qilingan'),
        ('bekor', 'Bekor qilingan'),

    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    penalty = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=155, choices=STATUS_CHOICE, default='bron')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rental'
        verbose_name_plural = 'Rentals'

    def calculate_penalty(self):
        if now().date() > self.end_date:
            overdue_days = (now().date() - self.end_date).days
            daily_penalty = self.book.daily_price * 0.01
            self.penalty += daily_penalty * overdue_days
            self.save()

    def cancel_bron(self):
        if self.status == 'bron' and timezone.now() > self.created_at + timedelta(days=1):
            self.status = 'bekor'
            self.book.available_copies += 1
            self.book.save()
            self.save()

    @staticmethod
    def calculate_user_debt(user):
        debt = Rental.objects.filter(user=user, status='ijara').aggregate(total_penalty=Sum('penalty'))['total_penalty']
        return debt or 0

    def __str__(self):
        return f"User - {self.user.email} Book - {self.book.name} Status - {self.status}"


# ---------------------------------------------  Assessment ------------------------------------------------------- #
class Assessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.CharField(max_length=2, choices=[(i, str(i)) for i in range(1, 6)], blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Assessment'
        verbose_name_plural = "Assessments"

    def __str__(self):
        return f"{self.user.email} Book - {self.book.name} Rating - {self.rating}"
