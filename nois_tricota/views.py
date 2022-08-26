from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin



class Card(TemplateView):
    def get_template_names(self):
        if self.request.path == '/nois-tricota/juliana-bonazone/':
            template_name = 'nois-tricota/juliana-bonazone.html'
        if self.request.path == '/nois-tricota/tiberio-mendonca/':
            template_name = 'nois-tricota/tiberio-mendonca.html'
        return template_name


    