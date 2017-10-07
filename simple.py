from structs import TileContent
from structs import Point

def find_minerals(map, pos):
    minerals = [j for i in map for j in i if j.Content == TileContent.Resource]
    return min([Point.Distance(pos, Point(tile.X, tile.Y)) for tile in minerals])

def walkable(pos):
    if pos.Content in [TileContent.House, TileContent.Lava, TileContent.Shop, TileContent.Wall]:
        return False

def print_map(map):
    for i in map:
        for j in i:
            print(j.Content, end='')
        print(' ')
