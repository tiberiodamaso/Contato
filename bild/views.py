from django.views.generic import TemplateView, RedirectView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class Card(TemplateView):
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
