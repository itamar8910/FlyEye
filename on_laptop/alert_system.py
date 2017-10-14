import math
class Point():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def scalar_mul(self, other):
        return other.x*self.x + other.y*self.y
    def norm(self):
        return self.scalar_mul(self)
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y)+")"
def avg(l):
    return sum(l)/float(len(l))

def point_dis_sqrd(x,y):
    return (x-y).norm()

def vect_mul(p1,p2):
    return p1.x*p2.y - p2.x*p1.y

def distance_3_sqrd(p1, p2, p3):
    a = p2-p1
    b = p3-p1
    c = p3-p2
    if a.scalar_mul(c) <= 0 and b.scalar_mul(c) >= 0:
        return (vect_mul(a,c) ** 2) / c.norm()
    else:
        return min(point_dis_sqrd(p1,p2), point_dis_sqrd(p1,p3))

class Rect:
    def __init__(self, p1, p2, p3, p4):
        self.points = [p1, p2, p3, p4]
        mean = Point(avg([p.x for p in self.points]), avg([p.y for p in self.points]))
        self.points.sort(key=lambda x: math.atan2((x-mean).y, (x-mean).x))

def parallel_rect(x, y, w, h):
    return Rect(Point(x, y), Point(x - w, y), Point(x, y - h), Point(x - w, y - h))


def rects_distance(rect1, rect2):
    distances = []
    for p1 in rect1.points:
        for i in range(len(rect2.points)):
            distances.append(distance_3_sqrd(p1, rect2.points[i], rect2.points[(i+1)%4]))
    return math.sqrt(min(distances))


def is_dangerous(rects_data):
    "returns true if given rects are in a collision danger"
    rects_xywh = [x[2:] for x in rects_data] # ommit class label & probabilty
    THRESH_PERSON = 30
    THRESH_OTHER = 50
    THRESH = THRESH_OTHER
    if rects_xywh is None or len(rects_xywh) < 2:
        return False
    rects = [parallel_rect(r[0],r[1],r[2],r[3]) for r in rects_xywh]
    distances = []
    for i in range(len(rects)):
        for j in range(len(rects)):
            if i==j:
                continue
            distances.append([rects_distance(rects[i],rects[j]), i, j])
    #return min(distances)
    min_dis = min([x[0] for x in distances])
    min_dis_index = ([x[0] for x in distances]).index(min_dis)
    min_dis_i = distances[min_dis_index][1]
    min_dis_j = distances[min_dis_index][2]
    class_i = rects_data[min_dis_i]
    class_j = rects_data[min_dis_j]
    if "person" in [class_i, class_j]:
        THRESH = THRESH_PERSON
    return [min_dis < THRESH, class_i, class_j]
    

#print(rects_distance(Rect(Point(0, 0), Point(0, 1), Point(1, 0), Point(1, 1)), Rect(Point(1.5, 2), Point(3.5, 2), Point(1.5, 10), Point(3.5, 10))))
