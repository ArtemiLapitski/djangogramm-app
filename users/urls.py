from django.urls import path
from users.views import Registration, Activation, Login, Logout, PasswordResetRequest, PasswordReset

urlpatterns = [
    path('register', Registration.as_view(), name="register"),
    path('activate/<activation_link>', Activation.as_view(), name="activate"),
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout"),
    path('reset/', PasswordResetRequest.as_view(), name="request_reset"),
    path('reset/<password_reset_link>', PasswordReset.as_view(), name="reset"),
]
