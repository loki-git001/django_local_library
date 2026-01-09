from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("books/", views.BookListView.as_view(), name="books"),
    path("books/<int:pk>", views.BookDetailView.as_view(), name="book-detail"),
    path("authors/", views.AuthorListview.as_view(), name="authors"),
    path("author/<int:pk>", views.AuthorDetailView.as_view(), name="author-detail"),
]

# User configured URLs

urlpatterns += [
    path("mybooks/", views.LoanedBooksByUserListView.as_view(), name="my-borrowed"),
    path("borrowed/", views.LoanedBookAllListView.as_view(), name="all-borrowed"),
]
