from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Filter, Image
from .forms import FilterForm
from .forms import CustomUserCreationForm
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import datetime
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Create your views here.
def index(request):
    total_filters = Filter.objects.count()
    user_filters = Filter.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

    return render(request, '../templates/filters/index.html', {
        'total_filters': total_filters,
        'user_filters': user_filters
    })

def signup_user(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('index')
            except IntegrityError:
                error = 'Usuário já cadastrado!'
        else:
            error = 'As senhas não coincidem!'
        return render(request, '../templates/registration/signup.html', {
            'form': CustomUserCreationForm(),
            'error': error
        })
    return render(request, 'registration/signup.html', {'form': CustomUserCreationForm()})

@login_required
def logout_user(request):
    logout(request)
    return redirect('index')

def login_user(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, '../templates/registration/login.html', {
                'form': AuthenticationForm(),
                'error': 'Usuário ou senha inválidos.'
            })
        else:
            login(request, user)
            return redirect('index')
    else:
        return render(request, '../templates/registration/login.html',{
            'form': AuthenticationForm()
        })

@login_required
def filter_list(request):
    filters = Filter.objects.filter(user=request.user)

    unique_code = request.GET.get('unique_code', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if unique_code:
        filters = filters.filter(unique_code__icontains=unique_code)
    if start_date and end_date:
        try:

            start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            
            filters = filters.filter(sync_date__range=(start_date, end_date))
        except ValueError:
            filters = filters.none()

    return render(request, "filters/filter_list.html", {"filters": filters})

@login_required
def filter_detail(request, pk):
    filter_instance = get_object_or_404(Filter, pk=pk)
    return render(request, "filters/filter_detail.html", {"filter": filter_instance})

@login_required
def filter_create(request):
    if request.method == 'POST':
        form = FilterForm(request.POST)

        unique_code = request.POST.get('unique_code', '')

        if Filter.objects.filter(unique_code=unique_code).exists():
                return render(request, 'filters/filter_form.html', {
                    'form': form,
                    'error_message': f'O código do filtro "{unique_code}" já está em uso.'
                })

        if form.is_valid():          

            filter_instance = form.save(commit=False)
            filter_instance.user = request.user
            filter_instance.save()
            
            for file in request.FILES.getlist('mass_initial_images'):
                image = Image.objects.create(file=file)
                filter_instance.mass_initial_images.add(image)

            for file in request.FILES.getlist('mass_final_images'):
                image = Image.objects.create(file=file)
                filter_instance.mass_final_images.add(image)

            return redirect('index')
    else:
        form = FilterForm()
    return render(request, 'filters/filter_form.html', {'form': form})

@login_required
def filter_edit(request, pk):
    filter_instance = get_object_or_404(Filter, pk=pk)
    if request.method == 'POST':
        form = FilterForm(request.POST, instance=filter_instance)
        if form.is_valid():
            form.save()

            
            for file in request.FILES.getlist('mass_initial_images'):
                image = Image.objects.create(file=file)
                filter_instance.mass_initial_images.add(image)
            
            
            for file in request.FILES.getlist('mass_final_images'):
                image = Image.objects.create(file=file)
                filter_instance.mass_final_images.add(image)

            return redirect('filter_detail', pk=pk)
    else:
        form = FilterForm(instance=filter_instance)
        mass_initial_images = [
            {'id': img.id, 'url': img.file.url} for img in filter_instance.mass_initial_images.all()
        ]
        mass_final_images = [
            {'id': img.id, 'url': img.file.url} for img in filter_instance.mass_final_images.all()
        ]
    return render(request, 'filters/filter_edit.html', {
        'form': form,
        'filter_instance': filter_instance,
        'mass_initial_images': mass_initial_images,
        'mass_final_images': mass_final_images
    })

@login_required
def filter_delete(request, pk):
    filter_instance = get_object_or_404(Filter, pk=pk)
    if request.method == 'POST':
        filter_instance.delete()
        return redirect('filter_list')
    return redirect('filter_list')

@login_required
def export_filter_pdf(request, pk):
    try:

        filter_instance = Filter.objects.get(id=pk)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filter_instance.unique_code}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['BodyText']

        # Título do PDF
        elements.append(Paragraph(f"Detalhes do Filtro - {filter_instance.unique_code}", title_style))
        elements.append(Spacer(1, 0.5 * inch))
        
        # Detalhes do filtro
        elements.append(Paragraph(f"Localização: {filter_instance.location}", normal_style))
        elements.append(Paragraph(f"Data Cadastro: {filter_instance.sync_date}", normal_style))
        elements.append(Spacer(1, 0.5 * inch))
        
        # Imagens de massa inicial
        elements.append(Paragraph("Imagens Iniciais:", styles['Heading2']))
        for image in filter_instance.mass_initial_images.all():
            img_path = image.file.path
            elements.append(Image(img_path, width=2 * inch, height=2 * inch))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Imagens de massa final
        elements.append(Paragraph("Imagens Finais:", styles['Heading2']))
        for image in filter_instance.mass_final_images.all():
            img_path = image.file.path
            elements.append(Image(img_path, width=2 * inch, height=2 * inch))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Geração do PDF
        doc.build(elements)
        return response

    except Filter.DoesNotExist:
        return HttpResponse("Filter not found", status=404)