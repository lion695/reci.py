from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, ProfileForm
from .models import Comment


def index(request):
    """View for the home page"""

    comments = Comment.objects.select_related("author")
    comment_form = CommentForm() if request.user.is_authenticated else None

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("account_login")
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "Comment added.",
            )
            return redirect("index")

    return render(
        request,
        "core/index.html",
        {
            "comments": comments,
            "comment_form": comment_form,
        }
    )


@login_required
def profile(request):
    """View for the profile page"""

    if request.method == "POST":
        form = ProfileForm(data=request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            messages.add_message(
                request, messages.SUCCESS,
                f'Email address changed to {request.user.email}'
            )

    else:
        form = ProfileForm(initial={"email": request.user.email})

    return render(
        request,
        "core/profile.html",
        {
            "form": form,
        }
    )


@login_required
def edit_comment(request, comment_id):
    """Allow a user to edit their own comment."""
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden("You can only edit your own comments.")

    if request.method == "POST":
        form = CommentForm(data=request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Comment updated.")
            return redirect("index")
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "core/edit_comment.html",
        {
            "form": form,
            "comment": comment,
        }
    )


@login_required
def delete_comment(request, comment_id):
    """Allow a user to delete their own comment."""
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden("You can only delete your own comments.")

    if request.method == "POST":
        comment.delete()
        messages.add_message(request, messages.SUCCESS, "Comment deleted.")
    return redirect("index")
