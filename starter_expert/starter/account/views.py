from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View

# Create your views here.

class LoginView(View):
    template_name = 'account/login.html'

    def get(self, request):
        message = ''
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('staff_home')

        message = 'Неправильный логин или пароль'
        return render(request, self.template_name, context={'message': message})


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('login')


class CabinetView(View):
    template_name = 'account/cabinet.html'
    def get(self, request):
        return render(request, self.template_name)