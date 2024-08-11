from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Subscription, Tag, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages


def home(request):
    public_posts = Post.objects.filter(is_private=False).order_by('-created_at')
    context = {
        'posts': public_posts,
        'user': request.user
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
    return render(request, 'blog/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Неверный логин или пароль')
        else:
            form.add_error(None, 'Форма не действительна')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})



@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    subscriptions = user.subscribers.all()
    context = {
        'user': user,
        'subscriptions': subscriptions,
    }
    return render(request, 'blog/profile.html', context)


@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            selected_tags = form.cleaned_data.get('tags')
            if selected_tags:
                print(selected_tags)
                post.tags.set(selected_tags)
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})


@login_required(login_url='login')
@login_required(login_url='login')
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    if post.is_private:
        if post.author == request.user or request.user in post.author.subscriptions.all():
            if request.method == 'POST':
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.post = post
                    comment.author = request.user
                    comment.save()
                    return redirect('post_detail', post_id=post.id)
            context = {
                'post': post,
                'comments': comments,
                'form': form
            }
            return render(request, 'blog/post_detail.html', context)
        else:
            return render(request, 'blog/access_denied.html')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'blog/post_detail.html', context)


def get_subscription_posts(user):
    subscriptions = Subscription.objects.filter(subscriber=user)
    if not subscriptions.exists():
        return Post.objects.none()
    posts = Post.objects.filter(author__in=[sub.subscribed_to for sub in subscriptions]).distinct()
    return posts


@login_required(login_url='login')
def subscription_list(request):
    posts = get_subscription_posts(request.user)
    return render(request, 'blog/subscription_list.html', {'posts': posts})

@login_required(login_url='login')
def unsubscribe(request, user_id):
    subscribed_to = get_object_or_404(User, pk=user_id)
    if request.user != subscribed_to:
        Subscription.objects.filter(subscriber=request.user, subscribed_to=subscribed_to).delete()
    return redirect('blog/profile.html', username=subscribed_to.username)


@login_required(login_url='login')
def subscribe(request, user_id):
    user_to_subscribe = get_object_or_404(User, id=user_id)
    if request.user.subscriptions.filter(subscribed_to=user_to_subscribe).exists():
        messages.warning(request, 'Вы уже подписаны на этого пользователя.')
    else:
        Subscription.objects.create(subscriber=request.user, subscribed_to=user_to_subscribe)
        messages.success(request, f'Вы подписались на {user_to_subscribe.username}.')
    return redirect('blog/profile.html', user_id=user_id)


@login_required(login_url='login')
def view_private_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.is_private:
        if post.author == request.user or request.user in post.author.subscriptions.all():
            comments = post.comments.all()
            form = CommentForm()
            context = {
                'post': post,
                'comments': comments,
                'form': form
            }
            return render(request, 'blog/post_detail.html', context)
        else:
            return render(request, 'blog/access_denied.html')
    comments = post.comment_set.all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'blog/post_detail.html', context)



@login_required(login_url='login')
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


@login_required(login_url='login')
def delete_post(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  if request.user == post.author:
      if request.method == 'POST':
          post.delete()
          return redirect('post_list')
      return render(request, 'blog/delete_post.html', {'post': post})
  else:
      return render(request, 'blog/access_denied.html')


@login_required(login_url='login')
def post_list(request):
    tags = Tag.objects.all()
    selected_tag = request.GET.get('tag')
    posts = Post.objects.none()
    if request.user.is_authenticated:
        subscription_posts = get_subscription_posts(request.user)
        print(f"Subscription posts count: {subscription_posts.count()}")
        if selected_tag:
            print(f"Filtering posts with tag id: {selected_tag}")
            posts = subscription_posts.filter(tags__id=int(selected_tag)).distinct()
            print(f"Filtered posts count: {posts.count()}")
        else:
            if subscription_posts.exists():
                subscription_posts = subscription_posts.distinct()
                posts = subscription_posts | Post.objects.filter(author=request.user).distinct() | Post.objects.filter(is_private=False).distinct()
            else:
                posts = Post.objects.filter(is_private=False).distinct()
    else:
        if selected_tag:
            posts = Post.objects.filter(tags__id=int(selected_tag), is_private=False).distinct()
        else:
            posts = Post.objects.filter(is_private=False).distinct()
    context = {
        'posts': posts,
        'tags': tags,
        'selected_tag': selected_tag,
    }
    return render(request, 'blog/post_list.html', context)

@login_required(login_url='login')
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post': post, 'form': form})