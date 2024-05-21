from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from homepage.models import Irasai, Naudotojai, Komentarai
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.http import JsonResponse

from django.contrib.auth import get_user_model

from django.contrib import messages

def delete_comment(request):
    if request.method == 'POST':
        # Get the comment_id from the URL parameters
        comment_id = request.GET.get('comment_id')
        # Retrieve the comment object from the database or return 404 if not found
        comment = get_object_or_404(Komentarai, id=comment_id)
        # Delete the comment
        comment.delete()
        # Return a success response
        return JsonResponse({'message': 'Comment deleted successfully.'})
    else:
        # Return a method not allowed response for non-POST requests
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)

@login_required
def like_comment(request, pk):
    comment = get_object_or_404(Komentarai, pk=pk)
    
    if request.user.is_authenticated:
        user = Naudotojai.objects.get(user=request.user)
        
        if user in comment.likes.all():
            # User has already liked this comment
            comment.likes.remove(user)
            message = "You have unliked this comment."
            message_type = "info"
        else:
            # User has not yet liked this comment
            comment.likes.add(user)
            message = "You have liked this comment."
            message_type = "success"
    else:
        message = "You need to be logged in to like a comment."
        message_type = "error"
            
    # Return JSON response to indicate success and provide message
    return JsonResponse({'message': message, 'type': message_type})



@login_required
def add_comment(request, irasas_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        try:
            irasas = Irasai.objects.get(id=irasas_id)
        except ObjectDoesNotExist:
            return render(request, 'error_page.html', {'error_message': 'Irasai does not exist'}, status=404)

        if hasattr(request.user, 'naudotojai'):
            naudotojas = request.user.naudotojai
        else:
            return render(request, 'error_page.html', {'error_message': 'User does not have related naudotojai'}, status=400)

        Komentarai.objects.create(tekstas=text, fk_Irasasid_Irasas=irasas, fk_Naudotojasid_Naudotojas=naudotojas, data=date.today())
        return redirect(reverse('Forumas:forumasview'))  # Redirect to the forum home page
    else:
        # Handle GET requests if needed
        return HttpResponse("Only POST requests are allowed", status=405)

@login_required
def forumasview(request):
    irasai_list = Irasai.objects.all().select_related('fk_Naudotojasid_Naudotojas')
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    return render(request, 'Forumas.html', {'topics': irasai_list, 'username': username})


@login_required
def create_topic(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        category = request.POST.get('recipient')  # Extract the selected category
        print("Received values - title:", title, ", text:", text, ", category:", category)  # Debugging
        if title and text and category:  # Check if title, text, and category are provided
            # Get the related Naudotojai instance for the logged-in user
            user = request.user.naudotojai
            today = date.today()
            # Create the Irasai instance
            Irasai.objects.create(
                pavadinimas=title,
                tekstas=text,
                data=today,
                fk_Naudotojasid_Naudotojas=user,
                category=category  # Save the selected category
            )
            messages.success(request, 'Topic created successfully.')
            return redirect('Forumas:forumasview')
        else:
            messages.error(request, 'Please provide both title, text, and select a category.')
            return redirect('Forumas:forumasview')  # Redirect back to the forum view
    return render(request, 'Forumas.html', {})  # Render the forum page for GET requests
