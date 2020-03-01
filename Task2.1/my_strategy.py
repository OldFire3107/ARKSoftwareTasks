import model
import random
import numpy as np
import math

max_health = 0
flag = 0
prev_x = 0

class PriorityQueue(object): 
    def __init__(self): 
        self.queue = [] 
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 
  
    # for checking if the queue is empty 
    def isEmpty(self): 
        return len(self.queue) == [] 
  
    # for inserting an element in the queue 
    def insert(self, data): 
        self.queue.append(data) 
  
    # for popping an element based on Priority 
    def delete(self): 
        try: 
            max = 0
            for i in range(len(self.queue)): 
                if self.queue[i] > self.queue[max]: 
                    max = i 
            item = self.queue[max] 
            del self.queue[max] 
            return item 
        except IndexError: 
            print("Index Error") 
            exit() 

class PathFinderNode:
    F = None
    PX = None
    PY = None
    Status = None
    PZ = None
    G = None
    JumpLegnth = None

    def UpdateStatus(self, newStatus):
        newNode = self
        self.Status = newStatus
        return newNode

class AStar:

    PQ = PriorityQueue()
    touchedLocations = []
    nodes = []
    Open = []
    Stop = False
    Stopped = True
    HeuristicEstimate = 2
    grid = None
    gridX = None
    gridY = None
    OpenNodeValue = 1
    CloseNodeValue = 1
    Found = False

    def __init___(self):     
        pass

    def FindPathFast(self, game):
        self.grid = game.level
        self.gridX = self.grid.shape(1)       # took 1 as x
        self.gridY = self.grid.shape(0)       # took 0 as y
        self.gridXLog2 = math.log(self.gridX)
        self.gridYLog2 = math.log(self.gridY)

    def FindPathStop(self):
        self.Stop = True

    def FindPath(self, start, end):
        while(len(self.touchedLocations) > 0):
            self.nodes[self.touchedLocations.pop()].clear()

        self.Found = False
        self.Stop = False
        self.Stopped = False
        self.CloseNodeCounter = 0
        self.OpenNodeValue += 2
        self.CloseNodeCounter += 2
        self.Open.clear()

        firstNode = PathFinderNode()
        firstNode.G = 0
        firstNode.F = self.HeuristicEstimate
        firstNode.PX = start.x
        firstNode.PY = start.y 
        firstNode.PZ = 0
        firstNode.Status = OpenNodeValue
        firstNode.JumpLegnth = 0

        


class MyStrategy:
    def __init__(self):
        pass

    def get_action(self, unit, game, debug):
        global max_health
        global flag
        global prev_x

        #   Declaration of constants

        mine = False
        weapon_change = False
        shoot_e = True
        target_pos = unit.position
        if unit.health > max_health:
            max_health = unit.health

        #   Determining nearest entities to pickup

        def distance_sqr(a, b):
            return (a.x - b.x)**2 + (a.y - b.y)**2
        nearest_enemy = min(
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key = lambda u: distance_sqr(u.position, unit.position),
            default = None
        )
        nearest_weapon = min(
            filter(lambda box : isinstance(
                box.item, model.Item.Weapon), game.loot_boxes
            ),
            key = lambda box: distance_sqr(box.position, unit.position),
            default = None
        )
        nearest_mine = min(
            filter(lambda box: isinstance(
                box.item, model.Item.Mine), game.loot_boxes
            ),
            key = lambda box: distance_sqr(box.position, unit.position),
            default = None
        )
        nearest_health = min(
            filter(lambda box: isinstance(
                box.item, model.Item.HealthPack), game.loot_boxes
            ),
            key = lambda box: distance_sqr(box.position, unit.position),
            default = None
        )
        #   Deciding target
        
        if unit.weapon is None and nearest_weapon is not None:
            target_pos = nearest_weapon.position
        elif nearest_enemy is not None:
            target_pos = nearest_enemy.position

        if nearest_health is not None and unit.health <= max_health*0.7:
            target_pos = nearest_health.position

        print(int(nearest_weapon.item.weapon_type))

        debug.draw(model.CustomData.Log("Target pos: {}".format(target_pos)))
        debug.draw(model.CustomData.Log("Current pos: {}".format(unit.position)))
        debug.draw(model.CustomData.Log("Opponent position: {}".format(nearest_enemy.position)))
        aim = model.Vec2Double(0,0)
        if nearest_enemy is not None:
            aim = model.Vec2Double(
                nearest_enemy.position.x - unit.position.x,
                nearest_enemy.position.y - unit.position.y
            )
        if unit.weapon is not None and nearest_mine is not None:
            if distance_sqr(nearest_mine.position, unit.position) < 100:
                target_pos = nearest_mine.position
        
        if unit.weapon is not None and nearest_weapon is not None:
            if int(nearest_weapon.item.weapon_type) > int(unit.weapon.typ):
                target_pos = nearest_weapon.position
                weapon_change = True
        
        jump = target_pos.y > unit.position.y

        if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
            if unit.weapon is not None and unit.weapon.last_angle > 0:
                print(unit.weapon.last_angle)
                shoot_e = False
            jump = True

        if target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            if unit.weapon is not None and unit.weapon.last_angle > 0:
                shoot_e = False
            jump = True
        
        vel = target_pos.x - unit.position.x

        # if unit.weapon is not None and unit.weapon.last_angle is not None:
        #     if unit.weapon.last_angle < 0 and game.level.tiles[int(unit.position.x)][int(unit.position.y-1)] == model.Tile.WALL:
        #         if unit.position.x < nearest_enemy.position.x and game.level.tiles[int(unit.position.x-1)][int(unit.position.y-1)] == model.Tile.WALL:
        #             shoot_e = False
        #         elif unit.position.x > nearest_enemy.position.x and game.level.tiles[int(unit.position.x+1)][int(unit.position.y-1)] == model.Tile.WALL:
        #             shoot_e = False

        isRetracing = False
        if distance_sqr(unit.position, nearest_enemy.position) < 9:
            flag = 1

        if flag:
            isRetracing = True
            vel = vel*(-1)
            if abs(vel) < 2:
                vel = vel * 10

        if unit.mines is not None and isRetracing:
            mine = True

        if flag and distance_sqr(unit.position, nearest_enemy.position) > 64:
            flag = 0     
        
        # print("{}   {}   {}".format(unit.jump_state.max_time, unit.jump_state.speed, unit.jump_state.max_time * unit.jump_state.speed))

        if unit.jump_state.max_time > 0 and unit.jump_state.max_time == 5.5:
            max_height = unit.jump_state.max_time * unit.jump_state.speed
            for i in range(int(max_height)):
                if unit.position.y+i<28 and game.level.tiles[int(unit.position.x)][int(unit.position.y+i)] == model.Tile.WALL:
                    print("%%%%%%%%%%%%%%%%%%%%%%%%")
                    target_pos.x = random.randint(int(unit.position.x)-20 ,int(unit.position.x)+20)
                    target_pos.y = unit.position.y
        
        if target_pos.y > unit.jump_state.max_time * unit.jump_state.speed:
            print("*****************")
            jump = True
            if vel < 0 and game.level.tiles[int(unit.position.x-1)][int(unit.position.y)] == model.Tile.WALL:
                target_pos.x = random.randint(int(unit.position.x) ,int(unit.position.x)+20)
            if vel > 0 and game.level.tiles[int(unit.position.x+1)][int(unit.position.y)] == model.Tile.WALL:
                target_pos.x = random.randint(int(unit.position.x)-20 ,int(unit.position.x))
            else:
                target_pos.x = random.randint(int(unit.position.x)-20 ,int(unit.position.x)+20)
            target_pos.y = unit.position.y



        return model.UnitAction(
            velocity = vel,
            jump = jump,
            jump_down = not jump,
            aim = aim,
            shoot = shoot_e,
            reload = False,
            swap_weapon = weapon_change,
            plant_mine = mine
        )