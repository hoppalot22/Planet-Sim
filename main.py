#import pygame as pg
import os
import random
import math
import time
import tkinter as tk

running = True
worlds = []

class Vector2:
    def __init__(self, x, y):

        self.x = float(x)
        self.y = float(y)

        self.components = [self.x, self.y]

    def __repr__(self):
        return f"[{self.x}, {self.y}]"

    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter > 1:
            raise StopIteration
        component = self.components[self.counter]
        self.counter += 1
        return component

    def __getitem__(self, item):
        return self.components[item]

    def __add__(self, Vec2):
        return Vector2(self.x + Vec2.x, self.y + Vec2.y)

    def __sub__(self, Vec2):
        return Vector2(self.x - Vec2.x, self.y - Vec2.y)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Vector2(self.x / other, self.y / other)

    def VectorMag(self):
        mag = 0
        for component in self:
            mag = math.sqrt(mag * mag + component * component)
        return mag

    def VectorNorm(self):
        mag = self.VectorMag()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def VectorDot(self, vec2):
        return self.x * vec2.x + self.y * vec2.y

class World:
    def __init__(self, gravity=0.01, speed=1, boundaries=None):
        global worlds
        if boundaries is None:
            boundaries = [1000, 1000]
        self.gravity = gravity
        self.boundaries = boundaries
        self.speed = speed

        self.bodies = []
        worlds.append(self)
        self.ID = str(len(worlds))
        self.frameNum = 0
        self.largestBody = None
        self.totalKineticEnergy = 0
        self.totalMomentum = 0

        self.mousePos = Vector2(0,0)
        self.window = tk.Tk()
        self.window.bind("<Configure>", self.UpdateCanvasSize)
        self.window.title(f'Physics: {self.ID}')
        self.canvas = tk.Canvas(self.window, width=self.boundaries[0], height=self.boundaries[1], highlightthickness=0)
        self.canvas.bind("<Button-1>", self.InitScroll)
        self.canvas.bind("<B1-Motion>", self.Scroll)
        self.canvas.bind("<MouseWheel>", self.Zoom)
        self.canvas.pack()

    def CalcMomentum(self):
        result = Vector2(0,0)
        for body in self.bodies:
            result += body.velocity * body.mass
        result = result.VectorMag()
        return result

    def CalcEnergy(self):
        result = 0
        for body in self.bodies:
            result += body.mass * body.velocity.VectorMag() * body.velocity.VectorMag() / 2
        return result

    def Tick(self):

        self.totalKineticEnergy = round(self.CalcEnergy(),2)
        self.totalMomentum = round(self.CalcMomentum(),2)

        for body in self.bodies:
            body.UpdateAccel()
            body.UpdateVelocity()
            body.UpdatePosition()
            body.CheckCollision()
            # if self.frameNum % 60 == 0:
            #     print(
            #         f"Body ID: {body.ID}, Body Mass: {body.mass}, Body Accel: {body.acceleration} Body velocity: {body.velocity}, Body Position {body.position}")

        self.RenderWorld()
        self.window.after(int(1000 / self.speed / 60), self.Tick)
        self.frameNum += 1

    def AddBody(self, body):
        if type(body) == MassBody:
            self.bodies.append(body)
            body.world = self
            body.ID = str(len(self.bodies))
            if self.largestBody is not None:
                if body.mass > self.largestBody.mass:
                    self.largestBody = body
            else:
                self.largestBody = body
            if body.position is None:
                body.position = [int(self.boundaries[0] / 2), int(self.boundaries[1] / 2)]

        else:
            raise Exception("Only MassBodies may be added to Worlds")

    def Zoom(self, event):
        if(event.delta<0):
            print("Zooming out")
        else:
            print("Zooming in")
    #     for body in self.bodies:
    #         body.mass += event.delta/120

    def InitScroll(self, event):
        self.mousePos = Vector2(event.x, event.y)
    def Scroll(self, event):
        for body in self.bodies:
            body.position += Vector2(event.x-self.mousePos.x, event.y - self.mousePos.y)
        self.mousePos = Vector2(event.x, event.y)

    def UpdateCanvasSize(self, event):
        self.canvas.config(width = self.window.winfo_width(), height=self.window.winfo_height())
    def RenderWorld(self):
        self.canvas.delete("all")
        for body in self.bodies:
            self.canvas.create_oval(body.position[0] - body.mass, body.position[1] - body.mass,
                                    body.position[0] + body.mass, body.position[1] + body.mass)
            if not (body.acceleration[0] == 0 and body.acceleration[1] == 0):
                self.canvas.create_line(body.position[0], body.position[1],body.position[0]+max(20,body.mass)*body.acceleration[0]/body.acceleration.VectorMag(), body.position[1]+max(20,body.mass)*body.acceleration[1]/body.acceleration.VectorMag(), fill='blue')
            if not (body.velocity[0] == 0 and body.velocity[1] == 0):
                self.canvas.create_line(body.position[0], body.position[1],body.position[0]+max(20,body.mass)*body.velocity[0]/body.velocity.VectorMag(), body.position[1]+max(20,body.mass)*body.velocity[1]/body.velocity.VectorMag(), fill='green')
        if self.largestBody is not None:
            #print("drawing")
            arrow_coords = self.largestBody.position.VectorNorm()*20
            self.canvas.create_line(30,30,30 + arrow_coords.x, 30 + arrow_coords.y)
            self.canvas.create_oval(26,26,34,34, fill='red')

        self.canvas.create_text(70, 50, text = f"Total Kinetic Energy: {self.totalKineticEnergy}")
        self.canvas.create_text(70, 70, text=f"Total Momentum: {self.totalMomentum}")
class MassBody:
    def __init__(self, mass, position=None, size=0, velocity=None, shape="circle"):
        if position is None:
            position = Vector2(0, 0)
        self.position = Vector2(position[0], position[1])
        if velocity is None:
            velocity = Vector2(0, 0)
        self.mass = mass
        self.size = size
        self.shape = shape
        self.velocity = Vector2(velocity[0], velocity[1])
        self.acceleration = Vector2(0, 0)
        self.world = None
        self.ID = None

    def UpdatePosition(self):
        self.position += self.velocity


    def UpdateVelocity(self):
        self.velocity += self.acceleration

    def UpdateAccel(self):
        self.acceleration = Vector2(0,0)
        for body in self.world.bodies:
            if body is self:
                continue
            relPos = body.position - self.position
            if relPos.VectorMag() < 0.8 * (self.mass + body.mass):
                continue
            accelScalar = self.world.gravity * body.mass / relPos.VectorMag() / relPos.VectorMag()
            self.acceleration += relPos.VectorNorm() * accelScalar

    def CheckCollision(self):
        for body in self.world.bodies:
            if(body.mass>self.mass):
                continue
            if (body.mass == self.mass):
                if int(body.ID) >= int(self.ID):
                    continue

                #print("calling")
            if self.shape == "circle" and body.shape == "circle":
                relPos = body.position - self.position
                if self.mass + body.mass > relPos.VectorMag():
                    # print(f"Planet {self.ID} has collied with planet {body.ID}")

                    normal = relPos.VectorNorm()
                    delVelocity = self.velocity - body.velocity
                    reflectedSelfVector = normal * 2 * body.mass/(self.mass + body.mass)*delVelocity.VectorDot(normal)
                    reflectedBodyVector = normal * -2 * self.mass/(self.mass + body.mass)*delVelocity.VectorDot(normal)

                    self.velocity -= reflectedSelfVector# * -direction
                    body.velocity -= reflectedBodyVector

                    self.position -= normal
                    body.position += normal

        return None, None



def Main():
    myWorld = World(gravity=5, speed=2)
    myWorld.AddBody(MassBody(5, position=[700, 500], velocity=[-1, 0]))
    myWorld.AddBody(MassBody(5, position=[800, 800], velocity=[-1, 0]))
    for i in range(5):
        myWorld.AddBody(MassBody(random.randrange(1, 5), position=[200*i, 800], velocity=[random.randrange(0,100)/50, 0]))
    myWorld.AddBody(MassBody(20, position=[900, 600], velocity=[0, 1]))
    myWorld.AddBody(MassBody(20, position=[800, 500], velocity=[0, 1]))
    myWorld.AddBody(MassBody(100, position=[500, 500], velocity=[-0, 0]))

    myWorld.Tick()
    myWorld.window.mainloop()


if __name__ == '__main__':

    # a = Vector2(5, 6)
    # print(a*float(5))

    Main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
