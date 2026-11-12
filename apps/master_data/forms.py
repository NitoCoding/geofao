from django import forms

from apps.master_data.models import Commodity, CommodityGroup, DataYear, SuitabilityCharacteristic


class CommodityGroupForm(forms.ModelForm):
    class Meta:
        model = CommodityGroup
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Misal: Pangan",
                }
            )
        }


class CommodityForm(forms.ModelForm):
    class Meta:
        model = Commodity
        fields = ["name", "group", "suitability_table"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "group": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "suitability_table": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Misal: padi_suitability",
                }
            ),
        }


class SuitabilityCharacteristicForm(forms.ModelForm):
    class Meta:
        model = SuitabilityCharacteristic
        fields = [
            "commodity",
            "name",
            "source_field",
            "s1_value",
            "s2_value",
            "s3_value",
            "n_value",
            "data_type",
            "unit",
            "is_active",
        ]
        widgets = {
            "commodity": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Misal: pH Tanah",
                }
            ),
            "source_field": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Misal: PH_NILAI",
                }
            ),
            "s1_value": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "s2_value": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "s3_value": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "n_value": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "data_type": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "unit": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Misal: pH, cm",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["commodity"].disabled = True


class DataYearForm(forms.ModelForm):
    """Form untuk create/edit DataYear."""

    class Meta:
        model = DataYear
        fields = ["year", "name", "description", "is_active"]
        widgets = {
            "year": forms.NumberInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Misal: 2024",
            }),
            "name": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Misal: Data 2024",
            }),
            "description": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full h-20",
                "placeholder": "Deskripsi periode data...",
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
        }
        labels = {
            "year": "Tahun",
            "name": "Nama Periode",
            "description": "Deskripsi",
            "is_active": "Aktif",
        }
