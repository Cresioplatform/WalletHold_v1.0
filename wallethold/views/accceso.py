from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from wallethold.forms import SignUpForm
from wallethold.utils import anonymous_required, class_view_decorator


@class_view_decorator(anonymous_required)
class SignInView(LoginView):
    template_name = 'acceso/iniciar_sesion.html'



class SignUpView(CreateView):
    template_name = 'acceso/registro.html'
    form_class = SignUpForm

    def form_valid(self, form):
        '''
        En este parte, si el formulario es valido guardamos lo que se obtiene de él y usamos authenticate para que el usuario incie sesión luego de haberse registrado y lo redirigimos al index
        '''
        form.save()
        usuario = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        usuario = authenticate(username=usuario, password=password)
        login(self.request, usuario)
        return redirect('/')



from django.contrib.auth.views import LogoutView
class SignOutView(LogoutView):
    pass