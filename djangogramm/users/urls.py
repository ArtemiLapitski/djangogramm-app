from django.urls import path
from .views import Registration, Activation, Login, Logout

urlpatterns = [
    path('register', Registration.as_view(), name="register"),
    path('activate/<activation_link>', Activation.as_view(), name="activate"),
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout")
]
