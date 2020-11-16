from Circles import Circle, Circles
from Lines import Line
from random import randint, seed
from math import sqrt
import pygame
from time import clock

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

def Main():
    # Changeable simulation parameters
    seed(1)
    MINIMUM_FRAMERATE = 1 / 30
    CIRCLES_AMOUNT = 20
    LINES_AMOUNT = 5

    # Automatic game parameter
    EPOCH_DIVISION = 1

    # Setup pygame
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("Bouncing Circles")
    Display = pygame.display.set_mode((900, 500))

    # Create lines(boundaries) and circles
    circlesList = list()
    linesList = list()
    for i in range(LINES_AMOUNT):
        linesList.append(Line([[100, 20*i], [300, 20*i]], 10))

    for x in range(CIRCLES_AMOUNT):
        radius = randint(20, 60)
        circlesList.append(Circle(radius, [randint(50, 850), randint(50, 450)], radius, acceleration=[0, 980]))

    # Create variables for interacting with the circles and lines
    circleClicked = None
    flick = None
    lineClicked = None

    # circles object where we simulate the physics
    circles = Circles(circlesList, linesList)

    deltaTime = clock()

    # If false stops the simulation but you can still interact with the objects (pressing space flips this variable)
    runSim = True
    while True:
        # Uncomment this if you want to see how many times the epoch gets split up (higher the better)
        # print(EPOCH_DIVISION)

        # makes screen blank
        Display.fill((0, 0, 0))

        timeElapsed = clock() - deltaTime
        deltaTime = clock()
        if runSim:
            # Splits time based of the EPOCH_DIVISION to make physics more accurate
            timeElapsed = timeElapsed / EPOCH_DIVISION
            for i in range(EPOCH_DIVISION):
                # Calculates the physics of the circles
                circles.Collide()
                circles.HandleCircleCollisions()
                circles.HandleLineCollisions()
                for circle in circlesList:
                    circle.Move(timeElapsed)
            # Determines if the EPOCH_DIVISION is to high/low to keep up the framerate requested at the beginning
            calculationTime = clock() - deltaTime
            if calculationTime + timeElapsed > MINIMUM_FRAMERATE and EPOCH_DIVISION-1:
                EPOCH_DIVISION -= 1
            elif calculationTime + timeElapsed < MINIMUM_FRAMERATE:
                EPOCH_DIVISION += 1

        # Displays circles
        for circle in circlesList:
            pygame.draw.circle(Display, (255, 255, 255), (circle.x, circle.y), circle.radius, 1)

        # Displays lines
        for line in linesList:
            DrawLine(Display, line)

        # Makes sure the balls don't run off the screen
        for circle in circlesList:
            if circle.x < 0:
                circle.x = 900
            elif circle.x > 900:
                circle.x = 0
            elif circle.y > 500:
                circle.y = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if runSim:
                        runSim = False
                    else:
                        runSim = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Checks if you're grabbing a line or circle to move
                if pygame.mouse.get_pressed(3)[0]:
                    x, y = pygame.mouse.get_pos()
                    for line in linesList:
                        if line.sx + line.radius >= x >= line.sx - line.radius and line.sy + line.radius >= y >= line.sy - line.radius:
                            lineClicked = [line, 0]
                            break
                        if line.ex + line.radius >= x >= line.ex - line.radius and line.ey + line.radius >= y >= line.ey - line.radius:
                            lineClicked = [line, 1]
                            break
                    for circle in circlesList:
                        if circle.PointWithin(x, y):
                            circleClicked = circle
                            break
                if pygame.mouse.get_pressed(3)[2]:
                    for circle in circlesList:
                        if circle.PointWithin(*pygame.mouse.get_pos()):
                            flick = circle
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if not pygame.mouse.get_pressed(3)[0]:
                    circleClicked = None
                    lineClicked = None

                if not pygame.mouse.get_pressed(3)[2] and flick is not None:
                    mousePos = pygame.mouse.get_pos()
                    flick.vx += (flick.x - mousePos[0]) * 10
                    flick.vy += (flick.y - mousePos[1]) * 10
                    flick = None

        # Draw flick line
        if flick is not None:
            pygame.draw.line(Display, (0, 0, 255), [flick.x, flick.y], pygame.mouse.get_pos(), 2)

        # Check if dragging a circle or line
        if pygame.mouse.get_pressed(3)[0] and flick is None:
            x, y = pygame.mouse.get_pos()
            if circleClicked is not None:
                circleClicked.x, circleClicked.y = x, y
                circleClicked.vx, circleClicked.vy = 0, 0
            elif lineClicked is not None:
                if lineClicked[1]:
                    lineClicked[0].ex, lineClicked[0].ey = x, y
                elif not lineClicked[1]:
                    lineClicked[0].sx, lineClicked[0].sy = x, y
        pygame.display.update()

if __name__ == '__main__':
    Main()
