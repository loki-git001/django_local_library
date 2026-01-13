"""Models for  Local library"""

import uuid
from django.db import models
from django.urls import reverse
from django.db.models.functions import Lower
from django.conf import settings
from datetime import date


class Genre(models.Model):
    """Model representing a book genre"""

    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre (e.g. Science fiction, fantasy, French poetry etc.)",
    )

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self):
        """Returns the URL to access a particular genre instance"""
        return reverse("genre-detail", args=[str(self.pk)])

    class Meta:
        """Perform validations for valid genre name"""

        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="genre_name_case_insensitive_unique",
                violation_error_message="Genre already exists (case-insensitive match)",
            )
        ]


class Book(models.Model):
    """Model representing a book (Not a specific copy of book)"""

    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        "Author", on_delete=models.RESTRICT, null=True, blank=True
    )
    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
    )
    genre = models.ManyToManyField("Genre", help_text="Select the genre of this book")
    language = models.ForeignKey("Language", on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return str(self.title)

    def get_absolute_url(self):
        """Returns the URL access to a detail record for this boook"""

        return reverse("book-detail", args=[str(self.pk)])

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ", ".join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = "Genre"


class BookInstance(models.Model):
    """Model representing a specific copy of a book"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library",
    )
    book = models.ForeignKey(Book, on_delete=models.RESTRICT)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ("m", "Maintenance "),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )

    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def is_overdue(self):
        """Verify whether due_back is empty and compare it with today's date"""
        return bool(self.due_back and date.today() > self.due_back)

    class Meta:
        ordering = ["-due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self) -> str:
        return f"{self.id} ({self.book.title})"


class Author(models.Model):
    """Model representing an author"""

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(
        null=True, blank=True, help_text="The date should be of format YYYY-MM-DD"
    )
    date_of_death = models.DateField(
        "Died",
        null=True,
        blank=True,
        help_text="The date should be of format YYYY-MM-DD",
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance"""
        return reverse("author-detail", args=[str(self.pk)])

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name}"


class Language(models.Model):
    """Model representing a language"""

    name = models.CharField(
        max_length=200,
        help_text="Enter the book's natural language (e.g. English, Malayalam, French)",
    )

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self):
        """Returns the URL to access a particular language instance"""
        return reverse("language-detail", args=[str(self.pk)])

    class Meta:
        """Perform validations for valid language name"""

        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="language_name_insesitive_unique",
                violation_error_message="Genre already exists (case-insensitive match)",
            )
        ]
