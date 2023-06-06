from enum import Enum, auto

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    delta_time: float = 3

    mass: int = 20

    velocity: Vector2 = Vector2(1, 1)

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)

def sum_vec2(list: list[Vector2]) -> Vector2:
    result = Vector2(0, 0)
    for vec in list:
        result += vec
    return result

class Bird(Agent):
    config: FlockingConfig

    max_v = Vector2(2, 2)

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        # move is velocity 
        #self.pos += self.move
        neighbors = list(self.in_proximity_accuracy().without_distance())

        neighbor_count = len(neighbors)

        a, c, s = self.config.weights()

        if neighbor_count != 0:

            pos_arr = [agent.pos for agent in neighbors]

            vec_arr = [agent.move for agent in neighbors]

            #avg_x = sum(agent.move[0] for agent in close) / neighbor_count - self.move[0]
            #avg_y = sum(agent.move[1] for agent in close) / neighbor_count - self.move[1]

            ave_v = sum_vec2(vec_arr) / neighbor_count

            alignment = (ave_v - self.move) * a

            #sep_x = sum(self.pos[0] - agent.pos[0] for agent in close)
            #sep_y = sum(self.pos[1] - agent.pos[1] for agent in close)

            seperation = Vector2(0, 0)

            for neighbor in neighbors:
                seperation -= neighbor.pos - self.pos

            seperation *= s
            
            #avg_pos_x = sum(agent.pos[0] for agent in close) / neighbor_count
            #avg_pos_y = sum(agent.pos[1] for agent in close) / neighbor_count

            #f_c_x = avg_pos_x - self.pos[0]
            #f_c_Y = avg_pos_y - self.pos[1]

            #c_x = f_c_x - self.move[0]
            #c_y = f_c_Y - self.move[1]

            

            center = sum_vec2(pos_arr) / neighbor_count
            cohesion = (center - self.pos) * c

            #cohesion = Vector2(c_x, c_y)


            #f_total_x = (a * avg_x + c * c_x + sep_x * s) / self.config.mass
            #f_total_y = (a * avg_y + c * c_y + sep_y * s) / self.config.mass

            #f_total = Vector2(f_total_x, f_total_y)

            self.move += alignment + seperation + cohesion
            self.move = self.move.normalize()

            #if self.move.magnitude() > 2:
            #    self.move = self.move.normalize() * 2
            self.pos += self.move

        else:

            self.pos += self.move

        #for agent, dist in close:
        #    print(agent.move)
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

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")

config = FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
            visualise_chunks=True
        )

x, y = config.window.as_tuple()

(
    FlockingLive(config)
    .batch_spawn_agents(100, Bird, images=["images/medium-bird.png"])
    #.spawn_obstacle("images/bubble-full.png", x // 2, y // 2)
    .run()
)


