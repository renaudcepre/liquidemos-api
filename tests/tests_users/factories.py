import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    password = factory.PostGenerationMethodCall('set_password', 'test')
    email = factory.Faker('email')
    username = factory.Faker('user_name')
