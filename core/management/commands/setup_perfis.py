from decouple import config
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from core.models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico


class Command(BaseCommand):
    help = 'Cria os grupos de usuários (Perfis), atribui permissões e opcionalmente provisiona usuários de homologação.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuarios-demo',
            action='store_true',
            help='Cria ou atualiza usuários padrão de homologação (dono, atendente, mecanico) para deploy no Render.',
        )

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

        grupos_criados = {}
        for nome_grupo, codinomes in perfis.items():
            grupo, criado = Group.objects.get_or_create(name=nome_grupo)
            perms = Permission.objects.filter(content_type__app_label='core', codename__in=codinomes)
            grupo.permissions.set(perms)
            grupos_criados[nome_grupo] = grupo
            status_txt = 'criado' if criado else 'atualizado'
            self.stdout.write(self.style.SUCCESS(f'Perfil "{nome_grupo}" {status_txt} com {perms.count()} permissões.'))

        if options.get('usuarios_demo') or config('CREATE_DEMO_USERS', default=False, cast=bool):
            senha_padrao = config('DEMO_USERS_PASSWORD', default='NovaMec@2026')
            usuarios_demo = [
                ('dono', 'Dono/Gerente', True, 'Rodrigo (Dono/Gerente)'),
                ('atendente', 'Atendente', False, 'João (Atendente)'),
                ('mecanico', 'Mecânico', False, 'Felipe (Mecânico)'),
            ]
            for username, nome_grupo, is_super, first_name in usuarios_demo:
                user, u_criado = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': first_name,
                        'email': f'{username}@novamecanica.com.br',
                        'is_staff': is_super,
                        'is_superuser': is_super,
                    },
                )
                if u_criado:
                    user.set_password(senha_padrao)
                    user.save()
                user.groups.add(grupos_criados[nome_grupo])
                self.stdout.write(
                    self.style.SUCCESS(f'Usuário "{username}" vinculado ao perfil "{nome_grupo}".')
                )

        self.stdout.write(self.style.SUCCESS('Todos os perfis foram configurados com sucesso!'))
