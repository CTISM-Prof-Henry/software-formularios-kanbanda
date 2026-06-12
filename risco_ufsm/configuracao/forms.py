from django import forms
from .models import DesafioPDI, ObjetivoPDI, Macroprocesso

#aqui ficam informacoes que só dependem da ação do usuário

class DesafioPDIForm(forms.ModelForm):
    class Meta:
        model = DesafioPDI
        fields= ['numero', 'descricao', 'ativo']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ObjetivoPDIForm(forms.ModelForm):
    class Meta:
        model = ObjetivoPDI
        fields = ['desafio', 'codigo', 'descricao', 'ativo']
        widgets={
            'desafio': forms.Select(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MacroprocessoForm(forms.ModelForm):
    class Meta:
        model =Macroprocesso
        fields= ['nome', 'desafio', 'ativo']
        widgets={
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'desafio': forms.Select(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }