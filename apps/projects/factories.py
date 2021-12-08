import factory
from faker import Faker

from . import models

fake = Faker(['fr'])


class AlternativeFactory(factory.django.DjangoModelFactory):
    content = factory.LazyFunction(fake.paragraph)
    proposition = factory.Iterator(models.Proposition.objects.all())
    created_by = factory.Iterator(models.User.objects.all())

    class Meta:
        model = models.Alternative


class PropositionFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(fake.catch_phrase)
    project = factory.Iterator(models.Project.objects.all())
    created_by = factory.Iterator(models.User.objects.all())

    class Meta:
        model = models.Proposition


class ProjectFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(fake.catch_phrase)
    description = factory.LazyFunction(fake.paragraph)
    created_by = factory.Iterator(models.User.objects.all())

    class Meta:
        model = models.Project
