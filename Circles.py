from math import sqrt
from copy import deepcopy

class Circle:
    def __init__(self, radius, position, mass, acceleration=None, velocity=None):
        if velocity is None:
            velocity = [0, 0]
        if acceleration is None:
            acceleration = [0, 0]
        self.x, self.y = position
        self.vx, self.vy = velocity
        self.ax, self.ay = acceleration
        self.radius = radius
        self.mass = mass

    def Move(self, timeElapsed):
        fx = self.vx * 0.9 * timeElapsed
        fy = self.vy * 0.9 * timeElapsed
        checkAX, checkAY = self.ax * timeElapsed, self.ay * timeElapsed
        self.vx += checkAX - fx
        self.vy += checkAY - fy
        if -0.01 < self.vx < 0.1 and not -0.1 < checkAX < 0.1:
            self.vx = 0
        if -0.1 < self.vy < 0.1 and not -0.1 < checkAY < 0.1:
            self.vy = 0
        self.x += self.vx * timeElapsed
        self.y += self.vy * timeElapsed

    def PointWithin(self, x, y):
        return self.x + self.radius >= x >= self.x - self.radius and self.y + self.radius >= y >= self.y - self.radius

    def DistanceToPoint(self, point):
        return ((point.x - self.x)*(point.x - self.x)) + ((point.y - self.y)*(point.y - self.y))

    def GetHalfOverlap(self, distance, point):
        return abs((self.radius + point.radius) - distance) / 2

    def CollideLine(self, line):
        deltaBallStart = (self.x - line.sx, self.y - line.sy)
        deltaStartEnd = (line.ex - line.sx, line.ey - line.sy)
        lineLength = deltaStartEnd[0]*deltaStartEnd[0] + deltaStartEnd[1]*deltaStartEnd[1]

        t = max(0, min(lineLength, deltaBallStart[0] * deltaStartEnd[0] + deltaBallStart[1] * deltaStartEnd[1])) / lineLength

        closestPoint = (line.sx + (deltaStartEnd[0] * t), line.sy + (deltaStartEnd[1] * t))

        if ((closestPoint[0] - self.x)*(closestPoint[0] - self.x)) + ((closestPoint[1] - self.y)*(closestPoint[1] - self.y)) <= (self.radius + line.radius) * (self.radius + line.radius):
            return Circle(line.radius, closestPoint, self.mass, velocity=[-self.vx, -self.vy])

    def CollideCircle(self, circle):
        distanceToPoint = self.DistanceToPoint(circle)
        combinedRadii = circle.radius + self.radius
        if combinedRadii*combinedRadii > distanceToPoint > 0:
            distanceToPoint = sqrt(distanceToPoint)
            depth = self.GetHalfOverlap(distanceToPoint, circle)
            self.x += (depth * (self.x - circle.x)) / distanceToPoint
            self.y += (depth * (self.y - circle.y)) / distanceToPoint
            circle.x -= (depth * (self.x - circle.x)) / distanceToPoint
            circle.y -= (depth * (self.y - circle.y)) / distanceToPoint
            return True
        return False

class Circles:
    def __init__(self, circles, lines):
        self.lines = lines
        self.circles = circles
        self.collidedCirclePairs = list()
        self.collidedLinePairs = list()

    def HandleLineCollisions(self):
        for objectA, objectB in self.collidedLinePairs:
            distance = sqrt(objectA.DistanceToPoint(objectB))
            nx = (objectB.x - objectA.x) / distance
            ny = (objectB.y - objectA.y) / distance

            tx = -ny
            ty = nx

            dpTanA = objectA.vx * tx + objectA.vy * ty

            dpNormA = objectA.vx * nx + objectA.vy * ny
            dpNormB = objectB.vx * nx + objectB.vy * ny

            mA = (dpNormA * (objectA.mass - objectB.mass) + 2 * objectB.mass * dpNormB) / (objectA.mass + objectB.mass)

            objectA.vx = tx * dpTanA + nx * mA
            objectA.vy = ty * dpTanA + ny * mA

    def HandleCircleCollisions(self):
        for objectA, objectB in self.collidedCirclePairs:
            distance = sqrt(objectA.DistanceToPoint(objectB))
            nx = (objectB.x - objectA.x) / distance
            ny = (objectB.y - objectA.y) / distance

            tx = -ny
            ty = nx

            dpTanA = objectA.vx * tx + objectA.vy * ty
            dpTanB = objectB.vx * tx + objectB.vy * ty

            dpNormA = objectA.vx * nx + objectA.vy * ny
            dpNormB = objectB.vx * nx + objectB.vy * ny

            mA = (dpNormA * (objectA.mass - objectB.mass) + 2 * objectB.mass * dpNormB) / (objectA.mass + objectB.mass)
            mB = (dpNormB * (objectB.mass - objectA.mass) + 2 * objectA.mass * dpNormA) / (objectA.mass + objectB.mass)

            objectA.vx = tx * dpTanA + nx * mA
            objectA.vy = ty * dpTanA + ny * mA
            objectB.vx = tx * dpTanB + nx * mB
            objectB.vy = ty * dpTanB + ny * mB

    def Collide(self):
        collidedCircles, collidedLines = list(), list()
        self.collidedCirclePairs, self.collidedLinePairs = list(), list()
        appendCollidedCircles, appendCollidedCirclePairs = collidedCircles.append, self.collidedCirclePairs.append
        appendCollidedLinePairs = self.collidedLinePairs.append
        appendCollidedLines = collidedLines.append
        for x, mainCircle in enumerate(self.circles):
            CollideLine = mainCircle.CollideLine
            CollideCircle = mainCircle.CollideCircle
            for y, otherCircle in enumerate(self.circles):
                if y <= x:
                    continue
                if CollideCircle(otherCircle):
                    appendCollidedCirclePairs([mainCircle, otherCircle])
                    appendCollidedCircles(otherCircle)
                    if mainCircle not in collidedCircles:
                        appendCollidedCircles(mainCircle)
            for line in self.lines:
                collisionResult = CollideLine(line)
                if collisionResult is not None and CollideCircle(collisionResult):
                    appendCollidedLinePairs([mainCircle, collisionResult])
                    if line not in collidedLines:
                        appendCollidedLines(line)
        return self.collidedCirclePairs, collidedCircles, self.collidedLinePairs, collidedLines

class CircleSim(Circles):
    def __init__(self, circles, lines):
        super().__init__(circles, lines)
        self.frames = list()

    def SimulateCollisions(self, collisionsPerFrame, fps, batches, worldFunctions=None):
        if worldFunctions is None:
            worldFunctions = list()
        fps = int(collisionsPerFrame / fps)
        for x in range(batches):
            frameBunch = list()
            for y in range(collisionsPerFrame):
                for function in worldFunctions:
                    function(self.circles)
                self.Collide()
                self.HandleCircleCollisions()
                self.HandleLineCollisions()
                for circle in self.circles:
                    circle.Move(1/collisionsPerFrame)
                if not y % fps:
                    circleStateFlash = [deepcopy(_) for _ in self.circles]
                    frameBunch.append(circleStateFlash)
            self.frames.append(frameBunch)
        return self.frames
