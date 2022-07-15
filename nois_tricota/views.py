from django.views.generic import TemplateView, RedirectView


class Admin(RedirectView):
    url = 'https://datastudio.google.com/reporting/ab1455eb-111a-46a7-b2f4-7554c427aec3/page/S33B'


class Card(TemplateView):
    def get_template_names(self):
        if self.request.path == '/nois-tricota/juliana-bonazone/':
            template_name = 'nois_tricota/juliana-bonazone.html'
        if self.request.path == '/nois-tricota/tiberio-mendonca/':
            template_name = 'nois_tricota/tiberio-mendonca.html'
        return template_name


    