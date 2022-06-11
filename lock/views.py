import random

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Create your views here.
from lock.filters import CardFilter
from lock.models import Lock, Card, LockCard
from lock.util import convert_card_str_to_number, get_cards_context, get_locks_context


@login_required
def search(request):
    card_filter = CardFilter(request.GET, queryset=Card.objects.filter(user=request.user))
    return render(request, 'lock/search.html', {'filter': card_filter})


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


@login_required
def assign_card_to_lock(request, lock_name):
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        card_number = convert_card_str_to_number(card_number)

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
        card = Card.objects.get(card_holder_id=convert_card_str_to_number(card_number))
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
def remove_assigned_card(request, lock_name):
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        card_number = convert_card_str_to_number(card_number)

        lock = Lock.objects.get(name=lock_name)
        card = Card.objects.get(card_holder_id=card_number)

        try:
            lock_card = LockCard.objects.create(card=card, lock=lock)
            lock_card.delete()
        except ValidationError:
            return redirect('lock:locks')
        return redirect('lock:locks')

    return redirect('lock:locks')


@login_required
def get_cards(request):
    context = get_cards_context(request.user, error='')
    return render(request, 'lock/cards.html', context=context, status=200)


def get_locks(request, condition=True):
    if not request.user.is_authenticated:
        return redirect("user:login")
    locks_context = get_locks_context(request.user)
    cards_context = get_cards_context(request.user, condition=condition)
    context = {**locks_context, **cards_context}

    return render(request, 'lock/locks.html', context=context, status=200)
