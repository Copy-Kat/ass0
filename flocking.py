from enum import Enum, auto
from polars import select
import pathlib

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
import vi
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    b_weight: float = 0.5
    b_dist: int = 20

    frame_count = 0

    delta_time: float = 3

    mass: int = 20


    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)

def sum_vec2(list: list[Vector2]) -> Vector2:
    result = Vector2(0, 0)
    for vec in list:
        result += vec
    return result



class Bird(Agent):
    config: FlockingConfig

    #i = 0

    def change_position(self):

        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()

        #YOUR CODE HERE -----------

        neighbors = list(self.in_proximity_accuracy().without_distance())

        neighbor_count = len(neighbors)

        a, c, s = self.config.weights()        

        prng = self.shared.prng_move

        should_change_angle = prng.random()

        deg = prng.uniform(-10, 10)

        if neighbor_count != 0:

            pos_arr = [agent.pos for agent in neighbors]

            vec_arr = [agent.move for agent in neighbors]

            ave_v = sum_vec2(vec_arr) / neighbor_count

            alignment = (ave_v - self.move) * a

            seperation = Vector2(0, 0)

            for neighbor in neighbors:
                seperation += self.pos - neighbor.pos

            seperation = seperation / neighbor_count * s

            center = sum_vec2(pos_arr) / neighbor_count
            cohesion = ((center - self.pos) - self.move) * c

            v4 = Vector2(0, 0)

            for i in range(2):
                if self.pos[i] < self.config.b_dist:
                    v4[i] += self.config.b_weight
                elif self.pos[i] > self.config.window.as_tuple()[i] - self.config.b_dist:
                    v4[i] -= self.config.b_weight

            self.move += (alignment + seperation + cohesion + v4)
            self.move = self.move.normalize()

        if 0.7 > should_change_angle:
            self.move.rotate_ip(deg)

        self.pos += self.move

        #END CODE -----------------


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()

class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION
                elif event.key == pg.K_q:
                    self._running = False

        a, c, s = self.config.weights()
        self.config.frame_count += 1
        print("Frame :", self.config.frame_count)
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")

config = FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
            visualise_chunks=True
        )

x, y = config.window.as_tuple()

df = FlockingLive(config).batch_spawn_agents(100, Bird, images=["images/bird.png"]).run().snapshots

print(df)

df.write_csv("new_file.csv", separator=",")
