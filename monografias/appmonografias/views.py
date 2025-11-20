from django.shortcuts import render, redirect, get_object_or_404
from .forms import MonografiaForm, ProfessorForm, BancaForm
from django.contrib.auth.decorators import login_required
from .models import Monografia, Professor, Banca
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def dashboard(request):
    if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
        return render(request, 'dashboard_admin.html')
    elif request.user.groups.filter(name='Professor').exists():
        return render(request, 'dashboard_professor.html')
    else:
        return render(request, 'dashboard_aluno.html')

@login_required
def agendar_defesa(request):
    if request.method == 'POST':
        form = BancaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_defesas')
    else:
        form = BancaForm()
    return render(request, 'agendar_defesa.html', {'form': form})

@login_required
def listar_defesas(request):
    defesas = Banca.objects.all()
    is_admin = request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()
    is_professor = request.user.groups.filter(name='Professor').exists()


    for banca in defesas:
        banca.pode_gerenciar = (
            is_admin or
            (is_professor and banca.professores_avaliadores.filter(user=request.user).exists())
        )

    return render(request, 'listar_defesas.html', {
        'defesas': defesas,
        'is_admin': is_admin,
        'is_professor': is_professor,
    })

@login_required
def deletar_defesa(request, pk):
    banca = get_object_or_404(Banca, pk=pk)
    is_admin = request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()

    if not is_admin:
        return redirect('listar_defesas')

    if request.method == 'POST':
        banca.delete()
        return redirect('listar_defesas')

    return render(request, 'deletar_defesa.html', {'banca': banca})

@login_required
def gerenciar_defesa(request, pk):
    banca = get_object_or_404(Banca, pk=pk)
    is_admin = request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()
    is_professor = request.user.groups.filter(name='Professor').exists() and banca.professores_avaliadores.filter(user=request.user).exists()

    if request.method == 'POST' and (is_admin or is_professor):
        nota = request.POST.get('nota_final')
        status = request.POST.get('status')

        if nota is not None and nota != '':
            banca.nota_final = float(nota)
        if status:
            banca.status = status

        banca.save()
        return redirect('listar_defesas')

    return render(request, 'gerenciar_defesa.html', {
        'banca': banca,
        'is_admin': is_admin,
        'is_professor': is_professor,
    })

@login_required
def criar_monografia(request):
    if request.method == 'POST':
        form = MonografiaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Monografia criada com sucesso!")
            return redirect('listar_monografias')
        else:
            messages.error(request, "Erro ao criar a monografia. Verifique os campos.")
    else:
        form = MonografiaForm()
    return render(request, 'criar_monografia.html', {'form': form})

@login_required
def listar_monografias(request):
    query = request.GET.get('q')
    monografias = Monografia.objects.all()
    if query:
        monografias = monografias.filter(
            Q(titulo__icontains=query) |
            Q(orientador__user__username__icontains=query) |
            Q(coorientador__user__username__icontains=query) |
            Q(palavras_chave__icontains=query)
        )

    is_admin = request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()

    paginator = Paginator(monografias, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'listar_monografias.html', {'monografias': page_obj, 'is_admin': is_admin})

@login_required
def deletar_monografia(request, pk):
    monografia = get_object_or_404(Monografia, pk=pk)
    
    if not request.user.is_superuser and monografia.orientador.user != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        monografia.delete()
        return redirect('listar_monografias')

    return render(request, 'deletar_monografia.html', {'monografia': monografia})

@login_required
def editar_monografia(request, pk):
    monografia = Monografia.objects.get(pk=pk)
    if request.method == 'POST':
        form = MonografiaForm(request.POST, request.FILES, instance=monografia)
        if form.is_valid():
            form.save()
            return redirect('listar_monografias')
    else:
        form = MonografiaForm(instance=monografia)
    return render(request, 'editar_monografia.html', {'form': form})

def criar_professor(request):
    if request.method == 'POST':
        form = ProfessorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email']
            )
            # adiciona grupo professor
            grupo = Group.objects.get(name='Professor')
            user.groups.add(grupo)
            # cria objeto Professor
            Professor.objects.create(user=user, titulação=data['titulação'], area_pesquisa=data['area_pesquisa'])
            messages.success(request, "Professor criado com sucesso!")
            return redirect('dashboard')
    else:
        form = ProfessorForm()
    return render(request, 'criar_professor.html', {'form': form})