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
            print(link)
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
    return HttpResponse('activating')


def login(request):
    context = dict()
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user:
            auth.login(request, user)
            #messages.success(request, 'Login Successful.')
            return redirect('home')
        else:
            messages.error(request, 'Check your email or password!')
            return redirect('login')

    return render(request, 'accounts/login.html', context)


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out successfully!')
    return redirect('login')
