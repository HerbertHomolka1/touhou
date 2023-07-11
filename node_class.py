class Node:
    def __init__(self, position, g_cost, h_cost, parent):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent

    def f_cost(self):
        return self.g_cost + self.h_cost


    def __lt__(self, other):
        return self.f_cost() < other.f_cost()