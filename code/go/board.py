from constants import *
import random
from contextlib import contextmanager
import itertools

def xor(s1, s2):
    if s1 == "":
        return s2
    elif s2 == "":
        return s1
    else:
        return ''.join([chr(ord(c1) ^ ord(c2)) for c1, c2 in zip(s1, s2)])

class Board:
    
    def __init__(self, dimension, content=None):
        self.dimension = dimension
        # default content is empty for all intersections
        if content is None:
            self.__content = [([E] * dimension[X]) for y in xrange(dimension[Y])]
        else:
            self.__content = content
        self.current_hash = ""
        self.zobrist = {}
        self.__init_zobrist()
        self.__recompute_hash()
    
    def clear(self):
        self.__content = [([E] * self.dimension[X]) for y in xrange(self.dimension[Y])]
        self.__recompute_hash()

    def __recompute_hash(self):
        h = ""
        for y in xrange(self.dimension[Y]):
            for x in xrange(self.dimension[X]):
                cell = self.__content[y][x]
                h = xor(h, self.zobrist[(x, y, cell)])
        self.current_hash = h

    def __hash__(self):
        return hash(self.current_hash)

    def __init_zobrist(self):
        for y in xrange(self.dimension[Y]):
            for x in xrange(self.dimension[X]):
                for cell in W, B, E:
                    self.zobrist[(x, y, cell)] = ''.join([random.choice('abcdefghijklmlnopqrstuvwxyz01234567890#?') for i in xrange(5)])

    def get_content(self):
        return tuple(tuple(lig) for lig in self.__content)

    def load_content(self, content):
        self.__content = list(list(lig) for lig in content)
        self.__recompute_hash()
    
    def count(self, player):
        return sum((1 if cell==player else 0) for lig in self.__content for cell in lig)

    def chaines(self, player):

        chaines = []
        visited = set()

        for y in xrange(self.dimension[Y]):
            for x in xrange(self.dimension[X]):
                chaine = self.chaine_starting_from(player, (x, y), visited)
                if chaine:
                    chaines.append(chaine)
        return chaines

    def chaine_starting_from(self, player, start, visited=None):
        if visited is None: visited = set()
        
        if start in visited:
            return []

        visited.add(start)

        if self.content(start) != player:
            return []
        
        chaine = [start]
        for coord in self.voisinage(start):
            chaine.extend(self.chaine_starting_from(player, coord, visited))

        return chaine

    def voisinage(self, coord):
        return ((coord[X] + horiz, coord[Y] + vert) 
                for horiz, vert in directions if self.inside((coord[X] + horiz, coord[Y] + vert)))
    
    def inside(self, coord):
        return coord[X] < self.dimension[X] and coord[Y] < self.dimension[Y] and coord[X] >= 0 and coord[Y] >= 0

    def content(self, coord):
        return self.__content[coord[Y]][coord[X]]
    
    def liberte_groupe(self, group):
        return sum(self.liberte(coord) for coord in group)

    def liberte(self, coord):
        return sum((1 if self.content(coord) == E  else 0) for coord in self.voisinage(coord))
    
    def territoires(self, player):
        territoires = []
        visited = set()
        for y in xrange(self.dimension[Y]):
            for x in xrange(self.dimension[X]):
                territoire = self.territoire_explore(player, (x, y), visited)
                if territoire:
                    if map(lambda coord: self.content(coord), territoire).count(E) == len(territoire):
                        territoires.append(territoire)
        return territoires
    
    def territoire_explore(self, player, start, visited):
        if visited is None: visited = set()

        if self.content(start) == player:
            return []

        if start in visited:
            return []
        visited.add(start)
  
        territoire = [start]
        for vois in self.voisinage(start):
            t = self.territoire_explore(player, vois, visited)
            territoire.extend(t)

        return territoire

    def replace_with(self, group, player):
        self.replace_element_by_element(group, itertools.repeat(player))
    
    def temporary_replace_with(self, group, player):
        return self.temporary_replace_element_by_element(group, itertools.repeat(player))

    def replace_element_by_element(self, group, players):
        for coord, player in zip(group, players):
            old_player = self.__content[coord[Y]][coord[X]]
            self.__content[coord[Y]][coord[X]] = player
            self.current_hash = xor(self.current_hash, self.zobrist[(coord[Y], coord[X], old_player)])
            self.current_hash = xor(self.current_hash, self.zobrist[(coord[Y], coord[X], player)])


    @contextmanager
    def temporary_replace_element_by_element(self, group, players):
        group_content_save = [self.content(coord) for coord in group]
        self.replace_element_by_element(group, players)
        yield self
        self.replace_element_by_element(group, group_content_save)

    def __str__(self):
        s = ""
        for lig in self.__content:
            s += str(lig) + "\n"
        return s

    @staticmethod
    def content_difference(content1, content2):
        return sum((1 if (val1 != val2) else 0)
                    for val1, val2 in zip(lig1, lig2) for lig1, lig2 in zip(content1, content2))

