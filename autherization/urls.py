from django.urls import path
from .views import ActivateAccountView,LoginView,LogoutView,AlertView,RegisterView
"""
TODO:
Add the urlpatterns of the endpoints, required for implementing
Todo GET (List and Detail), PUT, PATCH and DELETE.
"""

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register/', RegisterView.as_view()),
    path('alert/', AlertView.as_view()),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(),name="activate-account"),
]