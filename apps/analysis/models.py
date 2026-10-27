# from celery import uuid
import uuid

from django.db import models
from django.contrib.gis.db import models as gis_models
from apps.master_data.models import Commodity
from apps.spatial.models import MasterLayer

# Create your models here.
# models/analysis_result.py
class SuitabilityAnalysisResult(gis_models.Model):
    analysis_id = models.UUIDField(default=uuid.uuid4)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    base_layer = models.ForeignKey(MasterLayer, on_delete=models.CASCADE)
    geometry = gis_models.GeometryField(srid=4326)
    suitability_class = models.CharField(max_length=2)
    suitability_score = models.IntegerField()
    limiting_factors = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['analysis_id']),
            models.Index(fields=['commodity', 'suitability_class']),
        ]