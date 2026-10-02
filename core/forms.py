from django import forms
from .forms_login import BootstrapFormMixin

from .models import Cliente, Veiculo, Peca, Servico, OrdemServico
from .validators import normalizar_cpf, normalizar_placa


class ClienteForm(BootstrapFormMixin, forms.ModelForm):
    cpf = forms.CharField(label='CPF', max_length=14, help_text='11 dígitos, com ou sem pontuação.')

    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone', 'email']
        widgets = {'telefone': forms.TextInput(attrs={'type': 'tel'})}

    def clean_cpf(self):
        return normalizar_cpf(self.cleaned_data['cpf'])


class VeiculoForm(BootstrapFormMixin, forms.ModelForm):
    placa = forms.CharField(max_length=20, help_text='Formatos aceitos: ABC-1234 e ABC1D23.')

    class Meta:
        model = Veiculo
        fields = ['cliente', 'placa', 'marca', 'modelo', 'ano']

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
