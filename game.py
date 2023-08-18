from random import random
import pygame
from time import time
from random import *
import random
from main import branching_and_bounding

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
SILVER = (192, 192, 192)
LIME = (124, 255, 0)

# Initialize the game
pygame.init()

enabled = 20*[False]

# Creating the screen
screen = pygame.display.set_mode((1245, 636))

maxCapBarrier = 1

class Button:
    """Create a button, then blit the surface in the while loop"""

    def __init__(self, text,  pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg)

    def change_text(self, text, bg="black"):
        """Change the text whe you click"""
        self.text = self.font.render(text, 1, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self, x):
        screen.blit(x.surface, (self.x, self.y))

    def click(self, event, idx):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    enabled[idx] ^= True
class Signal:
    def __init__(self, isRed, road_no, coors, barrier):
        self.coors = coors
        self.isRed = isRed
        self.road_no = road_no
        self.wait_time = 0
        self.number_of_cars = 0
        self.barrier = list(barrier).copy()
        self.static_barrier = list(barrier).copy()
        self.cap_of_barrier = 0
        self.hori_delta = 0
        self.veri_delta = 0
        self.counter = 0
        self.queue = []

    def reset(self):
        self.cap_of_barrier = maxCapBarrier

    def extend_barrier(self, h_del, v_del):
        self.barrier[0][0] += h_del
        self.barrier[1][0] += h_del
        self.barrier[0][1] += v_del
        self.barrier[1][1] += v_del

    # def __str__(self) -> str:
    #     return str()


class Car:
    def __init__(self, coorX, coorY, direction, color, signal_no):
        # Current coordinates of the car
        self.coorX = coorX
        self.coorY = coorY

        # the direction in which the car is moving
        self.direction = direction

        # flag to stop the car when the signal is red
        self.stop = False

        # whether the car has passed the padding region
        self.toChange = False

        # if it has crossed the padding region then in which direction it should move
        self.nextDirection = "?"

        # if it has crossed the padding region then after what distance the direction should change
        self.nextChangeDistance = 0

        # the color of the car
        self.color = color

        # in which signal the car is standing
        self.signal_no = signal_no

        # number of signal after the direction is changed
        self.next_signal_no = -1

        self.wait = False


def draw_lines(lines):
    for line in lines:
        pygame.draw.line(screen, (0, 0, 0), line[0], line[1], 2)


class Padding:
    def __init__(self, fPoint, sPoint, padDist, directionList):
        self.fPoint = fPoint
        self.sPoint = sPoint
        self.padDist = padDist
        self.directionList = directionList

    def __str__(self) -> str:
        return str(self.fPoint) + str(self.sPoint) + str(self.padDist) + str(self.directionList)

    def draw_hori_padding(self):
        pygame.draw.line(screen, CYAN, self.fPoint, self.sPoint)
        nfPoint = (self.fPoint[0], self.fPoint[1]+self.padDist)
        nsPoint = (self.sPoint[0], self.sPoint[1] + self.padDist)
        pygame.draw.line(screen, CYAN, nfPoint, nsPoint)

    def draw_veri_padding(self):
        pygame.draw.line(screen, CYAN, self.fPoint, self.sPoint)
        nfPoint = (self.fPoint[0] + self.padDist, self.fPoint[1])
        nsPoint = (self.sPoint[0] + self.padDist, self.sPoint[1])
        pygame.draw.line(screen, CYAN, nfPoint, nsPoint)


pygame.display.set_caption("Traffic Control System")

placed_cars = []

# what should be the speed of the cars
speed = 1

horizontal_paddings = []
vertical_paddings = []


def initialize_padding():
    global horizontal_paddings, vertical_paddings
    # padding lines
    # horizontal padding
    hori_padding = [
        # down paddings
        [(75, 170), (105, 170), (("R", (3, -1)), ("R", (3, -1))), 40],
        [(451, 170), (480, 170), (("R", (5, 0)), ("R", (5, 0))), 40],
        [(948, 170), (1005, 170), (("R", (0, -1)), ("D", (7, -1))), 40],
        [(273, 413), (310, 413), (("R", (14, -1)), ("R", (14, -1))), 21],
        [(948, 515), (1007, 515), (("R", (0, -1)), ("D", (0, -1))), 40],
        # upp paddings
        [(274, 260), (234, 260), (("L", (0, -1)), ("L", (0, -1))), -40],
        [(663, 260), (623, 260), (("L", (11, -1)), ("L", (11, -1))), -40],
        [(948, 260), (885, 260), (("L", (9, -1)), ("U", (0, -1))), -40],
        [(663, 468), (628, 468), (("L", (17, -1)), ("U", (10, -1))), -25],
        [(130, 468), (94, 468), (("L", (0, -1)), ("L", (0, -1))), -25]
    ]

    veri_paddings = [
        # Right paddings
        [(44, 214), (44, 170), (("U", (0, -1)), ("R", (3, -1))), 20],
        [(417, 214), (417, 170), (("U", (0, -1)), ("R", (5, 0))), 20],
        [(894, 214), (894, 170), (("U", (0, -1)), ("R", (0, -1))), 40],
        [(238, 438), (238, 410), (("U", (12, -1)), ("U", (12, -1))), 20],
        [(627, 439), (627, 411), (("U", (10, -1)), ("U", (10, -1))), 20],
        # Left paddings
        [(307, 264), (307, 217), (("D", (16, -1)), ("L", (0, -1))), -20],
        [(696, 264), (696, 217), (("D", (0, -1)), ("L", (11, -1))), -20],
        [(1001, 264), (1001, 217), (("D", (7, -1)), ("L", (9, -1))), -40],
        [(1001, 578), (1001, 550), (("D", (0, -1)), ("D", (0, -1))), -20],
        [(162, 471), (162, 440), (("D", (0, -1)), ("L", (0, -1))), -20]
    ]
    for line in hori_padding:
        horizontal_paddings.append(
            Padding(fPoint=line[0], sPoint=line[1], padDist=line[3], directionList=line[2]))
    for line in veri_paddings:
        vertical_paddings.append(
            Padding(fPoint=line[0], sPoint=line[1], padDist=line[3], directionList=line[2]))

from main import flip_signal

signals = []

BARRIER_SPEED = 1

def initialize_signals():
    coordinates = [
        [[36, 192, [-BARRIER_SPEED, 0]],  [[30, 214], [30, 170]]],
        [[92, 154, [0, -BARRIER_SPEED]],  [[74, 160], [108, 160]]],
        [[395, 191, [-BARRIER_SPEED, 0]], [[409, 216], [409, 169]]],
        [[467, 146, [0, -BARRIER_SPEED]], [[451, 163], [480, 163]]],
        [[865, 191, [-BARRIER_SPEED, 0]], [[889, 215], [889, 169]],
         [1020, 240, [BARRIER_SPEED, 0]], [[1009, 216], [1009, 264]]],
        [[975, 156, [0, BARRIER_SPEED]],  [[894, 272], [947, 272]],
         [920, 272, [0, -BARRIER_SPEED]], [[949, 162], [999, 162]]],
        [[975, 480, [0, -BARRIER_SPEED]], [[950, 500], [999, 500]]],
        [[1030, 560, [BARRIER_SPEED, 0]], [[1008, 548], [1008, 577]]],
        [[715, 241, [BARRIER_SPEED, 0]],  [[699, 265], [699, 215]]],
        [[648, 280, [0, BARRIER_SPEED]],  [[627, 272], [667, 272]]],
        [[332, 241, [BARRIER_SPEED, 0]],  [[314, 261], [314, 216]]],
        [[254, 288, [0, BARRIER_SPEED]], [[237, 269], [271, 269]]],
        [[645, 500, [0, BARRIER_SPEED]],  [[628, 480], [663, 480]]],
        [[608, 425, [-BARRIER_SPEED, 0]], [[619, 410], [619, 438]]],
        [[209, 425, [-BARRIER_SPEED, 0]], [[232, 408], [232, 438]]],
        [[290, 387, [0, -BARRIER_SPEED]], [[272, 396], [308, 396]]],
        [[189, 457, [BARRIER_SPEED, 0]],  [[171, 440], [171, 471]]],
        [[115, 497, [0, BARRIER_SPEED]],  [[97, 476], [132, 476]]]
    ]
    cnt = 0
    signals.append(Signal(isRed=False, road_no=0, coors=(
        (-5, -5, (0, 0)), (-5, -5), (0, 0)), barrier=(-10, -10)))
    for cnt in range(1, len(coordinates)+1):
        temp = coordinates[cnt-1]
        if cnt == 5:
            signals.append(Signal(isRed=cnt % 2 == 0, road_no=5, coors=[
                coordinates[cnt-1][0], coordinates[cnt-1][2]], barrier=list([coordinates[cnt-1][1], coordinates[cnt-1][3]])))
            continue
        if cnt == 6:
            signals.append(Signal(isRed=cnt % 2 == 0, road_no=6, coors=[
                coordinates[cnt-1][0], coordinates[cnt-1][2]], barrier=list([coordinates[cnt-1][1], coordinates[cnt-1][3]])))
            continue
        signals.append(Signal(isRed=cnt % 2 == 0, road_no=cnt, coors=(
            (temp[0]), (temp[0][0], temp[0][1], temp[0][2])), barrier=list(temp[1])))


def render_signals():
    for sig in signals:
        for i in sig.coors:
            if sig.isRed:
                pygame.draw.circle(screen, RED, (i[0], i[1]), 20, 30)
                # screen.blit()
            else:
                # screen.blit()
                pygame.draw.circle(screen, GREEN, (i[0], i[1]), 20, 30)


def check_point_on_hor_line(line, point):
    x1 = min(line[0][0], line[1][0])
    x2 = max(line[0][0], line[1][0])
    if point[0] >= x1 and point[0] <= x2 and point[1] == line[0][1]:
        return True
    return False


def check_point_on_ver_line(line, point):
    y1 = min(line[0][1], line[1][1])
    y2 = max(line[0][1], line[1][1])
    if point[1] >= y1 and point[1] <= y2 and point[0] == line[0][0]:
        return True
    return False


def render_existing_cars():
    global placed_cars
    new_placed = []
    for car in placed_cars:
        barrier = signals[car.signal_no[0]].barrier
        x = car.coorX
        y = car.coorY
        pt1 = ()
        pt2 = ()
        displacement = ()
        if car.signal_no[0] == 6 or car.signal_no[0] == 5:
            pt1 = barrier[car.signal_no[1]][0]
            pt2 = barrier[car.signal_no[1]][1]
            displacement = signals[car.signal_no[0]].coors[car.signal_no[1]][2]
        else:
            pt1 = barrier[0]
            pt2 = barrier[1]
            displacement = signals[car.signal_no[0]].coors[0][2]

        crossing = True
        if signals[car.signal_no[0]].isRed:
            if car.direction == 'D' or car.direction == 'U':
                crossing &= check_point_on_hor_line((pt1, pt2), (x, y))
            else:
                crossing &= check_point_on_ver_line((pt1, pt2), (x, y))
        crossing &= signals[car.signal_no[0]].isRed
        if crossing:
            car.wait = True
            signals[car.signal_no[0]].queue.append(signals[car.signal_no[0]].counter)

        if car.wait:
            crossing = signals[car.signal_no[0]].isRed
            car.wait = signals[car.signal_no[0]].isRed
        if not (crossing or car.wait):
            if car.direction == 'U' or car.direction == 'D':
                for padding in horizontal_paddings:
                    if check_point_on_hor_line((padding.fPoint, padding.sPoint), (car.coorX, car.coorY)):
                        car.toChange = True
                        tt = random.choice(padding.directionList)
                        car.nextDirection = tt[0]
                        car.next_signal_no = tt[1]
                        car.nextChangeDistance = randint(
                            3, abs(padding.padDist))
            else:
                for padding in vertical_paddings:
                    if check_point_on_ver_line((padding.fPoint, padding.sPoint), (car.coorX, car.coorY)):
                        car.toChange = True
                        tt = random.choice(padding.directionList)
                        car.nextDirection = tt[0]
                        car.next_signal_no = tt[1]
                        car.nextChangeDistance = randint(
                            3, abs(padding.padDist))
        if car.toChange:
            if car.nextChangeDistance == 0:
                signals[car.signal_no[0]].number_of_cars -= 1
                signals[car.next_signal_no[0]].number_of_cars += 1
                car.direction = car.nextDirection
                car.signal_no = car.next_signal_no
                car.nextDirection = "?"
                car.nextChangeDistance = 0
                car.toChange = False
                car.next_signal_no = 0
            else:
                car.nextChangeDistance -= speed

        if not (crossing or car.wait):
            if car.direction == 'R':
                x += speed
            elif car.direction == 'L':
                x -= speed
            elif car.direction == 'D':
                y += speed
            else:
                y -= speed
        else:
            signals[car.signal_no[0]].cap_of_barrier -= 1
            if signals[car.signal_no[0]].cap_of_barrier <= 0:
                signals[car.signal_no[0]].reset()
                if car.signal_no[0] == 5 or car.signal_no[0] == 6:
                    signals[car.signal_no[0]].barrier = barrier
                else:
                    signals[car.signal_no[0]].barrier = barrier
        hello = 0
        try:
            pygame.draw.line(screen, MAGENTA, tuple(
                barrier[0]), tuple(barrier[1]), 2)
        except:   
            hello = 1
        car.coorX, car.coorY = x, y
        if x > 1245 or x < 0 or y > 636 or y < 0:
            continue
        new_placed.append(car)
        pygame.draw.circle(screen, car.color, (x, y), 5, 5)
    placed_cars = new_placed


valid_points_to_generate = [
    # points where cars can generate added padding
    [(0, 171), (0, 210), "R", (1, -1)],
    [(78, 2), (103, 2), "D", (2, -1)],
    [(2, 412), (2, 435), "R", (15, -1)],
    [(102, 625), (125, 625), "U", (18, -1)],
    [(456, 41), (477, 41), "D", (4, -1)],
    [(955, 41), (996, 41), "D", (6, 1)],
    [(1231, 221), (1231, 256), "L", (5, 1)],
    [(1234, 550), (1233, 573), "L", (8, -1)],
    [(633, 625), (657, 628), "U", (13, -1)],
    [(895, 630), (940, 630), "U", (6, 0)]
]


def rand_car():
    idx = randint(0, len(valid_points_to_generate) - 1)
    if not enabled[idx]:
        return
    line = valid_points_to_generate[idx]
    x, y = -1, -1
    if line[2] == "V":
        x = line[0][0]
        y = randint(min(line[0][1], line[1][1]), max(line[0][1], line[1][1]))
    else:
        y = line[0][1]
        x = randint(min(line[0][0], line[1][0]), max(line[0][0], line[1][0]))
    placed_cars.append(
        Car(coorX=x, coorY=y, direction=line[2], color=BLUE, signal_no=line[3]))
    signals[line[3][0]].number_of_cars += 1

from main import node

def branch_and_bound_caller():
    p = []
    for sig in signals:
        p.append(sig.queue)
    for root in 9:
        active_nodes = []
        temp = node()
        temp.idx = root
        active_nodes.append(temp)
        signals[root].red_time = branching_and_bounding(temp, active_nodes, p)

def draw_valid_points():
    for i in valid_points_to_generate:
        pygame.draw.line(screen, CYAN, i[0], i[1])


def draw_road():
    road = [
        [(0, 170), (42, 170)],
        [(42, 0), (42, 170)],
        [(0, 260), (240, 260)],
        [(0, 410), (240, 410)],
        [(106, 170), (106, 0)],
        [(106, 170), (415, 170)],
        [(415, 0), (415, 170)],
        [(480, 0), (480, 170)],
        [(480, 170), (890, 170)],
        [(890, 170), (890, 0)],
        [(1000, 170), (1000, 0)],
        [(1000, 170), (1240, 170)],
        [(1000, 260), (1240, 260)],
        [(1000, 520), (1240, 520)],
        [(1000, 580), (1240, 580)],
        [(1000, 580), (1000, 630)],
        [(1000, 260), (1000, 520)],
        [(700, 260), (890, 260)],
        [(890, 260), (890, 630)],
        [(700, 260), (700, 630)],
        [(625, 260), (625, 410)],
        [(625, 410), (303, 410)],
        [(303, 410), (303, 260)],
        [(0, 410), (237, 410)],
        [(237, 410), (237, 260)],
        [(237, 260), (0, 260)],
        [(307, 260), (625, 260)],
        [(0, 470), (100, 470)],
        [(100, 470), (100, 630)],
        [(160, 470), (160, 630)],
        [(160, 470), (630, 470)],
        [(630, 470), (630, 630)]
    ]


    road = [
        [[30, 214], [30, 170]],
        [[74, 160], [108, 160]],
        [[409, 216], [409, 169]],
        [[451, 163], [480, 163]],
        [[889, 215], [889, 169]],
        [[1009, 216], [1009, 264]],
        [[894, 272], [947, 272]],
        [[949, 162], [999, 162]],
        [[950, 500], [999, 500]],
        [[1008, 548], [1008, 577]],
        [[699, 265], [699, 237]],
        [[627, 272], [667, 272]],
        [[314, 261], [314, 216]],
        [[237, 269], [271, 269]],
        [[628, 480], [663, 480]],
        [[619, 410], [619, 438]],
        [[232, 408], [232, 438]],
        [[272, 396], [307, 396]],
        [[171, 440], [171, 471]],
        [[97, 476], [132, 476]],
    ]
    for line in road:
        pygame.draw.line(screen, LIME, line[0], line[1])


def extend_barrier():
    for sig in signals:
        if sig.road_no == 5 or sig.road_no == 6 or sig.road_no == 0:
            if sig.road_no != 0:
                sig.barrier[0][0][0] += sig.coors[0][2][0]
                sig.barrier[0][1][0] += sig.coors[0][2][0]
                sig.barrier[0][0][1] += sig.coors[0][2][1]
                sig.barrier[0][1][1] += sig.coors[0][2][1]
                sig.barrier[1][0][0] += sig.coors[1][2][0]
                sig.barrier[1][1][0] += sig.coors[1][2][0]
                sig.barrier[1][0][1] += sig.coors[1][2][1]
                sig.barrier[1][1][1] += sig.coors[1][2][1]
                sig.counter += 1
            continue
        sig.barrier[0][0] += sig.coors[0][2][0]
        sig.barrier[1][0] += sig.coors[0][2][0]
        sig.barrier[0][1] += sig.coors[0][2][1]
        sig.barrier[1][1] += sig.coors[0][2][1]
        sig.counter += 1


def reset_barrier():
    for sig in signals:
        if sig.road_no == 5 or sig.road_no == 6 or sig.road_no == 0:
            if sig.road_no != 0:
                sig.barrier[0][0][0] -= sig.counter*sig.coors[0][2][0]
                sig.barrier[0][1][0] -= sig.counter*sig.coors[0][2][0]
                sig.barrier[0][0][1] -= sig.counter*sig.coors[0][2][1]
                sig.barrier[0][1][1] -= sig.counter*sig.coors[0][2][1]
                sig.barrier[1][0][0] -= sig.counter*sig.coors[1][2][0]
                sig.barrier[1][1][0] -= sig.counter*sig.coors[1][2][0]
                sig.barrier[1][0][1] -= sig.counter*sig.coors[1][2][1]
                sig.barrier[1][1][1] -= sig.counter*sig.coors[1][2][1]
                sig.counter = 0
            continue
        sig.barrier[0][0] -= sig.counter*sig.coors[0][2][0]
        sig.barrier[1][0] -= sig.counter*sig.coors[0][2][0]
        sig.barrier[0][1] -= sig.counter*sig.coors[0][2][1]
        sig.barrier[1][1] -= sig.counter*sig.coors[0][2][1]
        sig.counter = 0


running = True
image = pygame.image.load(r'mywork/road.png')
car = pygame.image.load(r'car_1.png')
start_time = time()

initialize_padding()
initialize_signals()

wait_array = 20*[0]
def flip_caller():
    isRed = flip_signal(wait_array=wait_array)
    for i in range(1, 19):
        signals[i].isRed = isRed[i]
        signals[i].queue = []
        # signals[i].number_of_cars = 0


def increment_wait_time():
    global wait_array
    for sig in signals:
        wait_array[sig.road_no] = sig.number_of_cars

timer = 1
start_time_barrier = time()

button1 = Button(
    "1",
    (214, 509),
    font=30,
    bg="navy",
    feedback="1 disabled"
)
button2 = Button(
    "2",
    (253, 509),
    font=30,
    bg="navy",
    feedback="2 disabled"
)
button3 = Button(
    "3",
    (290, 509),
    font=30,
    bg="navy",
    feedback="3 disabled"
)
button4 = Button(
    "4",
    (330, 509),
    font=30,
    bg="navy",
    feedback="4 disabled"
)
button5 = Button(
    "5",
    (370, 509),
    font=30,
    bg="navy",
    feedback="5 disabled"
)

button6 = Button(
    "6",
    (400, 509),
    font=30,
    bg="navy",
    feedback="1 disabled"
)
button7 = Button(
    "7",
    (430, 509),
    font=30,
    bg="navy",
    feedback="2 disabled"
)
button8 = Button(
    "8",
    (460, 509),
    font=30,
    bg="navy",
    feedback="3 disabled"
)
button9 = Button(
    "9",
    (490, 509),
    font=30,
    bg="navy",
    feedback="4 disabled"
)
button10 = Button(
    "10",
    (520, 509),
    font=30,
    bg="navy",
    feedback="5 disabled"
)

while running:
    screen.blit(image, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        button1.click(event, 1)
        button2.click(event, 2)
        button3.click(event, 3)
        button4.click(event, 4)
        button5.click(event, 5)
        button6.click(event, 6)
        button7.click(event, 7)
        button8.click(event, 8)
        button9.click(event, 9)
    # for padding in horizontal_paddings:
    #     padding.draw_hori_padding()
    # for padding in vertical_paddings:
    #     padding.draw_veri_padding()
    now_time = time()
    button1.show(button1)
    button2.show(button2)
    button3.show(button3)
    button4.show(button4)
    button5.show(button5)
    button6.show(button6)
    button7.show(button7)
    button8.show(button8)
    button9.show(button9)
    if(now_time - start_time > 1):
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        rand_car()
        timer += 1
        increment_wait_time()
        start_time = now_time
    if now_time - start_time_barrier >= 0.2:
        extend_barrier()
        start_time_barrier = now_time
    render_existing_cars()
    render_signals()
    if timer % 7 == 0:
        timer += 1
        flip_caller()
        reset_barrier()
    pygame.display.update()