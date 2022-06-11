import random, json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Create your views here.
from lock.models import Lock, Card, LockCard


def index(request):
    if not request.user.is_authenticated:
        return redirect("user:login")
    return render(request, 'lock/index.html')


@login_required
def create_card(request):
    if request.method == "POST":
        access_level = request.POST.get("access").lower()
        while True:
            card_id = random.randint(pow(10, 15), pow(10, 16) - 1)
            if not Card.objects.filter(card_holder_id=card_id).exists():
                break

        try:
            card = Card.objects.create(card_holder_id=card_id, user=request.user,
                                   card_holder_name=request.user.get_full_name(),
                                   access_level=access_level)
            card.save()
        except IntegrityError:
            return JsonResponse({"error": "You already have a card with this access level."})
        return redirect("lock:cards")

    return redirect("lock:cards")


@login_required
def create_lock(request):
    if request.method == "POST":
        lock_name = request.POST.get("lock_name")

        if lock_name == "":
            return get_locks(request, error="Lock name cannot be empty.")

        try:
            lock = Lock.objects.create(name=lock_name, user=request.user)
            lock.save()
        except IntegrityError:
            return get_locks(request, error="Lock name already exists.")

    return redirect("lock:locks")


def convert_card_number(card_id_str):
    card_id = card_id_str.split(" ")
    return int("".join(card_id))


@login_required
def assign_card_to_lock(request, lock_name):
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        card_number = convert_card_number(card_number)

        lock = Lock.objects.get(name=lock_name)
        card = Card.objects.get(card_holder_id=card_number)

        try:
            lock_card = LockCard.objects.create(card=card, lock=lock)
            lock_card.save()
        except ValidationError:
            return redirect('lock:locks')
        return redirect('lock:locks')

    return redirect('lock:locks')


@login_required
def remove_card(request, card_number):
    if request.method == "POST":
        card = Card.objects.get(card_holder_id=convert_card_number(card_number))
        card.delete()

    return redirect("lock:cards")


@login_required
def remove_lock(request, lock_name):
    if request.method == "POST":
        try:
            lock = Lock.objects.get(name=lock_name)
            lock.delete()
        except Lock.DoesNotExist:
            return JsonResponse({"error": "Lock does not exist."}, status=400)

    return redirect("lock:locks")


@login_required
def remove_assigned_card(request):
    if request.method == "DELETE":
        received_data = json.loads(request.body)
        card_id = received_data["card_id"]
        lock_id = received_data["lock_id"]

        try:
            lock_card = LockCard.objects.get(card_id=card_id, lock_id=lock_id)
            lock_card.delete()
        except LockCard.DoesNotExist:
            return JsonResponse({"error": "Card does not exist."}, status=400)
        return JsonResponse({"success": "Card removed successfully."}, status=204)

    return JsonResponse({"error": "Method not allowed."}, status=400)


def get_cards_context(user, error='', condition=False):
    if condition:
        locks = Lock.objects.filter(user=user)
        lock_cards = LockCard.objects.filter(lock__in=locks)
        cards = Card.objects.exclude(card_holder_id__in=list(lock_cards.values_list('card__card_holder_id', flat=True)))
    else:
        cards = Card.objects.filter(user=user)

    cards_list = []
    for card in cards:
        card_id_str = ''
        card_id_num = card.card_holder_id

        for divider in range(12, -1, -4):
            four_digits = str(card_id_num // pow(10, divider))
            if len(four_digits) < 4:
                four_digits = '0' * (4 - len(four_digits)) + four_digits

            card_id_str += four_digits + ' '
            card_id_num %= pow(10, divider)

        cards_list.append({"card_id": card_id_str, "card_holder_name": card.card_holder_name,
                           "access_level": card.access_level.capitalize()})

    card_length = len(cards_list)
    if card_length == 0:
        card_count = 'You have no cards.'
    else:
        card_count = 'You have ' + str(card_length) + ' cards' + \
                     (', and can\'t have more than ' + str(card_length) + ' cards.' if card_length == 5 else '.')

    return {"cards": cards_list, "card_count": card_count, "error": error}


@login_required
def get_cards(request):
    context = get_cards_context(request.user, error='')
    return render(request, 'lock/cards.html', context=context, status=200)


def get_locks_context(user, error=''):
    locks = Lock.objects.filter(user=user)
    locks_list = []
    for lock in locks:
        locks_list.append({"user_name": lock.user.get_full_name(), "lock_name": lock.name,
                           "total": len(LockCard.objects.filter(lock=lock))})

    lock_length = len(locks_list)
    if lock_length == 0:
        lock_count = 'You have no locks.'
    else:
        lock_count = 'You have ' + str(lock_length) + ' locks' + \
                     (', and can\'t have more than ' + str(lock_length) + ' locks.' if lock_length == 2 else '.')

    return {"locks": locks_list, "lock_count": lock_count, "error": error}


@login_required
def get_locks(request, error='', condition=True):
    locks_context = get_locks_context(request.user)
    cards_context = get_cards_context(request.user, condition=condition)
    context = {**locks_context, **cards_context}

    return render(request, 'lock/locks.html', context=context, status=200)
