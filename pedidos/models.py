from django.db import models
from usuarios.models import Usuario

class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuário', related_name='pedidos')
    # valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pendente')
    id_pgto_mercado_pago = models.CharField(max_length=50, null=True, blank=True)
    criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return self.usuario.get_full_name()

