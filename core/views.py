from django.shortcuts import render, redirect
from django.contrib.auth import login

from . import forms


def home(request):
    return render(request, 'home.html')


def sign_up(request):
    form = forms.SignUpForm()

    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email').lower()

            user = form.save(commit=False)
            user.username = email
            user.email = email
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            
            form.save(user)  # Save the form to the Customer model

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')  # Redirect to the user home page

    return render(request, 'sign_up.html', {'form': form})