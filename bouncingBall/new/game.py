import turtle as t
import random
import time

ballSpeed = 9
paddleSpeed = 40

STONE_COLOR = ["green", "dark blue", "red", "pink", "violet", "yellow",
                "orange", "gray", "brown", "white", "blue", "yellow green",
                "navajo white", "dark gray", "violet red", "powder blue", "blue violet"]

class Game():
    def __init__(self):
        self.done = False
        self.reward = 0
        self.hit, self.miss = 0, 0

        # Setup Background

        self.win = t.Screen()
        self.win.title('Paddle')
        self.win.bgcolor('black')
        self.win.setup(width=600, height=600)
        self.win.tracer(0)
        self.win.onkey(self.paddle_right, 'Right')
        self.win.onkey(self.paddle_left, 'Left')
        self.win.listen()
        # Paddle

        self.paddle = t.Turtle()
        self.paddle.speed(0)
        self.paddle.shape('square')
        self.paddle.shapesize(stretch_wid=1, stretch_len=5)
        self.paddle.color('white')
        self.paddle.penup()
        self.paddle.goto(0, -275)
        
        # Ball

        self.ball = t.Turtle()
        self.ball.speed(0)
        self.ball.shape('circle')
        self.ball.color('red')
        self.ball.penup()
        # Random ball start position
        randomX = random.randint(-290, 290)
        self.ball.goto(randomX, 100)
        self.ball.dx = ballSpeed
        self.ball.dy = -ballSpeed

        # Score

        self.score = t.Turtle()
        self.score.speed(0)
        self.score.color('white')
        self.score.penup()
        self.score.hideturtle()
        self.score.goto(0, 250)
        self.score.write("Hit: {}   Missed: {}".format(self.hit, self.miss), align='center', font=('Courier', 24, 'normal'))

        # Stones
        self.stones = getStones()

    def paddle_right(self):
        if self.paddle.xcor() < 225:
            self.paddle.setx(self.paddle.xcor() + paddleSpeed)
    
    def paddle_left(self):
        if self.paddle.xcor() > -225:
            self.paddle.setx(self.paddle.xcor() - paddleSpeed)

    def run_frame(self, render):
        if render:
            self.win.update()
            
        # Ball movement
        self.ball.setx(self.ball.xcor() + self.ball.dx)
        self.ball.sety(self.ball.ycor() + self.ball.dy)

        # Border Wall checking
        if self.ball.xcor() > 290:
            self.ball.setx(290)
            self.ball.dx *= -1
        
        if self.ball.xcor() < -290:
            self.ball.setx(-290)
            self.ball.dx *= -1

        if self.ball.ycor() > 290:
            self.ball.sety(290)
            self.ball.dy *= -1

        # Ball Ground checking
        if self.ball.ycor() < -290:
            self.ball.goto(0, 100)
            self.miss += 1
            self.score.clear()
            self.score.write("Hit: {}   Missed: {}".format(self.hit, self.miss), align='center', font=('Courier', 24, 'normal'))
            self.reward -= 3
            self.done = True

        # Ball paddle checking
        if abs(self.ball.ycor() + 250) < 2 and abs(self.paddle.xcor() - self.ball.xcor()) < 55:
            self.ball.dy *= -1
            self.hit += 1
            self.score.clear()
            self.score.write("Hit: {}   Missed: {}".format(self.hit, self.miss), align='center', font=('Courier', 24, 'normal'))
            self.reward += 3
        
        # Ball stone checking
        hasStoneHit = False
        for stone in self.stones:
            if abs(stone.ycor() - self.ball.ycor()) < 20 and abs(stone.xcor() - self.ball.xcor()) < 20:
                print("Stone hit")
                hasStoneHit = True
                stone.color(random.choice(STONE_COLOR))
                self.reward += 0.3
                self.stones.remove(stone)
        if hasStoneHit:
            self.ball.dy *= -1
                

        
    def reset(self):
        self.paddle.goto(0, -275)
        # Random ball start position
        randomX = random.randint(-290, 290)
        self.ball.goto(randomX, 100)
        # Random ball start direction
        randXDir = random.randint(0, 1)
        randYDir = random.randint(0, 1)
        if randXDir == 0:
            self.ball.dx = -ballSpeed
        else:
            self.ball.dx = ballSpeed
        if randYDir == 0:
            self.ball.dy = -ballSpeed
        else:
            self.ball.dy = ballSpeed
        self.stones = getStones()
        return [self.paddle.xcor()*0.01, self.ball.xcor()*0.01, self.ball.ycor()*0.01, self.ball.dx, self.ball.dy]

    def step(self, action, render=False):
        self.reward = 0
        self.done = False

        if action == 0:
            self.paddle_left()
            self.reward -= 0.1
        elif action == 2:
            self.paddle_right()
            self.reward -= 0.1
        # Current time
        start = time.time()
        self.run_frame(render)
        end = time.time()
        diff = end - start
        print("Time: {}".format(diff))
        state = [self.paddle.xcor()*0.01, self.ball.xcor()*0.01, self.ball.ycor()*0.01, self.ball.dx, self.ball.dy]
        return self.reward, state, self.done

def getStones():
    stones = []
    for i in range(0, 5):
        # b = []
        for j in range(0, 19):
            random.shuffle(STONE_COLOR)
            tmp = t.Turtle()
            tmp.speed(0)
            tmp.shape('square')
            tmp.shapesize(stretch_wid=1, stretch_len=1)
            tmp.color(STONE_COLOR[0])
            tmp.penup()
            column = -280 + j*30
            row = 250 - i*20
            tmp.goto(column, row)
            # tmp.goto(i * -100, j * -10)
            # b.append(tmp)
            stones.append(tmp)
        # stones.append(b)
    return stones   

# env = Game()

# while True:
#      env.run_frame()