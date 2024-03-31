from django import forms
from django.forms import ModelForm, RadioSelect

from operators.models import Operators


class OperatorAdminForm(ModelForm):

    class Meta:
        model = Operators
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "phone",
            "gender",
        ]
        # widgets = {
        #     "payment_method": RadioSelect(),
        # }

    # def __init__(self, *args, **kwargs):
    #     instance = kwargs.get('instance')
    #     initial = {}

        # if instance:
        #     customer_full_name_split = instance.customer_full_name.split(" ", maxsplit=1)
        #     initial = {
        #         "first_name": customer_full_name_split[0],
        #         "last_name": customer_full_name_split[1],
        #     }
        #
        # super().__init__(*args, **kwargs, initial=initial)

    def save(self, commit=True):
        self.instance.role = "operator"
        return super().save(commit)