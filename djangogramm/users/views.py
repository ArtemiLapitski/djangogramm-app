from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, logout
from .forms import RegistrationForm, ActivationForm
from .services import UserService


class Registration(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'users/registration.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            activation_link = UserService.generate_activation_link()
            UserService.create_user(form, activation_link)

            email = form.cleaned_data['email']
            UserService.send_email(
                email=email,
                domain=get_current_site(request).domain,
                activation_link=activation_link
            )

            return render(request, 'users/message.html',
                          {'message': f"Activation link has been sent to {email}"})
        else:
            return render(request, 'users/registration.html', {'form': form})


class Activation(View):
    def get(self, request, activation_link):
        if not UserService.check_activation_link(activation_link):
            message = "Activation link is invalid"
            return render(request, 'users/message.html', {'message': message})
        elif UserService.is_active(activation_link):
            message = "The user has already been activated. You can log in now."
            return render(request, 'users/message.html', {'message': message})
        elif UserService.check_timestamp(activation_link):
            form = ActivationForm()
            return render(request, 'users/activation.html', {'form': form, 'activation_link': activation_link})
        else:
            message = "Activation link has expired. Please register again"
            UserService.delete(activation_link)
            return render(request, 'users/message.html', {'message': message})

    def post(self, request, activation_link):
        form = ActivationForm(request.POST, request.FILES)
        if form.is_valid():
            UserService.activate_user(activation_link=activation_link, **form.cleaned_data)
            message = "The user has been activated. You can log in now."
            return render(request, 'users/message.html', {'message': message})
        else:
            return render(request, 'users/activation.html', {'form': form, 'activation_link': activation_link})


class Login(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'users/login.html', {'form': form})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('feed')
