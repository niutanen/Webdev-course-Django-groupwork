from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from gameshop.models import Games, Payments, Gamestate, player, Developer
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib import messages
from hashlib import md5

'''
Feedback from Ahmed Beder:
Payment MODEL
The ‘state’ field would be useful.
It will be helpful to identify if the payment was cancelled, received or still in process.
I would recommend to add a unique secure payment_id field for security reasons.
This could be used to identify the payment and prevent fraud.
For the state of payment consider using enums.


Make sure you test this properly.
Most projects have security holes that reduce points.
 Make sure that you can't reuse payments, pay for something else you selected etc.
 All-in-all try to break your own product!
'''
def back_home(request):
    return redirect('home')

def payment(request,game_id=-1):
    if game_id == -1:
        return redirect('games_list')
    try:
        int(game_id)
    except Exception as e:
        return redirect('games_list')
    if request.method == "GET":
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        if user.groups.filter(name="developers").count() != 0:
                messages.add_message(request, messages.INFO, 'You must be a player to buy games!')
                return redirect("home")
        game = get_object_or_404(Games, id=game_id)
        sid = "ontija"
        secret_key = "301afa56fe812670d268dc6e9c200ca9"
        pid = 'ontija' + get_random_string(8,'0123456789') + "something"
        amount = game.price
        success = request.build_absolute_uri(reverse('payment_success'))+"/?id_game={}".format(game_id)
        cancel =  request.build_absolute_uri(reverse('payment_cancel'))+"/?id_game={}".format(game_id) #"http://localhost:8000/payment/cancel"
        error =  request.build_absolute_uri(reverse('payment_error'))+"/?id_game={}".format(game_id) #"http://localhost:8000/payment/error"
        checksumstr = "pid={}&sid={}&amount={}&token={}".format(pid,sid,amount,secret_key)
        md5_digest =  md5(checksumstr.encode("ascii"))
        checksum = md5_digest.hexdigest()
        url="http://payments.webcourse.niksula.hut.fi/pay/"
        transaction = Payments.objects.filter(user_id=user.id, game=game.id, state="success")
        if transaction.count() != 0:
            messages.add_message(request, messages.INFO, 'You have already bought this game, Enjoy Playing it!')
            return redirect(reverse('game_play_basic')+str(game_id))

        return render(request,"payments/request.html",{"game":game, "url":url, "pid":pid, "sid":sid, "amount":amount, "success":success, "cancel":cancel, "error":error, "checksum":checksum})
    else:
        return HttpResponse(status=500)


def success(request):
    if request.method == "GET":
        user = request.user
        if not user.is_authenticated:
            return redirect("shop:login")
        if user.groups.filter(name="developers").count() != 0:
            return redirect("login")
        game_id= int(request.GET["id_game"])
        game = get_object_or_404(Games, id=game_id)
        secret_key = "301afa56fe812670d268dc6e9c200ca9"
        pid=request.GET["pid"]
        ref=request.GET["ref"]
        result=request.GET["result"]
        checksum=request.GET["checksum"]
        checksumstr = "pid={}&ref={}&result={}&token={}".format(pid,ref,result,secret_key)
        digest =  md5(checksumstr.encode("ascii"))
        calculated_hash = digest.hexdigest()
        if calculated_hash == checksum:
            if Payments.objects.filter(payment_id = pid).exists():
                return redirect('games_list')
            Payments.objects.create (payment_id = pid, game=game, user=user , price = game.price, state="success", date=timezone.now()).save()
            game = Games.objects.get(id=game_id)
            a = Gamestate(uid=user, gameid=game)
            a.save()
            messages.add_message(request, messages.SUCCESS, 'Thank you for buying this game, enjoy playing!')
            return redirect(reverse('game_play_basic')+str(game_id))
        else:
            return HttpResponse(status = 500)
    return HttpResponse(status = 500)

def payment_cancel(request):
    if request.method == "GET":
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        if user.groups.filter(name="developers").count() != 0:
            messages.add_message(request, messages.ERROR, 'Your payment failed, please try again!')
            return redirect("home")
        game_id= int(request.GET["id_game"])
        game = get_object_or_404(Games, id=game_id)
        secret_key = "301afa56fe812670d268dc6e9c200ca9"
        pid=request.GET["pid"]
        ref=request.GET["ref"]
        result=request.GET["result"]
        checksum=request.GET["checksum"]
        checksumstr = "pid={}&ref={}&result={}&token={}".format(pid,ref,result,secret_key)
        digest =  md5(checksumstr.encode("ascii"))
        calculated_hash = digest.hexdigest()
        if calculated_hash == checksum:
            if Payments.objects.filter(payment_id = pid).exists():
                return redirect('games_list')
            Payments.objects.create (payment_id = pid, game=game, user=user , price = game.price, state="fail", date=timezone.now()).save()
            messages.add_message(request, messages.ERROR, 'Sorry The payment was cancelled')
            return redirect("games_list")
        else:
            return HttpResponse(status = 500)
    return HttpResponse(status = 500)

def error(request):
    if request.method == "GET":
        user = request.user
        if not user.is_authenticated:
            messages.add_message(request, messages.ERROR, 'Please login First')
            return redirect("login")
        if user.groups.filter(name="developers").count() != 0:
            messages.add_message(request, messages.ERROR, 'Sorry please create a player account to be able to play the game')
            return redirect("home")
        secret_key = "301afa56fe812670d268dc6e9c200ca9"
        pid=request.GET["pid"]
        ref=request.GET["ref"]
        result=request.GET["result"]
        checksum=request.GET["checksum"]
        checksumstr = "pid={}&ref={}&result={}&token={}".format(pid,ref,result,secret_key)
        digest =  md5(checksumstr.encode("ascii"))
        calculated_hash = digest.hexdigest()
        if calculated_hash == checksum:
            if Payments.objects.filter(payment_id = pid).exists():
                return redirect('games_list')
            Payments.objects.create (payment_id = pid, game=game, user=user , price = game.price, state="fail", date=timezone.now()).save()
            messages.add_message(request, messages.ERROR, 'Sorry Some error happened, please try again later.')
            return redirect("home")
        else:
            return HttpResponse(status = 500)
    return HttpResponse(status = 500)
