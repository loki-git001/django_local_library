from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from .models import Book, Author, BookInstance, Genre, Language


def index(request):
    """View function for home page of site."""

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()

    num_authors = Author.objects.count()

    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, "index.html", context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListview(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author

class GenreDetailView(generic.DetailView):
    model = Genre


class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 10


class LanguageDetailView(generic.DetailView):
    model = Language


class LanguageListView(generic.ListView):
    model = Language
    paginate_by = 10


class BookInstanceListView(generic.ListView):
    model = BookInstance
    paginate_by = 10


class BookInstanceDetailView(generic.DetailView):
    model = BookInstance


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing the books on loan for current user"""

    model = BookInstance
    template_name = "catalog/bookistance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class LoanedBookAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing the books on loan for librarians with the user names"""

    model = BookInstance
    permission_required = "catalog.can_mark_returned"
    template_name = "catalog/bookinstance_list_borrowed_all.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return BookInstance.objects.filter(status__exact="o").order_by("due_back")


# Form handling views
import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from .forms import RenewBookForm


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""

    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Create a form instance and populate it with data from the request (binding):
    if request.method == "POST":
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            return HttpResponseRedirect(reverse("all-borrowed"))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_date_renewal = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_date_renewal})

    context = {"form": form, "book_instance": book_instance}

    return render(request, "catalog/book_renew_librarian.html", context=context)


from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

# Create, Update, Delete Author


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    permission_required = "catalog.add_author"


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = "__all__"
    permission_required = "catalog.change_author"


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    object: Author

    model = Author
    success_url = reverse_lazy("authors")
    permission_required = "catalog.delete_author"

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(str(self.success_url))
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )


# Create, Update, Delete Book

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.add_book"


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.change_book"


class BookDelete(PermissionRequiredMixin, DeleteView):
    object: Book

    model = Book
    success_url = reverse_lazy("books")
    permission_required = "catalog.delete_book"

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(str(self.success_url))
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )

# Create, Update, Delete Genre

class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields= ['name']      
    permission_required = 'catalog.create_genre'

class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.change_genre'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'catalog.delete_genre'



# Create, Update, Delete Language

class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.add_language'


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.change_language'


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy('languages')
    permission_required = 'catalog.delete_language'



# Create, Update, Delete BookInstance

class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.add_bookinstance'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    # fields = "__all__"
    fields = ['imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.change_bookinstance'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('bookinstances')
    permission_required = 'catalog.delete_bookinstance'


# @csrf_exempt
# def author_list(request):
#     """
#     List all authors, or create a new author.
#     """
#     if request.method == "GET":
#         authors = Author.objects.all()
#         serializer = AuthorSerializer(authors, many=True)
#         return JsonResponse(serializer.data, safe=False)

#     elif request.method == "POST":
#         data = JSONParser().parse(request)
#         serializer = AuthorSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)

#     return HttpResponse(status=400)

# @csrf_exempt
# def author_detail(request, pk):
#     """
#     Retrieve, update or delete a code author.
#     """
#     try:
#         author = Author.objects.get(pk=pk)
#     except Author.DoesNotExist:
#         return HttpResponse(status=404)

#     if request.method == "GET":
#         serializer = AuthorSerializer(author)
#         return JsonResponse(serializer.data)

#     elif request.method == "PUT":
#         data = JSONParser().parse(request)
#         serializer = AuthorSerializer(author, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)

#     elif request.method == "DELETE":
#         author.delete()
#         return HttpResponse(status=204)

#     return HttpResponse(status=400)



from .serializers import AuthorSerializer, GenreSerializer, LanguageSerializer
from rest_framework import generics, permissions

# Author API
class AuthorList(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AuthorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Genre API
class GenreList(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GenreDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Language API
class LanguageList(generics.ListCreateAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class LanguageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

