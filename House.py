from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random

class House(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.width = 3
        self.height = 2
        self.x = (unique_id*10 + 3)
        self.y = 2
        self.owner = None
        self.compromised = False    # if the stealing agent has compromised the house, they can get in.
        self.covers_pos = self.position_covered_by_house()
        self.adjacent_included = self.circle_around_house()

    def set_owner(self, agent):
        house = self
        self.owner = agent
        agent.set_house_owner(house)

    def get_owner(self):
        return self.owner

    def set_compromised(self):
        self.compromised = True

    def position_covered_by_house(self):
        min_x = self.x - 2 # why? TODO
        min_y = self.y - 1
        max_x = self.x + self.width
        max_y = self.y + self.height

        list_of_positions = []

        for i in range(min_x, max_x):
            for j in range(min_y, max_y):
                list_of_positions.append((i, j))

        return list_of_positions

    def circle_around_house(self):
        min_x = self.x - 3  # why? TODO
        min_y = self.y - 2
        max_x = self.x + self.width + 1
        max_y = self.y + self.height + 1

        list_of_positions = []

        for i in range(min_x, max_x):
            for j in range(min_y, max_y):
                list_of_positions.append((i, j))

        return list_of_positions



    def step(self):
        pass