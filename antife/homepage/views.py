from django.shortcuts import render, HttpResponse, redirect
from .models import Naudotojai
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.sessions.models import Session
import re

def home(request):
    return render(request, "home.html")

def loged(request):
    return render(request, "baseLogged.html")

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User


from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Naudotojai
import re

from datetime import datetime

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        name = request.POST.get('name')
        lastName = request.POST.get('lastName')
        phoneNumber = request.POST.get('phoneNumber')
        birthday = request.POST.get('birthday')
        password = request.POST.get('password')
        if User.objects.filter(username=username):
            messages.error(request, 'Šis slapyvardis jau užimtas!')
            return render (request, 'register.html')
        # Validate email format using regular expression
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email) or not email.endswith('@gmail.com'):
            messages.error(request, 'Neteisingai įvestas elektronins paštas. Įveskite teisingą.')
        elif User.objects.filter(email=email).exists():
            # Set the message if the email already exists
            messages.error(request, 'Šis elektroninis paštas jau užimtas.')
        elif not re.match(r"\+370\d{8}", phoneNumber):
            # Validate phone number format
            # ^\+370 - starts with +370
            # \d{8}$ - followed by exactly 8 digits
            messages.error(request, 'Neteisingai įvestas telefono numeris. Įveskite per naują' )
        else:
            # Validate birthdate format and range
            try:
                birthdate_obj = datetime.strptime(birthday, '%Y-%m-%d').date()
                today = datetime.now().date()
                if birthdate_obj >= today:
                    raise ValueError  # Birthdate should be in the past
            except ValueError:
                messages.error(request, 'Neteisinga gimimo data. Pasirinkite dar kartą.')
                return render(request, 'register.html')
            
            # Create a new user account
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Hash the password
            hashed_password = make_password(password)
            
            # Save the user profile data to the database
            new_user_profile = Naudotojai(
                user=user,  # Associate the profile with the newly created user
                vardas=name,
                telefonas=phoneNumber,
                pavarde=lastName,
                gimimo_data=birthdate_obj,
                level=0  # Set default level or adjust as needed
            )  
            new_user_profile.save() 

            messages.success(request, f'Registracija sėkminga. Gali bandyt prisijungt!')
            return redirect('/login')  # Change 'home' to the name of your homepage URL pattern
    
    return render(request, 'register.html')





from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
            
        if user is not None and user.is_active:
            django_login(request, user)
            messages.success(request, f"Sėkmingai prisijungėte! Sveiki, {username}")
            return render(request, 'baseLogged.html')  # Redirect to the main forum page
        else:
            messages.error(request, "Neteisingi prisijungimo duomenys. Bandyk dar kartą.")
    
    return render(request, 'login.html')






from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    request.session.flush()  # Clear all session data
    return redirect('/')  # Redirect to the homepage or any other desired URL
