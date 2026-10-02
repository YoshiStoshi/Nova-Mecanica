from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Cliente(models.Model):
    nome = models.CharField('Nome', max_length=150)
    cpf = models.CharField('CPF', max_length=14, unique=True)
    telefone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', blank=True, null=True, default='')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.cpf})"


class Veiculo(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='veiculos',
        verbose_name='Proprietário'
    )
    placa = models.CharField('Placa', max_length=10, unique=True)
    marca = models.CharField('Marca', max_length=50)
    modelo = models.CharField('Modelo', max_length=50)
    ano = models.PositiveIntegerField('Ano')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['marca', 'modelo']

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo} ({self.ano})"


class Peca(models.Model):
    nome = models.CharField('Nome', max_length=100, blank=True)
    descricao = models.CharField('Descrição', max_length=255)
    preco = models.DecimalField(
        'Preço Unitário (R$)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    estoque = models.IntegerField(
        'Estoque Atual',
        default=0,
        validators=[MinValueValidator(0)]
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Peça'
        verbose_name_plural = 'Peças'
        ordering = ['descricao']

    def __str__(self):
        return f"{self.descricao} - R$ {self.preco:.2f}"

    def save(self, *args, **kwargs):
        if not self.nome:
            self.nome = self.descricao[:100]
        super().save(*args, **kwargs)


class Servico(models.Model):
    nome = models.CharField('Nome', max_length=100, blank=True)
    descricao = models.CharField('Descrição', max_length=255)
    preco = models.DecimalField(
        'Preço (R$)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['descricao']

    def __str__(self):
        return f"{self.descricao} - R$ {self.preco:.2f}"

    def save(self, *args, **kwargs):
        if not self.nome:
            self.nome = self.descricao[:100]
        super().save(*args, **kwargs)


class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('em_execucao', 'Em Execução'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ordens',
        verbose_name='Cliente'
    )
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name='ordens',
        verbose_name='Veículo'
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    desconto_percentual = models.DecimalField(
        'Desconto (%)',
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    subtotal = models.DecimalField(
        'Subtotal (R$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_desconto = models.DecimalField(
        'Valor Desconto (R$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total = models.DecimalField(
        'Total (R$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    observacoes = models.TextField('Observações', blank=True, default='')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-id']

    def __str__(self):
        return f"OS #{self.pk} - {self.cliente.nome} ({self.get_status_display()})"


class ItemPeca(models.Model):
    ordem = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name='itens_peca',
        verbose_name='Ordem de Serviço'
    )
    peca = models.ForeignKey(
        Peca,
        on_delete=models.PROTECT,
        related_name='itens_os',
        verbose_name='Peça'
    )
    quantidade = models.PositiveIntegerField(
        'Quantidade',
        default=1,
        validators=[MinValueValidator(1)]
    )
    preco_unitario_historico = models.DecimalField(
        'Preço Unitário Histórico (R$)',
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Item Peça'
        verbose_name_plural = 'Itens Peça'
        constraints = [
            models.UniqueConstraint(fields=['ordem', 'peca'], name='unique_peca_por_ordem')
        ]

    @property
    def subtotal(self):
        return (Decimal(self.quantidade) * self.preco_unitario_historico).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.quantidade}x {self.peca.descricao} na OS #{self.ordem_id}"


class ItemServico(models.Model):
    ordem = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name='itens_servico',
        verbose_name='Ordem de Serviço'
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name='itens_os',
        verbose_name='Serviço'
    )
    quantidade = models.PositiveIntegerField(
        'Quantidade',
        default=1,
        validators=[MinValueValidator(1)]
    )
    preco_unitario_historico = models.DecimalField(
        'Preço Unitário Histórico (R$)',
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Item Serviço'
        verbose_name_plural = 'Itens Serviço'
        constraints = [
            models.UniqueConstraint(fields=['ordem', 'servico'], name='unique_servico_por_ordem')
        ]

    @property
    def subtotal(self):
        return (Decimal(self.quantidade) * self.preco_unitario_historico).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.quantidade}x {self.servico.descricao} na OS #{self.ordem_id}"
