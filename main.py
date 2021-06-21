
import pygame

pygame.init()

# Lines 6-7: Caption / Display settings
screen = pygame.display.set_mode([600,800])
pygame.display.set_caption("Car-Obstacle Game")

count = 0

class User:

    def __init__(self, x_change): # Initializes x and y coordinates for Car
        self.x_change = x_change

        self.x = 285
        self.y = 675

    def display(self, x, y):
        global x_movement
        x_movement = 0

        # Line 25 - PNG from https://www.kindpng.com/imgv/iRmhxm_transparent-car-png-top-car-cartoon-from-top/
        player = pygame.image.load("Orange_Car.png")

        """ Lines 30 - 48: Movement Conditions for the Car, Inspiration from Lines 115 - 120, 128 - 139 at
            https://github.com/attreyabhatt/Space-Invaders-Pygame/blob/master/main.py """

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_movement = self.x_change * -1 # Car moves left
            if event.key == pygame.K_RIGHT:
                x_movement = self.x_change   # Car moves right

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                x_movement = 0
            if event.key == pygame.K_RIGHT:
                x_movement = 0

        self.x += x_movement

        # Boundaries for Car movement
        if self.x <= 0:   
            self.x = 0
        if self.x >= 555:
            self.x = 555
        
        screen.blit(player, (self.x,self.y))  # Displays car on screen
        
car = User(15)

class Obstacle:

    def __init__(self): # Initializes obstacle coordinates
        self.x = 0
        self.y = 0

    def display(self, x, y):
        global y_change
        y_change = 0

        # Line 65 - PNG adapted from https://www.flaticon.com/free-icon/barrier_479400?term=obstacle&page=1&position=12
        barrier = pygame.image.load("Barrier.png")
        if count == 0:
            screen.blit(barrier, (x,y))  # Displays obstacles at integer coordinates
            self.x = x
            self.y = y
            
        if count == 1:
            # Obstacle y-direction movement based on Level
            if level == 1:  
                y_change = 5
            if level == 2: 
                y_change = 10
            if level == 3: 
                y_change = 15

            self.y += y_change
            screen.blit(barrier, (self.x,self.y)) # Displays obstacle at coordinates saved as attributes

obstacles = []
for i in range(61): # Appends obstacle objects to a list
    obstacle = Obstacle()
    obstacles.append(obstacle)

# Lines 90 - 126: Functions to display Obstacles in their namesake Patterns

def horizontal(x,y,i):
    obstacles[i].display(x,y)
    obstacles[i+1].display(x+180,y)
    obstacles[i+2].display(x+360,y)

def diagonal(x,y,i,string):
    obstacles[i].display(x,y)
    if string == "right": # Looks like /
        obstacles[i+1].display(x+180,y-135)
        obstacles[i+2].display(x+360,y-270)
    if string == "left": # Looks like \
        obstacles[i+1].display(x-180,y-135)
        obstacles[i+2].display(x-360,y-270)

def triangle(x,y,i,integer):
    obstacles[i].display(x,y)
    obstacles[i+1].display(x+180+integer,y-160)
    obstacles[i+2].display(x+360,y+100)

def offset_square(x,y,i,integer):
    obstacles[i].display(x,y)
    obstacles[i+1].display(x+175,y-240-integer)
    obstacles[i+2].display(x+300,y)
    obstacles[i+3].display(x+465,y-240-integer)

def parallelogram(x,y,i):
    obstacles[i].display(x,y)
    obstacles[i+1].display(x+150,y+150)
    obstacles[i+2].display(x+300,y-120)
    obstacles[i+3].display(x+465,y)

def largeX(x,y,i):
    obstacles[i].display(x,y)
    obstacles[i+1].display(x-165,y-230)
    obstacles[i+2].display(x+165,y-230)
    obstacles[i+3].display(x-165,y+230)
    obstacles[i+4].display(x+165,y+230)


def collision(): # Function for collision of car and obstacle
    global collision_status
    collision_status = False

    for obstacle in obstacles: # Iterates over list of obstacles to see which if one collided with car
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

    

level = 1 
def level_change(): # Changes level, which changes speed of obstacles
    global level
    check_list = [obstacle for obstacle in obstacles if obstacle.y >= 800] # list of obstacles that are below screen
    if level == 1:
        if len(check_list) == 15:
            level = 2
            check_list.clear()
        else:
            check_list.clear()
    if level == 2:
        if len(check_list) == 35:
            level = 3
            check_list.clear()
        else:
            check_list.clear()
    

def show_text(string): # Function to display text for winning, losing, and level of the game

    if string == "level":
        level_font = pygame.font.Font("freesansbold.ttf",20)
        level_text = level_font.render("Level " + str(level), True, (255,255,255))
        screen.blit(level_text, (10,10))
    if string == "lose":
        lose_font = pygame.font.Font("freesansbold.ttf",35)
        lose_text = lose_font.render("You Lost ...", True, (240,5,5))
        screen.blit(lose_text, (207.5,386))
    if string == "win":
        win_font = pygame.font.Font("freesansbold.ttf",35)
        win_text = win_font.render("You Won!", True, (124,252,0))
        screen.blit(win_text, (221,368))
    pygame.display.update()
    


""" Lines 201 - 206: Inspiration from Simpson College Computer Science's code Lines 68 - 74 at
    http://programarcadegames.com/python_examples/show_file.php?file=snake.py"""

# Program Loop 
program_on = True
while program_on:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            program_on = False

    if collision() == False:

        screen.fill([107,108,115])  # Screen has grey color

        # Lines 215 - 236: Display and movement of obstacles in patterns
        # Level 1 Obstacles
        horizontal(75,-135,0)
        horizontal(15,-550,3)
        diagonal(450,-810,6,"left")
        triangle(15,-1350,9,0)
        horizontal(75,-1820,12)

        # Level 2 Obstacles
        triangle(13,-3000,15,15)
        horizontal(75,-3435,18)
        offset_square(0,-3710,21,0)
        diagonal(450,-4110,25,"left")
        parallelogram(0,-4920,28)
        diagonal(15,-5220,32,"right")

        # Level 3 Obstacles
        parallelogram(0,-6700,35)
        diagonal(15,-7010,39,"right")
        triangle(75,-7760,42,15)
        parallelogram(0,-8280,45)
        horizontal(15,-8860,49)
        offset_square(0,-9180,52,30)
        largeX(195,-9870,56)

        car.display(car.x, car.y)
           
        level_change()
        show_text("level")

        # Conditions if car is above all obstacles, which means that game is won
        collide_list = [obstacle for obstacle in obstacles if obstacle.y > (car.y + 150)]
        if len(collide_list) == len(obstacles):
            screen.fill([107,108,115])
            show_text("win")
        else:
            pass
    
    if collision() == True: # Game is lost
        
        screen.fill([107,108,115])
        show_text("lose")
        
    pygame.display.update() 
    count = 1 
    
pygame.quit()