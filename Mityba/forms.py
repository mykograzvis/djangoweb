from django import forms
from homepage.models import Valgymai, Product, Receptai

class ValgymasForm(forms.ModelForm):
    produktai = forms.ModelMultipleChoiceField(queryset=Product.objects.all(), required=False)
    receptai = forms.ModelMultipleChoiceField(queryset=Receptai.objects.all(), required=False)

    class Meta:
        model = Valgymai
        fields = ('tipas',)
        widgets = {
            'tipas': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ValgymasForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['produktai'].initial = self.instance.produktai.all()
            self.fields['receptai'].initial = self.instance.receptai.all()