from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.models import User
from .models import Post
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.

def home(request):
    posts=Post.objects.order_by('-date_posted')
    context={"posts":posts.all()[:5]}
    return render(request,'blog/trial.html',context)

class PostListView(LoginRequiredMixin,ListView):
    model=Post
    template_name='blog/home.html'
    context_object_name='posts'
    ordering=['-date_posted']
    paginate_by=5

class UserPostListView(LoginRequiredMixin,ListView):
    model=Post
    template_name='blog/user_posts.html'
    context_object_name='posts'
    paginate_by=5

    def get_queryset(self):
        user=get_object_or_404(User,username=self.kwargs.get('username'))

        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
    model=Post
    
class PostCreateView(LoginRequiredMixin,CreateView):
    model=Post
    fields=['title','content']

    def form_valid(self,form):
        form.instance.author=self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=Post
    fields=['title','content']

    def form_valid(self,form):
        form.instance.author=self.request.user
        return super().form_valid(form)

    def test_func(self):
        post=self.get_object()
        if self.request.user==post.author:
            return True
        return False
class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Post
    success_url = '/'


    def test_func(self):
        post=self.get_object()
        if self.request.user==post.author:
            return True
        return False
# class ProfileList(ListView):
#     template_name = 'blog/home.html'
#     model = Post
#     paginate_by=5

#     def get_queryset(self):
#         query = self.request.GET('query')
#         if query:
#             object_list = self.model.objects.filter(title__icontains=query)
#         else:
#             object_list = self.model.objects.none()
#         return object_list.order_by('-date_posted')

@login_required
def about(request):
    return render(request,'blog/about.html',{"title":"About"})

@login_required
def search(request):
    query=request.GET['query']
    if len(query)>100:
        posts=Post.objects.none()
    else:
        posts= Post.objects.filter(title__icontains=query).order_by("-date_posted")
    if posts.count()==0:
        messages.warning(request, "No search results found. Please enter new query.")
    paginate=Paginator(posts,5)
    page_number=request.GET.get('page')
    page_obj=paginate.get_page(page_number)
    context={'posts': posts,'query': query,"page_obj":page_obj}

    return render(request, 'blog/search.html',context)
    
   