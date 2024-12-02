from django.shortcuts import render, redirect
from django.dispatch import receiver
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, logout
from allauth.account.signals import user_signed_up
from users.forms import RegistrationForm, ActivationForm, LoginForm, PasswordResetRequestForm, PasswordResetForm
from users.services import UserService


class Registration(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'users/registration.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            activation_link = UserService.generate_activation_link()
            UserService.create_user(email, activation_link)

            UserService.send_activation_email(
                email=email,
                domain=get_current_site(request).domain,
                activation_link=activation_link
            )
            return render(request, 'message.html',
                          {'message': f"Activation link has been sent to {email}"})
        return render(request, 'users/registration.html', {'form': form})


class Activation(View):
    def get(self, request, activation_link):
        if not UserService.check_activation_link(activation_link):
            message = "Activation link is invalid"
            return render(request, 'message.html', {'message': message})

        if UserService.is_active(activation_link):
            message = "The user has already been activated. You can log in now."
            return render(request, 'message.html', {'message': message})

        if UserService.check_activation_timestamp(activation_link):
            form = ActivationForm()
            return render(request, 'users/activation.html', {'form': form, 'activation_link': activation_link})

        message = "Activation link has expired. Please register again"
        UserService.delete(activation_link)
        return render(request, 'message.html', {'message': message})

    def post(self, request, activation_link):
        form = ActivationForm(request.POST, request.FILES)
        if form.is_valid():
            user = UserService.activate_user(activation_link=activation_link, **form.cleaned_data)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('feed')
        return render(request, 'users/activation.html', {'form': form, 'activation_link': activation_link})


class Login(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
        return render(request, 'users/login.html', {'form': form})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('feed')


class PasswordResetRequest(View):
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, 'users/password_reset.html', {'form': form})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password_reset_link = UserService.add_password_reset_link(email)
            UserService.send_password_reset_email(
                email=email,
                domain=get_current_site(request).domain,
                password_reset_link=password_reset_link
            )
            return render(request, 'message.html', {'message': "Link for password reset has been sent to your email"})
        return render(request, 'users/password_reset.html', {'form': form})


class PasswordReset(View):

    def get(self, request, password_reset_link):
        if UserService.check_password_reset_link(password_reset_link):
            if UserService.check_password_reset_timestamp(password_reset_link):
                form = PasswordResetForm()
                return render(request, 'users/password_reset.html', {'form': form})
            return render(request, 'message.html', {'message': "Link has already expired"})
        return render(request, 'message.html', {'message': "Link is invalid"})

    def post(self, request, password_reset_link):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            UserService.reset_password(password_reset_link, password)
            return render(request, 'message.html', {'message': "Password has been changed. You can sign in now"})
        return render(request, 'users/password_reset.html',
                      {'form': form, 'password_reset_link': password_reset_link})


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    user.activation_link = UserService.generate_activation_link()
    user.save()
