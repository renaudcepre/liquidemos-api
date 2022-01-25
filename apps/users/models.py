from django.apps import apps
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def vote_weight(self, tag):
        """Gives the number of votes delegated to this user for a specific tag. """
        # OPTPOS
        delegation_model = apps.get_model("apps.projects.models.Delegation")
        return len(delegation_model.get_delegations(self, tag)) + 1
