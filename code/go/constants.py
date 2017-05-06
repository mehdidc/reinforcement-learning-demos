W, B, E = 'W', 'B', 'E'
directions = right, left, up, down = (1, 0), (-1, 0), (0, 1), (0, -1)
X, Y = 0, 1
noop = None
def other(player):
    return {W: B, B: W, E: E}[player]

def nice_coord(coord):
    return (("ABCDEFGHI")[coord[X]], coord[Y] + 1)
