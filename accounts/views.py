from django.shortcuts import render, redirect, reverse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


from .forms import RegistrationForm
from .models import Account

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                               phone_number=phone_number, email=email, password=password)
            user.save()

            #sending_verification_mail
            #lets create a link which will contain domain, encrypted userid, token to verify
            domain = get_current_site(request)
            #base64 is used for numbers encrypted to string, use url_encrypt because it will exclude =,/,+
            encrypted_userid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            link = 'http://' + str(domain) + str(reverse('activate', kwargs={
                'enc_userid': encrypted_userid,
                'token': token
            }))
            mail_subject = "Please verify your email for GreatKart Account"
            mail_body = render_to_string('accounts/mail_body.html', request=request, context={
                'user': user,
                'link': link
            })
            mail_instance = EmailMessage(subject=mail_subject, body=mail_body, to=[email])
            mail_instance.send()
            messages.success(request, "Your registration is successful. Please check your email, Thank you!")
            return redirect('login')
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def activate(request, enc_userid, token):
    try:
        user = Account.objects.get(pk=urlsafe_base64_decode(enc_userid))

    except(ValueError, TypeError, OverflowError, Account.DoesNotExist):
        user = None

    if not user.is_active:
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account is activated!")
            return redirect('login')
        else:
            messages.info(request, 'Please use the link sent to you only.')
            return redirect('login')
    else:
        messages.info(request, 'Your account is already active. Please login to continue')
        return redirect('login')


def login(request):
    context = dict()
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user:
            auth.login(request, user)
            messages.success(request, 'Hello ' + user.first_name.capitalize() + ' You are successfully logged in!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Check your email or password!')
            return redirect('login')

    return render(request, 'accounts/login.html', context)


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out successfully!')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    context = dict()
    return render(request, 'accounts/dashboard.html', context)


def forgot_password(request):
    context = dict()
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # sending_reset_password_mail
            # lets create a link which will contain domain, encrypted userid, token to verify
            domain = get_current_site(request)
            # base64 is used for numbers encrypted to string, use url_encrypt because it will exclude =,/,+
            encrypted_userid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            link = 'http://' + str(domain) + str(reverse('reset_password', kwargs={
                'enc_userid': encrypted_userid,
                'token': token
            }))
            mail_subject = "Reset your Password - GreatKart Account"
            mail_body = render_to_string('accounts/reset_password_mail_body.html', request=request, context={
                'user': user,
                'link': link
            })
            mail_instance = EmailMessage(subject=mail_subject, body=mail_body, to=[email])
            mail_instance.send()
            messages.success(request, "Sent a link to reset your password. Please check your email, Thank you!")
            return redirect('login')
        else:
            messages.error(request, "Account does not exists with the given email address")
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html', context)


def reset_password(request, enc_userid, token):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                user = Account.objects.get(pk=urlsafe_base64_decode(enc_userid))
            except(ValueError, TypeError, OverflowError, Account.DoesNotExist):
                user = None
            if user and default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                messages.info(request, 'Password changed successfully. Please login')
                return redirect('login')
            else:
                messages.info(request, 'Please use the link sent to you only.')
                return redirect('forgot_password')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password', enc_userid=enc_userid, token=token)

    elif request.method == 'GET':
        try:
            user = Account.objects.get(pk=urlsafe_base64_decode(enc_userid))
        except(ValueError, TypeError, OverflowError, Account.DoesNotExist):
            user = None
        if user and default_token_generator.check_token(user, token):
            return render(request, 'accounts/reset_password.html')
        else:
            messages.info(request, 'Please use the link sent to you only.')
            return redirect('forgot_password')
    return redirect('forgot_password')