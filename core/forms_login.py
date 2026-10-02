from django import forms
from django.contrib.auth.forms import AuthenticationForm


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = 'Selecione uma opção'
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css
            if self.is_bound and name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'
                field.widget.attrs['aria-invalid'] = 'true'


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass
