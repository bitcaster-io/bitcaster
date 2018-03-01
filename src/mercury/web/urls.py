from django.urls import include, path
from django.views.generic import TemplateView

# from mercury.web.views.register import confirm_email
# from mercury.web.views.views import OrganizationDetail
from .views import (ApplicationDetail, LoginView, LogoutView,
                    MercuryTemplateView, OrganizationDetail, SubscriptionList,
                    UserProfile, UserRegister, confirm_email,)

urlpatterns = [
    path(r'login/', LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),

    path(r'user/register/', UserRegister.as_view(), name='user-register'),

    path(r'user/register/register-wait-email/<int:pk>/',
         TemplateView.as_view(template_name='bitcaster/registration/register_wait_email.html'),
         name='register-wait-email'),
    path(r'user/register/confirm-email/<int:pk>/<str:check>/',
         confirm_email, name='confirm-email'),
    path(r'user/profile/', UserProfile.as_view(), name='user-profile'),

    path(r'new-user/', TemplateView.as_view(template_name='bitcaster/new-user.html')),
    path(r'new-association/', TemplateView.as_view(template_name='bitcaster/new-association.html')),

    path(r'terms/', TemplateView.as_view(template_name='bitcaster/legal/terms.html'), name='legal-terms'),
    path(r'privacy/', TemplateView.as_view(template_name='bitcaster/legal/privacy.html'), name='legal-privacy'),

    path(r'<slug:org>/', OrganizationDetail.as_view(), name='org-index'),

    path(r'<slug:org>/<slug:app>/', ApplicationDetail.as_view(), name='app-index'),

    path(r'<slug:org>/<slug:app>/subscriptions/',
         SubscriptionList.as_view(), name='user-subscriptions'),

    path(r'', include('social_django.urls', namespace='social')),
    path(r'', TemplateView.as_view(template_name='bitcaster/index.html'),
         name='index'),

]
