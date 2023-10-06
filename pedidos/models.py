from django.db import models
from usuarios.models import Usuario

class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuário', related_name='pedidos')
    assinatura_id = models.CharField(verbose_name='Assinatura ID', max_length=50)
    payer_id = models.CharField(verbose_name='Payer ID', max_length=20)
    date_created = models.DateField(verbose_name='Criado', max_length=50)
    valor = models.DecimalField(verbose_name='Valor', max_digits=10, decimal_places=2)
    status = models.CharField(verbose_name='Status', max_length=20, default='pendente')
    start_date = models.DateField(verbose_name='Início', max_length=50)
    next_payment_date = models.DateField(verbose_name='Próximo pgto', max_length=50)
    last_modified = models.DateField(verbose_name='Atualizado', max_length=50)

    # id_pgto_mercado_pago = models.CharField(max_length=50, null=True, blank=True)
    # criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    # atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return self.usuario.get_full_name()

