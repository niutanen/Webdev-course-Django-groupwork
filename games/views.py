from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import json
from gameshop.models import Games, Payments, Gamestate, player, Developer
from gameshop.forms import gameform, signupform

def games(request):
    page={}
    if is_developer(request):
        page['developer'] = 'developer'
    allGames = Games.objects.all().order_by('name')
    if request.user.is_authenticated:
        boughtGames = Gamestate.objects.filter(uid=request.user)
        for boGame in boughtGames:
            allGames= allGames.exclude(id=boGame.gameid.id )
        page['bought_games'] = boughtGames
    page['games'] = allGames
    page["title"]="Games"
    return render(request,"games/games.html", page)

# Edit game reuses the form from add game. Could be joned with the addgame view aswell
@login_required
def editgame(request, gameid):
    page={}
    if is_developer(request):
        page['developer'] = 'developer'
    # Handling POST requests
    currentGame = get_object_or_404(Games, id=gameid);
    #gets the game from database and checks if they own it
    if(currentGame.owner == request.user):
         if request.method == 'POST':
             form = gameform(request.POST)
             if form.is_valid():
                 form_name = form.cleaned_data['name']
                 form_link = form.cleaned_data['link']
                 form_description = form.cleaned_data['description']
                 form_Hscore = form.cleaned_data['highscore']
                 form_price = form.cleaned_data['price']
                 form_tags = form.cleaned_data['tags']
                 if request.user.is_authenticated:
                     # Edits the game in the database and saves it
                     currentGame.name = form_name
                     currentGame.link = form_link
                     currentGame.deiscription = form_description
                     currentGame.highscore = form_Hscore
                     currentGame.price = form_price
                     currentGame.tags = form_tags
                     currentGame.save()
                     return HttpResponseRedirect('/games')
             else:
                 return redirect('home')
         # Handling get request and any other requests
         else:
           #creating the form from the gameform class with the information fo the current game
           form = gameform(instance=currentGame)
           page["title"]="Add Game"
           page["form"] =  form
           return render(request,"games/addgame.html", page)
    else:
        return HttpResponse('You do not have the rights to this game.')

#helping function for finding the developer developer

def is_developer(request):
    if request.user.groups.filter(name="developers").count() != 0:
        return True
    else:
        return False

# Adding new game
@login_required
def addgame(request):
    page = {}
    if is_developer(request):
        page['developer'] = 'developer'
        # Handling POST requests
        if request.method == 'POST':
            form = gameform(request.POST)
            if form.is_valid():
                form_name = form.cleaned_data['name']
                form_link = form.cleaned_data['link']
                form_description = form.cleaned_data['description']
                form_price = form.cleaned_data['price']
                form_tags = form.cleaned_data['tags']
            if request.user.is_authenticated:
                #adding the game to the DB.
                saving_all = Games(link=form_link, name = form_name, description = form_description, price=form_price, tags = form_tags, owner=request.user)
                saving_all.save()
                return HttpResponseRedirect('/games')
        # Handling get request and any other requests
        else:
            #creating the form from the gameform class
            form = gameform()
            page["title"]="Add Game"
            page["form"] =  form
            return render(request,"games/addgame.html", page)
    else:
        return redirect("home")

@login_required(login_url='login')
def delete_game(request, gameid):
    # page={}
    # if is_developer(request):
    #     page['developer'] = 'developer'
    # # Handling get requests
    # if request.method == 'GET':
    #     if request.user.is_authenticated and is_developer(request):
    #         currentGame = get_object_or_404(Games, id=gameid);
    #         if(currentGame.owner == request.user):
    #             Games.objects.filter(id=gameid).delete()
    #             return HttpResponseRedirect('/profile')


    pass


    #              if request.user.is_authenticated:
    #                  # Edits the game in the database and saves it
    #                  currentGame.name = form_name
    #                  currentGame.link = form_link
    #                  currentGame.deiscription = form_description
    #                  currentGame.highscore = form_Hscore
    #                  currentGame.price = form_price
    #                  currentGame.tags = form_tags
    #                  currentGame.save()
    #                  return HttpResponseRedirect('/games')
    #         else:
    #              return redirect('home')
    pass




# test this out with real users with http://127.0.0.1:8000/games/playgame/1 (or 1 or 2)
@login_required(login_url='login')
def playgame(request, gameid):
    page={}
    isgame = Games.objects.filter(id=gameid).exists()
    isplayer = player.objects.filter(user=request.user).exists()
    if not Games.objects.filter(id=gameid).exists():
        return redirect('games_list')
    game = Games.objects.get(id=gameid)
    isgamestate = Gamestate.objects.filter(uid=request.user, gameid=game)
    if isplayer and isgame and isgamestate:
        gs =get_object_or_404(Gamestate, uid=request.user, gameid=game)
        page["title"]="Play Game: " + game.name
        if request.is_ajax() or request.method == 'POST':
            playerObj = json.loads(request.POST.get('values'))
            if playerObj['messageType'] == 'LOAD_REQUEST':
                loadpkg = {}
                loadpkg['messageType']= "LOAD"
                loadpkg['gameState']= gs.gamestate
                return JsonResponse(loadpkg)
            elif playerObj['messageType'] == 'SCORE':
                gs.score = playerObj['score']
                gs.save()
                #set new global highscore
                if (game.highscore<gs.score):
                    game.highscore=gs.score
                    game.save()
                    return HttpResponse('You got the new global highscore')
                return HttpResponse('Score submitted:  ' +str(gs.score))
            elif playerObj['messageType'] == 'SAVE':
                gs.gamestate = playerObj['gameState']
                gs.save()
                return HttpResponse('Your gamestate was saved')
            elif playerObj['messageType'] == 'ERROR':
                text= playerObj['error']
                return HttpResponse("error" + text)
            elif playerObj['messageType'] == 'SETTING':
                gs.options = playerObj["options"]
                gs.save();
                return HttpResponse("Options  " +  gs.options)
            else:
                return HttpResponse('You should not be playing this game')
        page['link']= game.link
        page['gameid'] = gameid
        page['highscore'] = game.highscore
        return render(request,"games/playgame.html", page)
    elif not isplayer:
        messages.add_message(request, messages.SUCCESS, 'You must be a player to play games.')
        return redirect('login')
    elif isplayer:
        messages.add_message(request, messages.SUCCESS, 'You must own the game to play it.')
        return redirect('home')



# highscores retrieves all the games from the database and returns the scores to be rendered
def highscores(request):
    page={}
    if is_developer(request):
        page['developer'] = 'developer'
    page["title"]="Highscores"
    allGames = Games.objects.all().order_by('name')
    showgames =[]
    allhighscores = Gamestate.objects.all()
    for game in allGames:
        gamescores = allhighscores.filter(gameid=game).order_by('-score')
        scorelist =  []
        try:
            for i in range(5):
                playerscore = dict()
                playerscore['name'] = gamescores[i].uid.username
                playerscore['score'] = gamescores[i].score
                scorelist.append(playerscore)
        except IndexError:
            pass
        showscores={}
        showscores['name'] = game.name
        showscores['highscores']=scorelist
        showscores['owner']= game.owner.username
        showgames.append(showscores)
    page['games'] = showgames
    return render(request,"games/highscores.html", page)
