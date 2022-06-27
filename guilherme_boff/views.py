from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'guilherme_boff/home.html'