import pygame
import neat
import os
import time
import sys
from math import dist


pygame.init()
pygame.display.set_caption("Car-Obstacle Game")

generation = 0

class Car:

	def __init__(self): # Initializes car coordinates, y-movement, and image
		self.x = 285
		self.y = 675

		self.X_CHANGE = 15
		self.IMAGE = pygame.image.load("Orange_Car.png")


	def display(self,action,screen): # controls display and x-movement of car

		if action == 'right':
			self.x -= self.X_CHANGE

		elif action == 'left':
			self.x += self.X_CHANGE

		if self.x <= 0:
			self.x = 0
		if self.x >= 555:
			self.x = 555	

		screen.blit(self.IMAGE, (self.x,self.y))



class Obstacle:

	def __init__(self, x, y): # Initializes obstacle coordinates, y-movement, and image
		self.x = x
		self.y = y

		self.Y_CHANGE = 5
		self.IMAGE = pygame.image.load("Barrier.png")


	def display(self,screen): #controls display and vertical movement of each obstacle

		self.y += self.Y_CHANGE
		screen.blit(self.IMAGE, (self.x,self.y))
		


class Pattern:  

	def __init__(self, x, y, style):  #Pattern objects contain a list of obstacles
		self.obstacles = []
		self.OP_1 = self.OP_2 = 0  #Coordinates of openings in pattern for car to go through
		self.STYLE = style

		self.configure_patterns(x,y)   #Sets up each pattern with coordinates


	def configure_patterns(self,x,y):

		if self.STYLE == 'horizontal':
			self.obstacles = [Obstacle(x,y), Obstacle(x+165,y), Obstacle(x+330,y)]
			self.OP_1 = self.OP_2 = (x / 2 if x == 105 else 547.5)

		elif self.STYLE == 'right diagonal':
			self.obstacles = [Obstacle(x,y), Obstacle(x+160,y-135), Obstacle(x+330,y-270)]
			self.OP_1 = self.OP_2 = 540

		elif self.STYLE == 'left diagonal':
			self.obstacles = [Obstacle(x,y), Obstacle(x-165,y-135), Obstacle(x-330,y-270)]
			self.OP_1 = self.OP_2 = 60

		elif self.STYLE == 'triangle':
			self.obstacles = [Obstacle(x,y), Obstacle(x+160,y-160), Obstacle(x+360,y+100)]
			self.OP_1 = self.OP_2 = self.obstacles[2].x - 15

		elif self.STYLE == 'offset_square':
			self.obstacles = [Obstacle(x,y), Obstacle(x+465,y-240), Obstacle(x+345,y), Obstacle(x+100,y-240)]
			self.OP_1 = self.obstacles[2].x - 30
			self.OP_2 = self.obstacles[2].x + 15


	def get_peak_y(self):  #Returns the y coordinate of the top of the pattern

		if self.STYLE == 'horizontal':
			return self.obstacles[0].y
		elif self.STYLE in ['right diagonal','left diagonal']:
			return self.obstacles[2].y
		elif self.STYLE in ['triangle','offset_square']:
			return self.obstacles[1].y


	def display(self,screen):  # Controls display of patterns
		for obstacle in self.obstacles:
			obstacle.display(screen)


def dist_closest_obstacle(pattern, car_x, car_y):  #Distance from car to closest obstacle

	distances = []
	for i in range(len(pattern.obstacles)):
		distances.append( dist([car_x,car_y], [pattern.obstacles[i].x+67.5, pattern.obstacles[i].y+58.5]) )

	min_dist = min(distances)
	i = distances.index(min_dist)

	return (-1 * min_dist if car_x < pattern.obstacles[i].x else min_dist)


def collision(car, pattern):
	
	collision_status = False

	for obstacle in pattern.obstacles: # Iterates over list of obstacles in a pattern to check collision
		# Bottom of Orange Posts
		if (obstacle.x - 25) <= car.x <= (obstacle.x + 25) or (obstacle.x + 65) <= car.x <= (obstacle.x + 115):
			if car.y == (obstacle.y + 110):
				collision_status = True

		# Side of Orange Posts
		if car.y <= (obstacle.y + 110) and car.y >= (obstacle.y + 75):
			if (car.x + 45) >= (obstacle.x + 30) and car.x <= (obstacle.x + 15):
				collision_status = True
			elif (car.x + 45) >= (obstacle.x + 120) and car.x <= (obstacle.x + 105):
				collision_status = True

		# Inner bottom part of Obstacle
		if car.y <= (obstacle.y + 75) and car.y >= (obstacle.y + 40):
			if (car.x + 45) >= (obstacle.x + 5) and car.x <= (obstacle.x + 130):
				collision_status = True

		# Outer Sides of Obstacle
		if (car.y + 100) >= (obstacle.y) and car.y <= (obstacle.y + 81):
			if (car.x + 45) >= (obstacle.x + 15) and (car.x + 45) <= (obstacle.x + 40):
				collision_status = True
			if car.x >= (obstacle.x + 95) and car.x <= (obstacle.x + 120):
				collision_status = True

	return collision_status


def show_text(string, screen): # Function to display text for statistics and winning

	if string == "stats":
		stat_font = pygame.font.Font("freesansbold.ttf",20)
		stat_text = stat_font.render("Pattern " + str(index + 1) +
										", Gen " + str(generation), True, (255,255,255))
		screen.blit(stat_text, (10,10))

	elif string == "win":
		win_font = pygame.font.Font("freesansbold.ttf",35)
		win_text = win_font.render("You Won!", True, (124,252,0))
		screen.blit(win_text, (221,368))

	pygame.display.update()
	

def eval_genomes(genomes, config):  #main function, ran for each generation

	SCREEN = pygame.display.set_mode([600,800])

	cars = [] #contains lists, each of which contains car object, genome, and neural net corresponding to that car

	#initialization of patterns
	patterns = [Pattern(105,-135,"horizontal"), Pattern(30,-580,"horizontal"),
				Pattern(450,-855,"left diagonal"), Pattern(15,-1400,"triangle"),
				Pattern(30,-1900,"horizontal"), Pattern(450,-2310,"left diagonal"),
				Pattern(105,-2765,"horizontal"),Pattern(0,-3060,"offset_square"),
				Pattern(450,-3450,"left diagonal"), Pattern(30, -4200, "horizontal"),
				Pattern(0,-4600,"offset_square"),Pattern(15,-5100,"right diagonal"),
				Pattern(100,-5800,"triangle"),Pattern(0,-6300,"offset_square"),
				Pattern(15, -6800, "right diagonal")]

	#Index that signifies upcoming / current pattern, which will serve as input for the Neural Networks
	global index
	index = 0

	#Appends lists of a car object and its corresponding genome and neural network to the cars list
	for genome_id, genome in genomes:

		genome.fitness = 0
		net = neat.nn.FeedForwardNetwork.create(genome, config)

		cars.append([Car(), genome, net])

	
	running = True
	while running and len(cars) >= 1:
		
		#Conditions for quitting game if user quits in middle
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				sys.exit()

		
		for car in cars:

			#Condition to change the upcoming pattern / input source to Neural Network
			if patterns[index].get_peak_y() > car[0].y + 100:

				# If car passed all patterns successfully, end game and display Winning text
				if index == len(patterns) - 1:
					pass
					SCREEN.fill([107,108,115])
					show_text("win", SCREEN)
					time.sleep(5)
					sys.exit()

				#Otherwise increase index for next pattern, increase car's fitness since it passed previous pattern successfully
				else:
					index += 1
					car[1].fitness += 4


		SCREEN.fill([107,108,115])

		#Checks for collision of car and obstacle; if collision, remove the specific car list from cars
		for car in cars:
			if collision(car[0], patterns[index]):
				car[1].fitness -= 2
				cars.pop(cars.index(car))


		#Pattern display
		for pattern in patterns: 
			pattern.display(SCREEN)

		
		#Car display and neural network inputs
		for car in cars:  

			car_centerX = car[0].x + 23
			car_centerY = car[0].y + 50


			dist = dist_closest_obstacle(patterns[index],car_centerX, car_centerY)

			"""
			NEAT NN Inputs:
				For upcoming pattern,
					1. Y Distance from top of pattern to center of car
					2. X Distance from first opening of pattern to center of car
					3. X Distance from second opening of pattern to center of car (Mainly for offset square)
					4. Distance from car to closest obstacle, positive or negative
					   depending on relative positioning (left or right)

			"""
			value = car[2].activate((patterns[index].get_peak_y() - car_centerY, 
									 patterns[index].OP_1 - car_centerX,
									 patterns[index].OP_2 - car_centerX,
									 dist))

			# Car takes action depending on value returned by Neural Network
			if value[0] > 0.5:
				car[0].display('right',SCREEN)
			elif value[0] < -0.5:
				car[0].display('left',SCREEN)
			else:
				car[0].display('still',SCREEN)
		

		show_text('stats', SCREEN)

		pygame.display.update()

	global generation  
	generation += 1  # Increases generation number for display




def run(config_file):
	# Load configuration file
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_file)

	# Create population
	p = neat.Population(config)

	# Add statistic reporters to show progress for each generation in terminal
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	p.add_reporter(neat.Checkpointer(5))

	#Run the NEAT algorithm over 25 generations
	p.run(eval_genomes, 25)


if __name__ == '__main__':
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config.txt')
	run(config_path)





