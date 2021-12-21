import logging

from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Length
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.users.models import User
from apps.commons.utils.mptree.models import MaterializedPathNodeModel

logger = logging.getLogger(__name__)

models.CharField.register_lookup(Length, 'length')


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Project(DatedModelMixin, MaterializedPathNodeModel):
    name = models.CharField(max_length=64,
                            validators=[RegexValidator(r'^[a-zA-Z-1-9-_ ]*$')])
    description = models.TextField(blank=True)
    slug = models.SlugField(editable=False)
    tags = models.ManyToManyField(Tag, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    depends_on = models.ManyToManyField("Project",
                                        related_name='dependencies',
                                        blank=True)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug
