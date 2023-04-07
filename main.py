# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing
from math import sqrt, pow
from statistics import mean


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
  print("INFO")

  return {
    "apiversion": "1",
    "author": "",  # TODO: Your Battlesnake Username
    "color": "#7F171F",  # TODO: Choose color
    "head": "earmuffs",  # TODO: Choose head
    "tail": "weight",  # TODO: Choose tail
  }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
  print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
  print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

  is_move_safe = {"up": True, "down": True, "left": True, "right": True}
  backup_move = 'down'
  # We've included code to prevent your Battlesnake from moving backwards
  my_head = game_state["you"]["body"][0]  # Coordinates of your head
  my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

  if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
    is_move_safe["left"] = False

  elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
    is_move_safe["right"] = False

  elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
    is_move_safe["down"] = False

  elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
    is_move_safe["up"] = False

  # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
  board_width = game_state['board']['width']
  board_height = game_state['board']['height']

  if my_head['x'] == board_width - 1:
    is_move_safe["right"] = False

  elif my_head['x'] == 0:
    is_move_safe["left"] = False

  if my_head["y"] == board_height - 1:
    is_move_safe["up"] = False

  elif my_head["y"] == 0:
    is_move_safe["down"] = False

  # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
  my_body = game_state['you']['body']

  for part in my_body[:-1]:
    if my_head['x'] == part['x'] - 1 and my_head['y'] == part['y']:
      is_move_safe["right"] = False

    elif my_head['x'] == part['x'] + 1 and my_head['y'] == part['y']:
      is_move_safe["left"] = False

    if my_head['y'] == part['y'] - 1 and my_head['x'] == part['x']:
      is_move_safe["up"] = False

    elif my_head['y'] == part['y'] + 1 and my_head['x'] == part['x']:
      is_move_safe["down"] = False

  # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
  opponents = game_state['board']['snakes']
  for opponent in opponents:
    op_head = opponent['head']
    if op_head != my_head:
      for part in opponent['body'][:-1]:
        if my_head['y'] == part['y']:
          if my_head['x'] == part['x'] - 1:
            is_move_safe["right"] = False

          elif my_head['x'] == part['x'] + 1:
            is_move_safe["left"] = False

        if my_head['x'] == part['x']:
          if my_head['y'] == part['y'] - 1:
            is_move_safe["up"] = False

          elif my_head['y'] == part['y'] + 1:
            is_move_safe["down"] = False

      if is_opponent_head_close(
          my_head, op_head) and opponent['length'] >= len(my_body):
        if my_head['x'] == op_head['x']:
          if my_head['y'] < op_head['y']:
            is_move_safe["up"] = False
          elif my_head['y'] > op_head['y']:
            is_move_safe["down"] = False

        elif my_head['y'] == op_head['y']:
          if my_head['x'] < op_head['x']:
            is_move_safe["right"] = False
          elif my_head['x'] > op_head['x']:
            is_move_safe["left"] = False

        else:
          if op_head['x'] > my_head['x']:
            is_move_safe["right"] = False
            backup_move = 'right'
          elif op_head['x'] < my_head['x']:
            is_move_safe["left"] = False
            backup_move = 'left'

          if op_head['y'] > my_head['y']:
            is_move_safe["up"] = False
            backup_move = 'up'
          elif op_head['y'] < my_head['y']:
            is_move_safe["down"] = False
            backup_move = 'down'

  # Are there any safe moves left?
  safe_moves = []
  for move, isSafe in is_move_safe.items():
    if isSafe:
      safe_moves.append(move)

  if len(safe_moves) == 0:
    print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
    return {"move": backup_move}

  # Choose a random move from the safe ones
  next_move = random.choice(safe_moves)

  # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
  food = game_state['board']['food']
  minimum = get_distance(my_head, food[0])
  target = food[0]

  for f in food:
    if get_distance(my_head, f) < minimum:
      print(target)
      minimum = get_distance(my_head, f)
      target = f

  width = game_state['board']['width']
  height = game_state['board']['height']
  opponents = game_state['board']['snakes']
  for opponent in opponents:
    op_len = opponent['length']
    if op_len < len(my_body) - 5 and game_state['you']['health'] > 30:
      target = opponent['head']

  left_free = num_surrounding_free({
    'x': my_head['x'] - 1,
    'y': my_head['y']
  }, opponents, width, height)
  right_free = num_surrounding_free({
    'x': my_head['x'] + 1,
    'y': my_head['y']
  }, opponents, width, height)
  up_free = num_surrounding_free({
    'x': my_head['x'],
    'y': my_head['y'] - 1
  }, opponents, width, height)
  down_free = num_surrounding_free({
    'x': my_head['x'],
    'y': my_head['y'] + 1
  }, opponents, width, height)
  if is_deadend(safe_moves):
    print('Reached deadend')
    print('Up:', up_free)
    print('Down:', down_free)
    if 'left' in safe_moves:
      if left_free > right_free:
        safe_moves.remove('right')
      else:
        safe_moves.remove('left')

    if 'up' in safe_moves:
      print('Up:', up_free)
      print('Down', down_free)
      if up_free > down_free:
        safe_moves.remove('up')
      else:
        safe_moves.remove('down')

  if len(safe_moves) == 1:
    next_move = safe_moves[0]
  else:
    if (my_head['x'] > target['x']) and 'left' in safe_moves:
      next_move = 'left'
    elif my_head['x'] < target['x'] and 'right' in safe_moves:
      next_move = 'right'

    if my_head['y'] > target['y'] and 'down' in safe_moves:
      next_move = 'down'
    elif my_head['y'] < target['y'] and 'up' in safe_moves:
      next_move = 'up'

  print(f"MOVE {game_state['turn']}: {next_move}")
  return {"move": next_move}


def get_distance(p1, p2):
  return sqrt(pow(pow(p1['x'] - p2['x'], 2) + pow(p1['y'] - p2['y'], 2), 2))


def is_opponent_head_close(my_head, op_head):
  if (abs(my_head['x'] - op_head['x']) <= 1
      and abs(my_head['y'] - op_head['y']) <= 1) or (
        my_head['x'] == op_head['x'] and abs(my_head['y'] - op_head['y'])
        == 2) or (my_head['y'] == op_head['y']
                  and abs(my_head['x'] - op_head['x']) == 2):
    return True
  return False


def num_surrounding_free(p1, snakes, width, height):
  x_min = p1['x'] - 1
  x_max = p1['x'] + 1
  y_min = p1['y'] - 1
  y_max = p1['y'] + 1
  if x_min < 0: x_min = 0
  if x_min > width: x_max = width
  if y_min < 0: y_min = 0
  if y_min > height: y_max = height
  count = 0
  surrounding = []
  for x in range(x_min, x_max + 1):
    for y in range(y_min, y_max + 1):
      surrounding.append({'x': x, 'y': y})
  for snake in snakes:
    for part in snake['body']:
      if part not in surrounding:
        count = count + 1
  return count


def is_deadend(safe_moves):
  return 'left' in safe_moves and 'right' in safe_moves and len(
    safe_moves) == 2 or 'up' in safe_moves and 'down' in safe_moves and len(
      safe_moves) == 2


def is_body_mostly(x_or_y, body):
  return mean([(body[0][x_or_y] - body[i][x_or_y])
               for i in range(1, len(body))])


# Start server when `python main.py` is run
if __name__ == "__main__":
  from server import run_server

  run_server({"info": info, "start": start, "move": move, "end": end})
