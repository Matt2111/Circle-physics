import pygame
from random import randint, seed
from Circles import Circle, CircleSim
from Lines import Line
from time import sleep
from math import sqrt

def DrawLine(display, line):
    nx = -(line.ey - line.sy)
    ny = (line.ex - line.sx)
    d = sqrt(nx * nx + ny * ny)
    nx /= d
    ny /= d

    pygame.draw.circle(display, (255, 255, 255), (line.sx, line.sy), line.radius, 1)
    pygame.draw.circle(display, (255, 255, 255), (line.ex, line.ey), line.radius, 1)
    pygame.draw.line(display, (255, 255, 255), (line.sx + nx * line.radius, line.sy + ny * line.radius),
                     (line.ex + nx * line.radius, line.ey + ny * line.radius), 1)
    pygame.draw.line(display, (255, 255, 255), (line.sx - nx * line.radius, line.sy - ny * line.radius),
                     (line.ex - nx * line.radius, line.ey - ny * line.radius), 1)

def UnlimitedBorders(circlesList):
    for circle in circlesList:
        if circle.x < 0:
            circle.x = 900
        elif circle.x > 900:
            circle.x = 0
        if circle.y < 0:
            circle.y = 500
        elif circle.y > 500:
            circle.y = 0

def Main():
    # Changeable simulation parameters
    seed(5)
    # How many times per second you want the simulation to log the state of the circles
    FRAMERATE = 1 / 30
    # How many collision per second
    COLLISIONS = 1000
    # Simulation time (seconds)
    SIM_TIME = 10
    # Each epoch the functions you enter get run the function must only take the circles as input
    WORLD_FUNCTIONS = [UnlimitedBorders]

    CIRCLES_AMOUNT = 50

    # Create circles
    circlesList = list()
    for x in range(CIRCLES_AMOUNT):
        radius = randint(1, 5)*10
        circlesList.append(Circle(radius, [randint(50, 850), randint(50, 450)], radius/10, velocity=[randint(-360, 360), randint(-360, 360)], acceleration=[0, 1000]))

    # Creates lines for the border of the scene
    linesList = [Line(((0, 500), (900, 500)), 10), Line(((0, 0), (0, 500)), 10), Line(((900, 0), (900, 500)), 10)]

    # Creates simulation object which calculates everything before hand and then returns the result
    simulation = CircleSim(circlesList, linesList)
    # Runs simulation
    simulationResults = simulation.SimulateCollisions(COLLISIONS, FRAMERATE, SIM_TIME, worldFunctions=WORLD_FUNCTIONS)
    # Setup pygame
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("Bouncing Circles")
    Display = pygame.display.set_mode((900, 500))

    # A "batch" is a list of frames, the amount is determined by "FRAMERATE"
    for batch in simulationResults:
        for frame in batch:
            sleep(1/len(batch))
            Display.fill((0, 0, 0))
            for circle in frame:
                pygame.draw.circle(Display, (255, 255, 255), (circle.x, circle.y), circle.radius, 1)
            for line in linesList:
                DrawLine(Display, line)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            pygame.display.update()

if __name__ == '__main__':
    Main()
