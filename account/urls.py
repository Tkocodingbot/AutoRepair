from django.urls import path
from account import views
from django.contrib.auth import views as auth_view

from account.forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm


urlpatterns = [
    path('signup/',views.Signupuser.as_view(), name='signupuser'),
    path ('accounts/login', auth_view.LoginView.as_view(template_name='account/login.html', authentication_form=LoginForm, success_url='/home'), name='login'),
    
    #Authentications
    
    # path('password-reset/', auth_view.PasswordResetView.as_view(template_name='account/password_reset.html', form_class=MyPasswordResetForm), name='password_reset'),
    path('passwordchange/', auth_view.PasswordChangeView.as_view(template_name='account/changepassword.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone'), name='passwordchange'),
    path('passwordchangedone/', auth_view.PasswordChangeDoneView.as_view(template_name='account/passwordchangedone.html'), name='passwordchangedone'),
    path('logout/', views.logout, name='logout'),

    path('password-reset/', auth_view.PasswordResetView.as_view(template_name='account/password_reset.html',form_class=MyPasswordResetForm), name='password_reset'),
    path('password-reset/done/',auth_view.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_view.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html', form_class=MySetPasswordForm),name='password_reset_confirm'),
    path('password-reset-complete/', auth_view.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),

]
