from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico


class Command(BaseCommand):
    help = 'Cria os grupos de usuários (Perfis) e atribui as permissões do sistema Nova Mecânica.'

    def handle(self, *args, **options):
        # 1. Obter permissões do app core
        core_permissions = Permission.objects.filter(content_type__app_label='core')
        
        # Mapa de permissões por perfil
        perfis = {
            'Dono/Gerente': [
                'add_cliente', 'change_cliente', 'delete_cliente', 'view_cliente',
                'add_veiculo', 'change_veiculo', 'delete_veiculo', 'view_veiculo',
                'add_peca', 'change_peca', 'delete_peca', 'view_peca',
                'add_servico', 'change_servico', 'delete_servico', 'view_servico',
                'add_ordemservico', 'change_ordemservico', 'delete_ordemservico', 'view_ordemservico',
                'add_itempeca', 'change_itempeca', 'delete_itempeca', 'view_itempeca',
                'add_itemservico', 'change_itemservico', 'delete_itemservico', 'view_itemservico',
            ],
            'Atendente': [
                'add_cliente', 'change_cliente', 'view_cliente',
                'add_veiculo', 'change_veiculo', 'view_veiculo',
                'view_peca', 'view_servico',
                'add_ordemservico', 'change_ordemservico', 'view_ordemservico',
                'add_itempeca', 'delete_itempeca', 'view_itempeca',
                'add_itemservico', 'delete_itemservico', 'view_itemservico',
            ],
            'Mecânico': [
                'view_ordemservico', 'change_ordemservico',
                'view_veiculo', 'view_peca', 'view_servico',
            ],
        }

        for nome_grupo, codinomes in perfis.items():
            grupo, criado = Group.objects.get_or_create(name=nome_grupo)
            perms = Permission.objects.filter(content_type__app_label='core', codename__in=codinomes)
            grupo.permissions.set(perms)
            status_txt = 'criado' if criado else 'atualizado'
            self.stdout.write(self.style.SUCCESS(f'Perfil "{nome_grupo}" {status_txt} com {perms.count()} permissões.'))

        self.stdout.write(self.style.SUCCESS('Todos os perfis foram configurados com sucesso!'))
