try:
    from urllib import quote_plus #python 2
except:
    pass

try:
    from urllib.parse import quote_plus #python 3
except:
    pass

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import PostForm
from .models import Post

def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    paginator = Paginator(queryset_list, 5) # Show N contacts per page

    page_request_var = "page"
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        "title": "List",
        "object_list": queryset,
        "page_request_var": page_request_var,
        "today": today,
    }
    return render(request, 'post_list.html', context)

def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff and not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)
    context = {
        "title": "Detail",
        "instance": instance,
        "share_string": share_string,
    }
    return render(request, 'post_detail.html', context)

def post_create(request):
    if not request.user.is_staff and not request.user.is_superuser:
        raise Http404

    # if not request.user.is_authenticated:
    #     raise Http404

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, 'Successfully created.')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form,
    }
    return render(request, 'post_form.html', context)

def post_update(request, slug=None):
    if not request.user.is_staff and not request.user.is_superuser:
        raise Http404

    instance = get_object_or_404(Post,slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, 'Post details updated.')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, 'post_form.html', context)

def post_delete(request, slug=None):
    if not request.user.is_staff and not request.user.is_superuser:
        raise Http404

    instance = get_object_or_404(Post,slug=slug)
    instance.delete()
    messages.success(request, 'Successfully deleted.')
    return redirect("posts:list")
