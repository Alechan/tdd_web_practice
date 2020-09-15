from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

from lists.forms import ExistingListItemForm, ItemForm, NewListForm
from lists.models import List


User = get_user_model()


def home_page(request):
    return render(request, 'home.html', {"form": ItemForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form = ExistingListItemForm(data=request.POST, for_list=list_)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(request, 'list.html', {'list': list_, "form": form})


def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, "home.html", {"form": form})


def my_lists(request, email):
    user = User.objects.get(email=email)
    
    return render(request, 'my_lists.html', {"user": user})


def share_list(request, list_id):
    if request.method == 'POST':
        sharee_email = request.POST["sharee"]
        sharee = User.objects.get(email=sharee_email)
        list_ = List.objects.get(id=list_id)
        list_.shared_with.add(sharee)
        list_.save()
        return redirect(list_)
