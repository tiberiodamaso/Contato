from django.views.generic import TemplateView, RedirectView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from cards.models import Card


class Administracao(LoginRequiredMixin, ListView):
    model = Card
    template_name = 'bild/admin.html'
    context_object_name = 'cartoes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ua = self.request.META['HTTP_USER_AGENT']
        queryset = Card.objects.filter(empresa__nome='Bild')
        context['cartoes'] = queryset
        return context

class Cartao(TemplateView):
    def get_template_names(self):
        if self.request.path == '/bild/guilherme-leal/':
            template_name = 'bild/guilherme-leal.html'
        if self.request.path == '/bild/juliana-costa/':
            template_name = 'bild/juliana-costa.html'
        if self.request.path == '/bild/tiberio-mendonca/':
            template_name = 'bild/tiberio-mendonca.html'
        if self.request.path == '/bild/vitoria-almeida/':
            template_name = 'bild/vitoria-almeida.html'
        return template_name