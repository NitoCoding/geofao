from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from sqids import Sqids


# Import library pihak ketiga
from safedelete.models import SafeDeleteModel, SOFT_DELETE, SOFT_DELETE_CASCADE
from crum import get_current_user
# Import opsional (install jika butuh):
# from concurrency.fields import IntegerVersionField
# from concurrency.api import concurrency_disable_increment
# from simple_history.models import HistoricalRecords

_sqids = Sqids(
    alphabet=getattr(settings, 'SQIDS_ALPHABET', "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"),
    min_length=getattr(settings, 'SQIDS_MIN_LENGTH', 8),
)

# ==============================================================================
# 1. MIXINS (Fondasi Fitur)
# ==============================================================================

class StatusMixin(models.Model):
    """Mixin untuk status aktif/non-aktif (soft delete support)"""
    
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self):
        self.is_active = True
        self.save(update_fields=['is_active'])

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")

    class Meta:
        abstract = True
        ordering = ['-created_at']

class UserTrackingMixin(models.Model):
    """Mixin untuk user tracking otomatis"""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, # Tetap null=True untuk antisipasi background task (Celery)
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name="Dibuat Oleh"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name="Diperbarui Oleh"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # 1. Ambil user yang sedang melakukan request dari middleware
        user = get_current_user()
        
        # 2. Pastikan user valid (bukan AnonymousUser)
        if user and not user.is_anonymous:
            # Jika ini adalah record baru (belum punya Primary Key)
            if not self.pk:
                self.created_by = user
            
            # Selalu update user yang terakhir mengubah (termasuk saat soft delete)
            self.updated_by = user

            update_fields = kwargs.get('update_fields')
            if update_fields and 'updated_by' not in update_fields:
                kwargs['update_fields'] = list(update_fields) + ['updated_by']

        # 3. Lanjutkan proses save bawaan Django
        super().save(*args, **kwargs)

class PublicIdMixin(models.Model):
    class Meta:
        abstract = True

    @property
    def public_id(self) -> str:
        content_type = ContentType.objects.get_for_model(self)
        return _sqids.encode([self.pk, content_type.id])

    @classmethod
    def get_by_public_id(cls, public_id: str, include_deleted: bool = False):
        """
        PERBAIKAN: Tambahkan include_deleted agar Admin/Restore bisa mengakses data yang di-soft delete.
        """
        try:
            decoded = _sqids.decode(public_id)
            if not decoded:
                raise ValidationError("Format public ID tidak valid")

            pk = decoded[0]
            
            if len(decoded) == 2:
                content_type_id = decoded[1]
                expected_content_type = ContentType.objects.get_for_model(cls)
                if content_type_id != expected_content_type.id:
                    raise ValidationError(f"Public ID ini bukan untuk model '{cls._meta.model_name}'")

            # Gunakan all_objects jika ingin mengambil data yang sudah di-soft delete
            manager = cls.all_objects if include_deleted else cls.objects
            return manager.get(pk=pk)

        except ObjectDoesNotExist:
            raise ValidationError(f"{cls.__name__} dengan public ID tersebut tidak ditemukan.")
        except (ValueError, ContentType.DoesNotExist) as e:
            raise ValidationError(f"Invalid public ID: {str(e)}")

    @classmethod
    def filter_by_public_ids(cls, public_ids: list, include_deleted: bool = False):
        pks = []
        expected_content_type = ContentType.objects.get_for_model(cls)
        for public_id in public_ids:
            try:
                decoded = _sqids.decode(public_id)
                if decoded: 
                    pks.append(decoded[0])
                
                # Validasi content type jika ID mengandung 2 nilai
                if len(decoded) == 2:
                    if decoded[1] != expected_content_type.id:  # ← pakai di sini
                        continue  # Skip ID dari model lain
            except ValueError:
                continue # Skip ID yang invalid
        
        manager = cls.all_objects if include_deleted else cls.objects
        return manager.filter(pk__in=pks)


# ==============================================================================
# ABSTRACT USER CUSTOM
# ==============================================================================

class AbstractBaseUser(TimeStampMixin, PublicIdMixin, AbstractUser):
    """
    Base user model dengan:
    - Timestamp (created_at, updated_at)
    - Public ID untuk URL/API
    - TANPA soft delete (GDPR compliance)
    - TANPA user tracking (self-referential)
    """
    
    class Meta:
        abstract = True


# ==============================================================================
# 1. TIER 1: STANDARD BASE MODEL (Untuk 100% Model Biasa)
# ==============================================================================

class BaseModel(TimeStampMixin, UserTrackingMixin, PublicIdMixin, StatusMixin):
    """
    Base model standar. Aman, memiliki soft delete, tracking, dan public ID.
    Cocok untuk: Master Data, Kategori, Profil, Konfigurasi.
    """

    class Meta:
        abstract = True


# ==============================================================================
# 2. TIER 2: SOFT DELETE BASE MODEL (Untuk 80% Model Biasa)
# ==============================================================================

class SoftDeleteBaseModel(SafeDeleteModel, TimeStampMixin, UserTrackingMixin, PublicIdMixin):
    """
    Base model standar. Aman, memiliki soft delete, tracking, dan public ID.
    Cocok untuk: Master Data, Kategori, Profil, Konfigurasi.
    """
    # SOFT_DELETE: Hanya menandai dihapus. 
    # Gunakan SOFT_DELETE_CASCADE hanya jika Anda YAKIN ingin anak-anaknya ikut terhapus secara soft.
    _safedelete_policy = SOFT_DELETE 

    class Meta:
        abstract = True


# ==============================================================================
# 3. TIER 3: FINANCIAL / CRITICAL BASE MODEL (Untuk 20% Model Kritis)
# ==============================================================================

class FinancialBaseModel(SoftDeleteBaseModel, StatusMixin):
    """
    Base model khusus untuk data finansial (Transaksi, Saldo, Ledger, Harga).
    Menambahkan Optimistic Locking (Concurrency) dan Audit Trail (History).
    """
    # 1. Tambahkan Concurrency (Optimistic Locking)
    # version = IntegerVersionField() 
    
    # 2. Tambahkan History (Audit Trail)
    # history = HistoricalRecords()

    class Meta:
        abstract = True

    # --- OVERRIDE UNTUK MENANGANI CONCURRENCY SAAT SOFT DELETE ---
    # (Aktifkan bagian ini jika Anda meng-uncomment IntegerVersionField di atas)
    """
    def delete(self, using=None, keep_parents=False):
        # Mencegah nomor versi bertambah saat soft delete (mencegah false-positive conflict)
        with concurrency_disable_increment(self):
            return super().delete(using=using, keep_parents=keep_parents)

    def undelete(self):
        with concurrency_disable_increment(self):
            return super().undelete()
    """