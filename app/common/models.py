from django.db import models

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('생성일',auto_now_add=True)
    updated_at = models.DateTimeField('수정일',auto_now=True)

    class Meta:
        abstract = True