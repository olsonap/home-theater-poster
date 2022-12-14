from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import time
from tmdbv3api import TMDb
from tmdbv3api import Movie
import requests
import shutil
import threading
import socket
from PIL import Image
from io import BytesIO
import json

from django_user_agents.utils import get_user_agent


tmdb = TMDb()
tmdb.api_key = '2b9f3ff3381ad78a6a295082cef2910d'
tmdb.language = 'en'
tmdb.debug = True
movie = Movie()
chosen_movie = None
movieID = None
poster_path = None
default = Image.open(r'static/default.jpeg')
resetposter = default.copy()
resetposter.save(r'static/poster.jpg')

# Login page
#def login(request):
#    print("Entering Index")
#    return render(request, "login.html")


def admin_login(request):
    print("Entering Index")
    if user_agent.is_mobile:
        print("IS MOBILE")
    return render(request, "registration/login.html")


@login_required
def index(request):
    user_agent = get_user_agent(request)

    global chosen_movie, movie
    print("Entering Index")
    if request.method == "POST":
        moviename = request.POST['moviename'].strip()
        if moviename:
            return redirect('make-selection', moviename=moviename)
        #return redirect('/make-selection/', moviename)
    if chosen_movie == None:
        if user_agent.is_mobile:
            return render(request, "index_mob.html", {'poster_path': '/static/default.jpeg'})
        return render(request, "index.html", {'poster_path': '/static/default.jpeg'})
    poster_path = f"http://image.tmdb.org/t/p/original{chosen_movie.poster_path}"
    if user_agent.is_mobile:
        return render(request, "index_mob.html", {'poster_path': poster_path})
    return render(request, "index.html", {'poster_path': poster_path})

@login_required
def selected(request, movieid):
    user_agent = get_user_agent(request)
    global chosen_movie
    global poster_path
    global movieID
    if request.method == "GET":
        chosen_movie = movie.details(movieid)
        #print(chosen_movie)
        movie_name = chosen_movie["original_title"]
        overview = chosen_movie["overview"]
        release_date = chosen_movie["release_date"]
        runtime = chosen_movie["runtime"]
        tmpvideos = chosen_movie["videos"]
        movieID = chosen_movie["id"]
        trailer_url = None
        trailer_exists = 'F'
        if tmpvideos:
            tmpresults = tmpvideos["results"]
            if tmpresults:
                youtubeKey = tmpresults[0]['key']
                trailer_exists = 'T'
                trailer_url = f"https://www.youtube.com/embed/{youtubeKey}"
                for video in tmpresults:
                    vidtype = video.get("type", None)
                    if vidtype.lower() in ["official trailer", "trailer"]:
                        youtubeKey = video['key']
                        trailer_exists = 'T'
                        trailer_url = f"https://www.youtube.com/embed/{youtubeKey}"
        poster_path = "http://image.tmdb.org/t/p/original" + chosen_movie.poster_path
        response = requests.get(poster_path)
        img = Image.open(BytesIO(response.content))
        img.save('static/poster.jpg')
        if user_agent.is_mobile:
            return render(request, "selected_mob.html", {'poster_path': poster_path,
                                                     'movie_name': movie_name,
                                                     'overview': overview,
                                                     'release_date': release_date,
                                                     'runtime': runtime,
                                                     'trailer_url': trailer_url,
                                                     'trailer_exists': trailer_exists
                                                     })
        return render(request, "selected.html", {'poster_path': poster_path,
                                                 'movie_name':movie_name,
                                                 'overview': overview,
                                                 'release_date':release_date,
                                                 'runtime': runtime,
                                                 'trailer_url': trailer_url,
                                                 'trailer_exists': trailer_exists
                                                 })

@login_required
def make_selection(request, moviename=None):
    user_agent = get_user_agent(request)

    global chosen_movie
    global movieID
    if request.method == "GET":
        print("GET : " + moviename)
        search = movie.search(moviename)
        search_results = []
        for result in search:
            movieID = result.id
            if result.get('release_date'):
                new_string = f"{result.title} | {result.release_date[0:4]}"
            else:
                new_string = f"{result.title}"
            poster_path = None
            if result.poster_path:
                poster_path = f"http://image.tmdb.org/t/p/original{result.poster_path}"
            search_results.append((new_string, poster_path, movieID))
        if chosen_movie == None:
            if user_agent.is_mobile:
                return render(request, "make_selection_mob.html",
                              {'search': search_results, 'searched_movie': moviename,
                               'default_path': '/static/default.jpeg'})
            return render(request, "make_selection.html",
                          {'search': search_results, 'searched_movie': moviename,
                           'default_path': '/static/default.jpeg'})
        default_path = f"http://image.tmdb.org/t/p/original{chosen_movie.poster_path}"
        if user_agent.is_mobile:
            return render(request, "make_selection_mob.html", {'search': search_results, 'searched_movie': moviename, 'default_path': default_path})
        return render(request, "make_selection.html", {'search': search_results, 'searched_movie': moviename, 'default_path': default_path})

    if request.method == "POST":
        selection = request.POST['selection']
        poster_movieID(int(moviename))
        if user_agent.is_mobile:
            return render(request, "make_selection_mob.html")
        return render(request, "make_selection.html")

def poster_movieID(id):
    global movieID
    movieID = id
    # print(movieID)
    chosen_movie = movie.details(movieID)
    POSTERPATH = "http://image.tmdb.org/t/p/original" + chosen_movie.poster_path
    img_data = requests.get(POSTERPATH).content
    # print(POSTERPATH)
    # print(movieID)
    # RASPBERRY PI VERSION with open('static/poster.jpg', 'wb') as handler:
    with open(r'static/poster.jpg', 'wb') as handler:
        handler.write(img_data)

    #posterwindow.changeImage = True
    #posterwindow.update_display()
    print("Changed")
    return

@csrf_exempt
def get_current_movie(request, movie_id=None):
    global movieID
    global poster_path
    #if chosen_movie:
    #    poster_path = "http://image.tmdb.org/t/p/original" + chosen_movie.poster_path
    #    return {'poster_path': poster_path}
    if request.method == "GET":
        if movie_id:
            movie_idtmp = str(movie_id).strip()
            movieIDtmp = str(movieID).strip()
            if movie_idtmp == movieIDtmp:
                print("Movie didn't change")
                return JsonResponse({'msg': 'Movie has not changed'})
        return JsonResponse({'msg':{'movie_id':movieID,'poster_path':poster_path}})
        data={'movie_id':movieID}
        print("sending image")
        im = Image.open('static/poster.jpg')
        exif = im.getexif()
        exif[0x9286] = movieID
        im.save('static/poster.jpg', exif=exif)
        poster_img = open('static/poster.jpg', 'rb')
        print(exif)
        return FileResponse(poster_img)
    data = {'error':'What are you trying to do?'}
    return JsonResponse(data)

