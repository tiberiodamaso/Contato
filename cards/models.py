from django.db import models

class Empresa(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=200)
    criada = models.DateField(verbose_name='Criada', auto_now_add=True)
    atualizada = models.DateField(verbose_name='Atualizada', auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome


class Card(models.Model):
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', on_delete=models.CASCADE, related_name='cards')
    img_perfil = models.ImageField(verbose_name='Foto perfil')
    primeiro_nome = models.CharField(verbose_name='Primeiro nome', max_length=20)
    ultimo_nome = models.CharField(verbose_name='Último nome', max_length=20)
    whatsapp = models.CharField(verbose_name='Whatsapp', max_length=30)
    facebook = models.CharField(verbose_name='Facebook', max_length=200)
    instagram = models.CharField(verbose_name='Instagram', max_length=200)
    telefone = models.CharField(verbose_name='Telefone', max_length=30)
    criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)

    class Meta:
        verbose_name = 'Cartão'
        verbose_name_plural = 'Cartões'

    def __str__(self):
        return self.primeiro_nome + self.ultimo_nome

