from django.shortcuts import render

def home(request):
    """Página inicial do sistema Nova Mecânica"""
    context = {
        'titulo': 'Início',
        'sistema': 'Nova Mecânica',
        'versao': '1.0.0'
    }
    return render(request, 'core/home.html', context)

