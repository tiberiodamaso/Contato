from django.db import models
from usuarios.models import Usuario

class Relatorio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuário', related_name='relatorios')
    stripe_id = models.CharField(verbose_name='Stripe ID', max_length=50)
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
    status = models.CharField(verbose_name='Status', max_length=20, default='pendente')
    stripe_customer = models.CharField(verbose_name='Stripe customer', max_length=100)
    date_created = models.DateField(verbose_name='Criado', auto_now_add=True)
    cancelamento = models.DateField(verbose_name='Cancelamento', default=None, blank=True, null=True)


    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'

    def __str__(self):
        return self.usuario.get_full_name()


class CartaoPF(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuário', related_name='cartoespf')
    stripe_id = models.CharField(verbose_name='Stripe ID', max_length=50)
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
    status = models.CharField(verbose_name='Status', max_length=20, default='pendente')
    date_created = models.DateField(verbose_name='Criado', auto_now_add=True)
    cancelamento = models.DateField(verbose_name='Cancelamento', default=None, blank=True, null=True)


    class Meta:
        verbose_name = 'Cartão PF'
        verbose_name_plural = 'Cartões PF'

    def __str__(self):
        return self.usuario.get_full_name()


class Ad(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuário', related_name='ads')
    stripe_id = models.CharField(verbose_name='Stripe ID', max_length=50)
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
    status = models.CharField(verbose_name='Status', max_length=20, default='pendente')
    date_created = models.DateField(verbose_name='Criado', auto_now_add=True)
    cancelamento = models.DateField(verbose_name='Cancelamento', default=None, blank=True, null=True)


    class Meta:
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'

    def __str__(self):
        return self.usuario.get_full_name()


class CartaoPJ(models.Model):

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuário', related_name='cartoespj')
    stripe_id = models.CharField(verbose_name='Stripe ID', max_length=50)
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
    status = models.CharField(verbose_name='Status', max_length=20, default='pendente')
    stripe_customer = models.CharField(verbose_name='Stripe customer', max_length=100)
    date_created = models.DateField(verbose_name='Criado', auto_now_add=True)
    cancelamento = models.DateField(verbose_name='Cancelamento', default=None, blank=True, null=True)


    class Meta:
        verbose_name = 'Cartão PJ'
        verbose_name_plural = 'Cartões PJ'

    def __str__(self):
        return self.usuario.get_full_name()


# class Pagamento(models.Model):
#     STATUS_CHOICES = [
#         ('pendente', 'Pendente'),
#         ('aprovado', 'Aprovado'),
#         ('falhou', 'Falhou'),
#     ]
    
#     stripe_session_id = models.CharField(verbose_name='Stripe session ID', max_length=255, unique=True)
#     customer_email = models.EmailField(verbose_name='E-mail do cliente')
#     amount = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
#     product = models.CharField(verbose_name='Produto', max_length=20)
#     status = models.CharField(verbose_name='Status', max_length=10, choices=STATUS_CHOICES, default='pendente')
#     created_at = models.DateTimeField(verbose_name='Criado', auto_now_add=True)
#     updated_at = models.DateTimeField(verbose_name='Atualizado', auto_now=True)

#     class Meta:
#         verbose_name = 'Pagamento'
#         verbose_name_plural = 'Pagamentos'

#     def __str__(self):
#         return f'{self.customer_email} - {self.amount} - {self.status}'
