from django.contrib import admin
from .models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico


class VeiculoInline(admin.TabularInline):
    model = Veiculo
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'cpf', 'telefone', 'email', 'criado_em')
    search_fields = ('nome', 'cpf', 'telefone', 'email')
    inlines = [VeiculoInline]


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'cliente', 'marca', 'modelo', 'ano')
    search_fields = ('placa', 'marca', 'modelo', 'cliente__nome', 'cliente__cpf')
    list_filter = ('marca', 'ano')


@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'preco', 'estoque', 'atualizado_em')
    search_fields = ('nome', 'descricao')
    list_filter = ('estoque',)


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'preco', 'atualizado_em')
    search_fields = ('nome', 'descricao')


class ItemPecaInline(admin.TabularInline):
    model = ItemPeca
    extra = 0
    readonly_fields = ('subtotal',)


class ItemServicoInline(admin.TabularInline):
    model = ItemServico
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'veiculo', 'status', 'desconto_percentual', 'subtotal', 'total', 'criado_em')
    list_filter = ('status', 'criado_em')
    search_fields = ('id', 'cliente__nome', 'veiculo__placa')
    inlines = [ItemPecaInline, ItemServicoInline]
    readonly_fields = ('subtotal', 'valor_desconto', 'total', 'criado_em', 'atualizado_em')
