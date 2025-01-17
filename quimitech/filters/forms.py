from django import forms
from .models import Filter, Image
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': 'Nome de Usuário',
            'password1': 'Senha',
            'password2': 'Confirmação de Senha', 
        }
        help_texts = {
            'username': 'Obrigatório. 150 caracteres ou menos. Apenas letras, números e @/./+/-/_',
            'password1': 'Sua senha deve ter pelo menos 8 caracteres, não ser totalmente numérica e não ser muito comum.',
            'password2': 'Insira a mesma senha para confirmação.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = self.Meta.help_texts.get(field_name, field.help_text)
            

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file']

class FilterForm(forms.ModelForm):
    class Meta:
        model = Filter
        fields = ['unique_code', 'location']
        widgets = {
            'unique_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código do Filtro'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Localização'
            })
        }   