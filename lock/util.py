from lock.models import Lock, LockCard, Card


def get_locks_context(user, error=''):
    locks = Lock.objects.filter(user=user)

    locks_list = []
    for lock in locks:
        used_cards = LockCard.objects.filter(lock=lock).values_list('card__card_holder_id', flat=True)

        used_cards_list = []
        for card in used_cards:
            card_holder_id = convert_card_number_to_str(card)
            used_cards_list.append({"card_id": card_holder_id})

        locks_list.append({"user_name": lock.user.get_full_name(), "lock_name": lock.name,
                           "total": len(LockCard.objects.filter(lock=lock)), 'used_cards': used_cards_list})

    lock_length = len(locks_list)
    if lock_length == 0:
        lock_count = 'You have no locks.'
    else:
        lock_count = 'You have ' + str(lock_length) + ' locks' + \
                     (', and can\'t have more than ' + str(lock_length) + ' locks.' if lock_length == 2 else '.')

    return {"locks": locks_list, "lock_count": lock_count, "error": error}


def get_cards_context(user, error='', condition=False):
    if condition:
        locks = Lock.objects.filter(user=user)
        lock_cards = LockCard.objects.filter(lock__in=locks)
        remaining_cards = Card.objects.exclude(card_holder_id__in=list(lock_cards.values_list('card__card_holder_id',
                                                                                              flat=True)))
    else:
        remaining_cards = Card.objects.filter(user=user)

    remaining_cards_list = []
    for card in remaining_cards:
        card_holder_id = convert_card_number_to_str(card.card_holder_id)
        remaining_cards_list.append({"card_id": card_holder_id, "card_holder_name": card.card_holder_name,
                                     "access_level": card.access_level.capitalize()})

    card_length = len(remaining_cards_list)
    if card_length == 0:
        card_count = 'You have no cards.'
    else:
        card_count = 'You have ' + str(card_length) + ' cards' + \
                     (', and can\'t have more than ' + str(card_length) + ' cards.' if card_length == 5 else '.')

    return {"cards": remaining_cards_list, "card_count": card_count, "error": error}


def convert_card_str_to_number(card_id_str):
    card_id = card_id_str.split(" ")
    return int("".join(card_id))


def convert_card_number_to_str(card_holder_id):
    card_id_str = ''
    card_id_num = card_holder_id

    for divider in range(12, -1, -4):
        four_digits = str(card_id_num // pow(10, divider))
        if len(four_digits) < 4:
            four_digits = '0' * (4 - len(four_digits)) + four_digits

        card_id_str += four_digits + ' '
        card_id_num %= pow(10, divider)

    return card_id_str
