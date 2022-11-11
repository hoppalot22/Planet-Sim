#import pygame as pg
import os
import random
import math
import time
import tkinter as tk

running = True
worlds = []


def VectorMag(vector):
    mag = 0
    for component in vector:
        mag = math.sqrt(mag * mag + component * component)
    return mag


def VectorNorm(vector):
    mag = VectorMag(vector)
    if mag == 0:
        return Vector2(0,0)
    return Vector2(vector.x/mag, vector.y/mag)


def VectorDot(vec1, vec2):
    return vec1.x*vec2.x+vec1.y*vec2.y


class Vector2:
    def __init__(self, x, y):

        self.x = float(x)
        self.y = float(y)

        self.components = [x, y]

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

        self.window = tk.Tk()
        self.window.title(f'Physics: {self.ID}')
        self.canvas = tk.Canvas(self.window, width=self.boundaries[0], height=self.boundaries[1])
        self.canvas.pack()

    def Tick(self):

        for body in self.bodies:
            body.UpdateAccel()
            body.UpdateVelocity()
            body.UpdatePosition()
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
            if body.position is None:
                body.position = [int(self.boundaries[0] / 2), int(self.boundaries[1] / 2)]

        else:
            raise Exception("Only MassBodies may be added to Worlds")

    def RenderWorld(self):
        self.canvas.delete("all")
        for body in self.bodies:
            self.canvas.create_oval(body.position[0] - body.mass, body.position[1] - body.mass,
                                    body.position[0] + body.mass, body.position[1] + body.mass)
            if not (body.acceleration[0] == 0 and body.acceleration[1] == 0):
                self.canvas.create_line(body.position[0], body.position[1],body.position[0]+max(20,body.mass)*body.acceleration[0]/VectorMag(body.acceleration), body.position[1]+max(20,body.mass)*body.acceleration[1]/VectorMag(body.acceleration), fill='blue')
            if not (body.velocity[0] == 0 and body.velocity[1] == 0):
                self.canvas.create_line(body.position[0], body.position[1],body.position[0]+max(20,body.mass)*body.velocity[0]/VectorMag(body.velocity), body.position[1]+max(20,body.mass)*body.velocity[1]/VectorMag(body.velocity), fill='green')


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
        proposed_position = self.position + self.velocity
        collision_point, col_body = self.CheckCollision()
        if collision_point is not None:
            var1 = 2*VectorDot(self.velocity, VectorNorm(collision_point))
            var2 = VectorNorm(collision_point)

            selfVelocityMag = VectorMag(self.velocity)
            bodyVelocityMag = VectorMag(col_body.velocity)

            M1 = self.mass*selfVelocityMag + bodyVelocityMag*col_body.mass
            K1 = selfVelocityMag*selfVelocityMag*self.mass + bodyVelocityMag*bodyVelocityMag*col_body.mass
            a = K1 - col_body.mass-col_body.mass*col_body.mass
            b = 2*M1*col_body.mass/self.mass
            c = -1*M1/self.mass

            new_body_velocity = (-1*b + math.sqrt(max(b*b-4*a*c, 0)))/(2*a)
            new_self_velocity = (M1 - col_body.mass*new_body_velocity)/self.mass

            self.velocity = VectorNorm(self.velocity - var2*var1)*new_self_velocity/2
            self.position += self.velocity
        else:
            self.position = proposed_position

    def UpdateVelocity(self):
        self.velocity += self.acceleration

    def UpdateAccel(self):
        self.acceleration = Vector2(0,0)
        for body in self.world.bodies:
            if body is self:
                continue
            relPos = body.position - self.position
            if VectorMag(relPos) < 0.8 * (self.mass + body.mass):
                continue
            accelScalar = self.world.gravity * body.mass / (VectorMag(relPos)) / (VectorMag(relPos))
            self.acceleration += VectorNorm(relPos) * accelScalar

    def CheckCollision(self):
        for body in self.world.bodies:
            if body is self:
                continue
            else:
                if self.shape == "circle" and body.shape == "circle":
                    relPos = body.position - self.position
                    if self.mass + body.mass > VectorMag(relPos):
                        print(f"Planet {self.ID} has collied with planet {body.ID}")
                        return VectorNorm(relPos)*self.mass, body
        return None, None



def Main():
    myWorld = World(gravity=5, speed=2)
    myWorld.AddBody(MassBody(20, position=[700, 500], velocity=[0, 0]))
    myWorld.AddBody(MassBody(20, position=[900, 500], velocity=[0, 0]))
    for i in range(5):
        myWorld.AddBody(MassBody(random.randrange(3, 10), position=[200*i, 800], velocity=[-.02*random.randrange(0, 100), 0]))
    myWorld.AddBody(MassBody(4, position=[900, 600], velocity=[0, 1]))
    # myWorld.AddBody(MassBody(20, position=[800, 500], velocity=[0, 1]))
    myWorld.AddBody(MassBody(100, position=[500, 500], velocity=[0, -0.2]))

    myWorld.Tick()
    myWorld.window.mainloop()


if __name__ == '__main__':

    # a = Vector2(5, 6)
    # print(a*float(5))

    Main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
