from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

from apps.commons.utils.model_mixins import DatedModelMixin
from apps.users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"


class Project(DatedModelMixin, models.Model):
    name = models.CharField(max_length=64,
                            validators=[RegexValidator(r'^[a-zA-Z-1-9-_ ]*$')])
    description = models.TextField(blank=True)

    slug = models.SlugField(editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    # Un parent est considere comme dependance de son enfant par default
    parent = models.ForeignKey("Project", on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='childs')
    # Ne doivent pas etre un parent
    depends_on = models.ManyToManyField("Project",
                                        related_name='dependencies',
                                        blank=True)
    # Les alternatives doivent avoir le meme parent, et ne pas etre dependants
    # les unes des autres
    alternatives = models.ManyToManyField("Project", blank=True)

    @property
    def parents_number(self):
        """@return the number of projects that are parents of this one """
        count = 0
        project = self
        while project.parent is not None:
            count += 1
            project = project.parent
        return count

    @property
    def first_parent(self):
        """@return the older parent of this project"""
        project = self
        while project.parent is not None:
            project = project.parent
        return project

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if not self.parent:
            return f"{self.name}"
        parent_count = self.parents_number
        if parent_count == 1:
            return f"{self.parent.name}/{self.name}"
        return f"{self.first_parent.name}/.../{self.name}"
