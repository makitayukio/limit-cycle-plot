import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
import math
from matplotlib.transforms import Affine2D

class Point():
    def __init__(self, x, y, r=None, is_vo=False):
        self.x = x
        self.y = y
        self.r = r
        self.is_vo = is_vo

class Ball():
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

class Obstacle():
    def __init__(self, x, y, r, side=None, is_vo=False):
        self.x = x
        self.y = y
        self.r = r
        self.side = side
        self.is_vo = is_vo

def discriminant(a, b, c, o):
    k = 1 + (a**2/b**2)
    l = -2*o.x + (2*a*c)/b**2 + (2*a*o.y)/b
    m = o.x**2 + o.y**2 - o.r**2 + c**2/b**2 + (2*c*o.y)/b
    dscr = l**2 - 4*k*m
    return dscr

def dist(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def filter_func(a, b, c, r, t, o):
    return discriminant(a, b, c, o) > 0 and dist(o, r) < dist(r, t) and dist(o, t) < dist(r, t)

def contour(a, b, c, robot, obst, idx=15):
        dx = robot.x - obst.x
        dy = robot.y - obst.y
        
        mlt = int(idx/math.sqrt(dx**2 + dy**2))

        if obst.is_vo:
            if obst.side == "R": #cw
                d = 1
            else: # ccw
                d = -1
        else:
            d = (a*obst.x + b*obst.y + c)/math.sqrt(a**2 + b**2)

        print(d)
        
        ddx =  (d/abs(d))*dy + mlt*dx*(obst.r**2 - dx**2 - dy**2)
        ddy = -(d/abs(d))*dx + mlt*dy*(obst.r**2 - dx**2 - dy**2)

        return (robot.x + dt*ddx, robot.y + dt*ddy)

fig = plt.figure(figsize=(10, 7.8))

vel = 0.05

ball = Obstacle(1.3, .4, (.0427/2))
ball = Obstacle(1.3, .9, (.0427/2))

j = math.atan2((0.65 - ball.y), 1.5 - ball.x)

t = Point(ball.x, ball.y) # target
r_v = .12 # avoidance radius
q_1 = Point(1.2, .65, r_v) # obstacle
q_2 = Point(1.2 - 2*r_v*math.cos(math.pi/4), .65 + 2*r_v*math.sin(math.pi/4), r_v) # obstacle
q_3 = Point(1.2 - r_v*math.cos(math.pi/4), .65 + r_v*math.sin(math.pi/4), r_v) # obstacle
r = Point(1, 1, 0) # robot
r = Point(1, .3, 0) # robot

j_r = j + math.pi/2
p = 0.075

if r.y < j*(r.x - ball.x) + ball.y:
    vo = Obstacle(t.x - p*math.cos(j_r) - ball.r*math.cos(j), t.y - p*math.sin(j_r) - ball.r*math.sin(j), p, side="R", is_vo=True)
else:
    vo = Obstacle(t.x + p*math.cos(j_r) - ball.r*math.cos(j), t.y + p*math.sin(j_r) - ball.r*math.sin(j), p, side="L", is_vo=True)

target_is_ball = False

# Plotting Field
ax = plt.gca()
ax.add_patch(Rectangle((0, 0), 1.5, 1.3, fill=None, alpha=1))
ax.add_patch(Rectangle((0, 0), .75, 1.3, fill=None, alpha=1))
ax.add_patch(Rectangle((0, .45), -.1, .4, fill=None, alpha=1))
ax.add_patch(Rectangle((1.5, .45), .1, .4, fill=None, alpha=1))
ax.add_patch(Rectangle((0, .3), .15, .7, fill=None, alpha=1))
ax.add_patch(Rectangle((1.5, .3), -.15, .7, fill=None, alpha=1))
ax.add_patch(Circle((.75, .65), .2, fill=None, alpha=1))
ax.add_patch(Arc((.15, .65), .1, 0.2, angle=0, theta1=-90, theta2=90, fill=None, alpha=1))
ax.add_patch(Arc((1.5-.15, .65), .1, 0.2, angle=0, theta1=90, theta2=-90, fill=None, alpha=1))
ax.add_patch(Rectangle((r.x-(.075/2), r.y-(.075/2)), .075, .075, fill=True, color="blue", alpha=1))
ax.add_patch(Circle((ball.x, ball.y), ball.r, fill=True, color="orange", alpha=1))

ax.add_patch(Rectangle((q_1.x-(.075/2), q_1.y-(.075/2)), .075, .075, fill=True, color="yellow", alpha=1))
ax.add_patch(Circle((q_1.x, q_1.y), r_v, fill=None, color="black", alpha=1))

ax.add_patch(Rectangle((q_2.x-(.075/2), q_2.y-(.075/2)), .075, .075, fill=True, color="yellow", alpha=1))
ax.add_patch(Circle((q_2.x, q_2.y), r_v, fill=None, color="black", alpha=1))

ax.add_patch(Rectangle((q_3.x-(.075/2), q_3.y-(.075/2)), .075, .075, fill=True, color="lime", alpha=1))

if target_is_ball:
    ax.add_patch(Circle((vo.x, vo.y), vo.r, fill=None, color="black", alpha=1))
    obstacles = [q_1, vo]
else:
    obstacles = [q_1]

path_x = []
path_y = []

while round(r.x, 2) != round(t.x, 2) and round(r.x, 2) != round(t.x, 2):
    _fps = 60
    dt = 1/_fps
    
    x = np.linspace(r.x, t.x, 10)

    a = t.y - r.y
    b = r.x - t.x
    c = t.x*r.y - r.x*t.y
    
    obstacles = list(filter(lambda o: filter_func(a, b, c, r, t, o), obstacles))
    obstacles.sort(key=lambda o: math.sqrt((o.x - r.x)**2 + (o.y - r.y)**2))

    print(f"{r.x=}\n{r.y=}")
    print(f"{t.x=}\n{t.y=}")

    if len(obstacles) > 0:
        r_x, r_y = contour(a, b, c, r, obstacles[0])

        r.x = r_x
        r.y = r_y

        path_x.append(r.x)
        path_y.append(r.y)

    else:
        if target_is_ball:    
            r_x, r_y = contour(a, b, c, r, vo, 12.5)

            r.x = r_x
            r.y = r_y

            path_x.append(r.x)
            path_y.append(r.y)
        else:
            r_x = r.x + dt
            r_y = (-a*r_x - c)/b

            r.x = r_x
            r.y = r_y

            path_x.append(r.x)
            path_y.append(r.y)

plt.plot(path_x, path_y)
plt.plot([t.x, 1.5], [t.y, 0.65])

# Setting x, y boundary limits
plt.xlim(-0.15, 1.65)
plt.ylim(-0.05, 1.35)
plt.axis("equal")
  
# Show plot with grid
plt.show()
