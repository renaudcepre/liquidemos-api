from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.projects.models import Vote, Delegation


def get_votes_to_update(vote):
    delegations = vote.user.delegation_chain(vote.project, 'out')
    delegates = [d.delegate for d in delegations]
    return Vote.objects.filter(user__in=delegates, project=vote.project)


@receiver(post_save, sender=Vote)
def update_delegates_votes(sender, instance, created, **kwargs):
    """
    When a user votes for a project, all votes made by users who have been
    delegated for the topic of that project lose the weight of the vote of
    the user who voted.
    """
    if created:
        votes = get_votes_to_update(instance)
        for vote in votes:
            vote.weight -= instance.weight
        sender.objects.bulk_update(votes, fields=('weight',))


@receiver(post_delete, sender=Vote)
def update_delegates_votes_on_vote(sender, instance, **kwargs):
    votes = get_votes_to_update(instance)
    for vote in votes:
        vote.weight += instance.weight
    sender.objects.bulk_update(votes, fields=('weight',))


@receiver((post_delete, post_save), sender=Delegation)
def update_delegates_vote_on_delegation(instance, **kwargs):
    delegations = instance.delegate.delegation_chain(target=instance.theme,
                                                     direction='out')
    delegates = [d.delegate for d in delegations]

    votes = Vote.objects.filter(user__in=delegates,
                                project__theme=instance.theme)

    for vote in votes:
        vote.weight = vote.user.vote_weight(vote.project)
    Vote.objects.bulk_update(votes, fields=('weight',))
