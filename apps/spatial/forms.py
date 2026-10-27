from django import forms

from apps.master_data.models import DataYear
from .models import MasterLayer


class LayerUploadForm(forms.ModelForm):
    """
    Form untuk mengupload file shapefile (dalam format ZIP).
    """

    shapefile = forms.FileField(
        label="Pilih File Shapefile (ZIP)",
        help_text="Upload file ZIP yang berisi .shp, .shx, .dbf, dan .prj",
        widget=forms.FileInput(attrs={"accept": ".zip"}),
    )

    data_year = forms.ModelChoiceField(
        label="Tahun Data",
        help_text="Tahun ketika data dikumpulkan",
        required=False,
        queryset=DataYear.objects.filter(is_active=True).order_by("-year"),
        widget=forms.Select(
            attrs={
                "class": "select select-bordered w-full",
            }
        ),
        empty_label="Pilih Tahun",
    )

    layer_category = forms.ChoiceField(
        label="Kategori Layer",
        help_text="Pilih kategori layer",
        choices=MasterLayer.LAYER_CATEGORY_CHOICES,
        initial="lainnya",
        widget=forms.Select(
            attrs={
                "class": "select select-bordered w-full",
            }
        ),
    )

    class Meta:
        model = MasterLayer
        fields = ["name", "data_year", "layer_category"]
    

    def clean_shapefile(self):
        shapefile = self.cleaned_data["shapefile"]
        if shapefile:
            # Validasi ekstensi file
            if not shapefile.name.endswith(".zip"):
                raise forms.ValidationError("File harus berformat ZIP.")

            # Validasi ukuran file (maks 100MB)
            if shapefile.size > 100 * 1024 * 1024:
                raise forms.ValidationError("Ukuran file tidak boleh lebih dari 100MB.")

        return shapefile


class LayerEditForm(forms.ModelForm):
    """Form untuk mengedit metadata layer spasial."""

    layer_category = forms.ChoiceField(
        label="Kategori Layer",
        help_text="Pilih kategori layer",
        choices=MasterLayer.LAYER_CATEGORY_CHOICES,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )

    data_year = forms.ModelChoiceField(
        label="Tahun Data",
        help_text="Tahun ketika data dikumpulkan",
        required=False,
        queryset=DataYear.objects.filter(is_active=True).order_by("-year"),
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
        empty_label="Pilih Tahun",
    )

    class Meta:
        model = MasterLayer
        fields = ["name", "layer_category", "data_year"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Nama layer",
                }
            ),
        }
        labels = {
            "name": "Nama Layer",
            "layer_category": "Kategori Layer",
            "data_year": "Tahun Data",
        }

