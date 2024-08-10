from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Subscription, Tag, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


def home(request):
    public_posts = Post.objects.filter(is_private=False).order_by('-created_at')
    subscription_posts = get_subscription_posts(request.user) if request.user.is_authenticated else []

    context = {
        'posts': public_posts,
        'subscription_posts': subscription_posts
    }
    return render(request, 'blog/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'blog/registration/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    subscriptions = Subscription.objects.filter(subscriber=user)

    context = {
        'user': user,
        'subscriptions': subscriptions,
    }
    return render(request, 'blog/account/profile.html', context)


@login_required
def create_post(request):
  if request.method == 'POST':
      form = PostForm(request.POST)
      if form.is_valid():
          post = form.save(commit=False)
          post.author = request.user
          post.save()
          selected_tags = request.POST.getlist('tags')
          for tag_name in selected_tags:
              tag, created = Tag.objects.get_or_create(name=tag_name)
              post.tags.add(tag)
          return redirect('home')
  else:
      form = PostForm()
  return render(request, 'blog/create_post.html', {'form': form})

@login_required
def post_detail(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  comments = Comment.objects.filter(post=post)

  if request.method == 'POST':
      form = CommentForm(request.POST)
      if form.is_valid():
          comment = form.save(commit=False)
          comment.post = post
          comment.author = request.user
          comment.save()
          return redirect('post_detail', post_id=post.id)
  else:
      form = CommentForm()

  context = {
      'post': post,
      'comments': comments,
      'form': form
  }
  return render(request, 'blog/post_detail.html', context)


def get_subscription_posts(user):
    subscriptions = Subscription.objects.filter(subscriber=user)
    posts = Post.objects.filter(author__in=[sub.subscribed_to for sub in subscriptions])
    return posts


@login_required
def subscribe(request, user_id):
  subscribed_to = get_object_or_404(User, pk=user_id)
  if request.user != subscribed_to:
      Subscription.objects.create(subscriber=request.user, subscribed_to=subscribed_to)
  return redirect('user_profile', username=subscribed_to.username)


@login_required
def view_private_post(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  if post.is_private:
      if post.author == request.user or request.user in post.author.subscriptions.all():
          return render(request, 'blog/post_detail.html', {'post': post})
      else:
          return render(request, 'blog/access_denied.html')
  else:
      return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def edit_post(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  if request.user == post.author:
      if request.method == 'POST':
          form = PostForm(request.POST, instance=post)
          if form.is_valid():
              form.save()
              return redirect('post_detail', post_id=post.id)
      else:
          form = PostForm(instance=post)
      return render(request, 'blog/edit_post.html', {'form': form})
  else:
      return render(request, 'blog/access_denied.html')


@login_required
def delete_post(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  if request.user == post.author:
      if request.method == 'POST':
          post.delete()
          return redirect('home')
      return render(request, 'blog/delete_post.html', {'post': post})
  else:
      return render(request, 'blog/access_denied.html')


def post_list(request):
    tags = Tag.objects.all()
    selected_tags = request.GET.getlist('tag')

    if selected_tags:
        posts = Post.objects.filter(tags__name__in=selected_tags).distinct()
    else:
        posts = Post.objects.all()

    context = {
        'posts': posts,
        'tags': tags,
        'selected_tags': selected_tags
    }
    return render(request, 'blog/post_list.html', context)


@login_required
def add_comment(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  if request.method == 'POST':
      form = CommentForm(request.POST)
      if form.is_valid():
          comment = form.save(commit=False)
          comment.post = post
          comment.author = request.user
          comment.save()
          return redirect('post_detail', post_id=post.id)
  else:
      form = CommentForm()
  return render(request, 'blog/add_comment.html', {'form': form, 'post': post})