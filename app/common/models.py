from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField("생성일", default=timezone.now)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        abstract = True
