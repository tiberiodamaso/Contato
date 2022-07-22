from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class Administracao(LoginRequiredMixin, TemplateView):
    # url = 'https://datastudio.google.com/reporting/ab1455eb-111a-46a7-b2f4-7554c427aec3/page/S33B'
    template_name = 'nois_tricota/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ua = self.request.META['HTTP_USER_AGENT']
        return context

class Card(TemplateView):
    def get_template_names(self):
        if self.request.path == '/nois-tricota/juliana-bonazone/':
            template_name = 'nois_tricota/juliana-bonazone.html'
        if self.request.path == '/nois-tricota/tiberio-mendonca/':
            template_name = 'nois_tricota/tiberio-mendonca.html'
        return template_name


    