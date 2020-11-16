class Line:
    def __init__(self, positions, radius):
        self.sx, self.sy = positions[0]
        self.ex, self.ey = positions[1]
        self.radius = radius
