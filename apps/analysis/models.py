# from celery import uuid
import uuid

from django.db import models
from django.contrib.gis.db import models as gis_models
from apps.master_data.models import Commodity
from apps.spatial.models import MasterLayer
