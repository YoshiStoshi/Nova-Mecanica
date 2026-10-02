from decimal import Decimal
from django import forms
from django.core.validators import MinValueValidator

from .forms_login import BootstrapFormMixin
from .models import Cliente, Veiculo, Peca, Servico, OrdemServico
from .validators import normalizar_cpf, normalizar_placa


class ClienteForm(BootstrapFormMixin, forms.ModelForm):
    cpf = forms.CharField(label='CPF', max_length=14, help_text='11 dígitos, com ou sem pontuação.')

    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone', 'email']
        widgets = {
            'telefone': forms.TextInput(attrs={'type': 'tel', 'placeholder': '(16) 99999-9999'}),
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do cliente'}),
            'email': forms.EmailInput(attrs={'placeholder': 'cliente@exemplo.com'}),
        }

    def clean_cpf(self):
        return normalizar_cpf(self.cleaned_data['cpf'])


class VeiculoForm(BootstrapFormMixin, forms.ModelForm):
    placa = forms.CharField(max_length=20, help_text='Formatos aceitos: ABC-1234 e ABC1D23.')

    class Meta:
        model = Veiculo
        fields = ['cliente', 'placa', 'marca', 'modelo', 'ano']
        widgets = {
            'marca': forms.TextInput(attrs={'placeholder': 'Ex: Volkswagen, Chevrolet'}),
            'modelo': forms.TextInput(attrs={'placeholder': 'Ex: Gol 1.0, Onix Plus'}),
            'ano': forms.NumberInput(attrs={'placeholder': 'Ex: 2022', 'min': 1900, 'max': 2099}),
        }

    def clean_placa(self):
        return normalizar_placa(self.cleaned_data['placa'])


class DescontoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ['desconto_percentual']
        widgets = {'desconto_percentual': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': '0.01'})}
        help_texts = {'desconto_percentual': 'De 0% a 100%. Use até duas casas decimais.'}


class ItemPecaForm(BootstrapFormMixin, forms.Form):
    peca = forms.ModelChoiceField(label='Peça', queryset=Peca.objects.all())
    quantidade = forms.IntegerField(min_value=1, max_value=2147483647, initial=1)


class ItemServicoForm(BootstrapFormMixin, forms.Form):
    servico = forms.ModelChoiceField(label='Serviço', queryset=Servico.objects.all())
    quantidade = forms.IntegerField(min_value=1, max_value=2147483647, initial=1)


class PecaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Peca
        fields = ['nome', 'descricao', 'preco', 'estoque']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome ou código da peça'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Descrição detalhada'}),
            'preco': forms.NumberInput(attrs={'min': '0.00', 'step': '0.01', 'placeholder': '0.00'}),
            'estoque': forms.NumberInput(attrs={'min': '0', 'step': '1', 'placeholder': '0'}),
        }
        labels = {
            'nome': 'Nome da Peça',
            'descricao': 'Descrição',
            'preco': 'Preço Unitário (R$)',
            'estoque': 'Estoque Inicial',
        }
        help_texts = {
            'preco': 'Preço unitário em Reais (deve ser maior ou igual a zero).',
            'estoque': 'Quantidade inicial em estoque (deve ser maior ou igual a zero).',
        }

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco < 0:
            raise forms.ValidationError('O preço unitário não pode ser negativo.')
        return preco

    def clean_estoque(self):
        estoque = self.cleaned_data.get('estoque')
        if estoque is not None and estoque < 0:
            raise forms.ValidationError('O estoque não pode ser negativo.')
        return estoque


class ServicoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Servico
        fields = ['nome', 'descricao', 'preco']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do serviço'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Descrição detalhada do serviço prestado'}),
            'preco': forms.NumberInput(attrs={'min': '0.00', 'step': '0.01', 'placeholder': '0.00'}),
        }
        labels = {
            'nome': 'Nome do Serviço',
            'descricao': 'Descrição',
            'preco': 'Preço (R$)',
        }
        help_texts = {
            'preco': 'Preço do serviço em Reais (deve ser maior ou igual a zero).',
        }

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco < 0:
            raise forms.ValidationError('O preço do serviço não pode ser negativo.')
        return preco


class AjusteEstoqueForm(BootstrapFormMixin, forms.Form):
    OPERACAO_CHOICES = [
        ('adicionar', 'Adicionar ao estoque (+)'),
        ('remover', 'Subtrair do estoque (-)'),
        ('definir', 'Definir novo saldo fixo (=)'),
    ]
    operacao = forms.ChoiceField(
        label='Tipo de Movimentação',
        choices=OPERACAO_CHOICES,
        initial='adicionar'
    )
    quantidade = forms.IntegerField(
        label='Quantidade',
        min_value=0,
        help_text='Informe a quantidade para ajuste.'
    )
    motivo = forms.CharField(
        label='Justificativa / Motivo',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Compra de fornecedor, avaria, contagem física'})
    )
