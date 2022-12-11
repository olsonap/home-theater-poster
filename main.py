#!/usr/bin/env python
import requests
import time
from tmdbv3api import TMDb
from tmdbv3api import Movie
import jinja2
import os
import pygame
import cv2
from flask import Flask, render_template, flash, redirect, request, session
from multiprocessing import Process
from pynput.keyboard import Key, Controller

import webbrowser

#FLASK API_KEY
flask_key = "pk_66113390abf04f548b30e71300685206"



#Pygame initials
pygame.init()

dis_width = int(1080*(1/2))
dis_height = int(1920*(1/2))
#gameDisplay = pygame.display.set_mode((dis_width, dis_height), pygame.NOFRAME)
gameDisplay = pygame.display.set_mode((dis_width, dis_height))


pygame.display.set_caption('Poster')
default = pygame.image.load('static/default.jpeg').convert()
theater = pygame.image.load('static/theatername.jpg')
t_width = theater.get_width()
t_height = theater.get_height()
t_ratio = int(t_width / dis_width)
theater = pygame.transform.scale(theater, (dis_width, int(dis_width * (5 / 18))))


white = (255, 255, 255)
black = (0, 0, 0)

gameDisplay.fill(black)
gameDisplay.blit(default, (0, 0))
gameDisplay.blit(theater, (0, 0))
pygame.draw.rect(gameDisplay, white, (0, 0, dis_width, dis_height), 10)
pygame.display.update()

# FONTS
#font1 = pygame.font.Font('static/motionpicture.ttf', 90)
#text = font1.render("Twilight Cinema", True, white, black)
#textRect = text.get_rect()
#textRect.center = (dis_width / 2, 70)


keyboard = Controller()
tmdb = TMDb()
tmdb.api_key = '2b9f3ff3381ad78a6a295082cef2910d'
tmdb.language = 'en'
tmdb.debug = True
movie = Movie()
movieID = 140

changeImage = False

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

class mainloop():
	changeImage = False
	
	def update_display():
		global poster, gameDisplay, white, default, dis_width, dis_height
		time.sleep(0.1)
		#print("Hello there")
		pygame.display.update()
		poster = pygame.image.load('static/poster.jpg').convert()
		height = poster.get_height()
		width = poster.get_width()
		ratio = width/height
		#print(width, height)
		if width / dis_width > height / dis_height:
			width = int(width / (width / dis_width))
			height = int(width / (ratio))
		else:
			width = int(width / (height / dis_height))
			height = int(height * (height / dis_height))
		poster = pygame.transform.scale(poster, (width, height))
		#dis_height - height
		for i in range(100):
			poster.set_alpha(i)
			#print(i)
			gameDisplay.blit(theater, (0, 0))
			gameDisplay.blit(poster, (0, (dis_height - height)))
			pygame.draw.rect(gameDisplay, white, (0, dis_height - height, width, height - 5), 10)
			#gameDisplay.blit(poster, (0, (dis_height - height) / 2))
			pygame.display.update()
		poster.set_alpha(255)
		gameDisplay.fill(black)
		gameDisplay.blit(poster, (0, (dis_height - height)))
		gameDisplay.blit(theater, (0, 0))
		#gameDisplay.blit(text, textRect)
		pygame.draw.rect(gameDisplay, white, (0, dis_height - height, width, height - 5), 10)
		
		#gameDisplay.blit(poster, (0, (dis_height - height) / 2))
		pygame.display.update()
		return


	def pygameLoop():
		out = False
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					out = True
					break
					#pygame.display.quit()
					#pygame.quit()
					#quit()
				
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						#pygame.display.quit()
						out = True
						break
						#pygame.quit()
						#quit()
			
			if out:
				break
			if mainloop.changeImage:
				#print(self.changeImage)
				mainloop.update_display()
				mainloop.changeImage = False
		pygame.display.quit()
		pygame.quit()
		quit()
		

	def parallel_functions(*functions):
		processes = []
		for function in functions:
			p = Process(target=function)
			p.start()
			processes.append(p)
		for p in processes:
			p.join()
			
		
	@app.route("/", methods=["GET", "POST"])
	def home():
		global movieID
		chosen_movie = movie.details(movieID)
		POSTERPATH = "http://image.tmdb.org/t/p/original" + chosen_movie.poster_path
		img_data = requests.get(POSTERPATH).content
		print(POSTERPATH)
		print("index ", movieID)
		with open('static/poster.jpg', 'wb') as handler:
			handler.write(img_data)
			
		return render_template("index.html")
		
	@app.route("/poster_movieID<id>", methods=["GET","POST"])
	def poster_movieID(id):
		global movieID
		movieID = id
		#print(movieID)
		chosen_movie = movie.details(movieID)
		POSTERPATH = "http://image.tmdb.org/t/p/original" + chosen_movie.poster_path
		img_data = requests.get(POSTERPATH).content
		#print(POSTERPATH)
		#print(movieID)
		with open('static/poster.jpg', 'wb') as handler:
			handler.write(img_data)
		
		#print(mainloop.changeImage)
		mainloop.changeImage = True
		#print(mainloop.changeImage)
		mainloop.update_display()
		#keyboard.press(Key.ctrl)
		#keyboard.press('w')
		#keyboard.release(Key.ctrl)
		#keyboard.release('w')
		#time.sleep(1)
		#webbrowser.open('http://0.0.0.0:5000/', new=0)
		#time.sleep(5)
		#keyboard.press(Key.f11)
		#keyboard.release(Key.f11)
		return render_template("index.html")

	def run_app():
		app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
	#app.run(host='0.0.0.0', port=5000, debug=True)
	mainloop.parallel_functions(mainloop.run_app, mainloop.pygameLoop)
mainloop.pygame.display.quit()
mainloop.pygame.quit()
mainloop.quit()
