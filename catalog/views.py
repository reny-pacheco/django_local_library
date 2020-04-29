from django.shortcuts import render
import datetime
from django.views import generic
from catalog.models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genre = Genre.objects.all().count()
    book_genre_horror = Book.objects.filter(genre__name='Horror').count()
    book_genre_scifi = Book.objects.filter(genre__name='Science Fiction').count()
    book_genre_comedy = Book.objects.filter(genre__name='Comedy').count()
    book_genre_action = Book.objects.filter(genre__name='Action').count()
    book_genre_lifestyle = Book.objects.filter(genre__name='Lifestyle').count()
    book_genre_drama = Book.objects.filter(genre__name='Drama').count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre' : num_genre,
        'book_genre_horror' : book_genre_horror,
        'book_genre_scifi' : book_genre_scifi,
        'book_genre_action' : book_genre_action,
        'book_genre_comedy' : book_genre_comedy,
        'book_genre_lifestyle' : book_genre_lifestyle,
        'book_genre_drama' : book_genre_drama,
    }

    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 3
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class BorrowedBooksByUserListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/borrowed_books_by_users.html'
    paginate_by = 5
    permission_required = 'catalog.can_mark_returned'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


# I did not include this view in the template
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk,):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)


    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    context = {
        'form': form,
        'book_instance': book_instance,
    }



    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin,CreateView):
    model = Author
    fields = '__all__'
    # initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = "__all__"
    permission_required = 'catalog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = "__all__"
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'