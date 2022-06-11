import django_filters

from lock.models import Card


class CardFilter(django_filters.FilterSet):
    class Meta:
        model = Card
        fields = ['card_holder_id', 'card_holder_name', 'access_level']
