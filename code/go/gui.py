import sys
import pygame
import time
from constants import *
from board import Board
from game import GameRules, Game
from player import DeterministicPlayer, RandomPlayer, UserInterfacePlayer, MonteCarloPlayer

class GraphicalBoard:
    def __init__(self, board):
        self.board = board
        self.square_dim = (40, 40)
        self.circle_radius = 15
    
    def get_intersection_coord(self, pixel_coord):
        for y in xrange(self.board.dimension[Y]):
            for x in xrange(self.board.dimension[X]):
                intersection_x = x * self.square_dim[X]
                intersection_y = y * self.square_dim[Y]
                if ((pixel_coord[X]-intersection_x)**2 + (pixel_coord[Y]-intersection_y)**2) <= self.circle_radius ** 2:
                    return (x, y)
        return None

    def show(self, surface, coord):
        col = (100, 100, 100)

        dim = ((self.board.dimension[X] - 1) * self.square_dim[X],
               (self.board.dimension[Y] - 1) * self.square_dim[Y],)
        
        rect = pygame.Rect(coord[X], coord[Y], dim[X], dim[Y]) 
        pygame.draw.rect(surface, col, rect)
        
        col = (255, 255, 255)

        for y in xrange(self.board.dimension[Y] - 1):
            for x in xrange(self.board.dimension[X] - 1):
                sur_x = coord[X] + x * self.square_dim[X]
                sur_y = coord[Y] + y * self.square_dim[Y]
                rect = pygame.Rect(sur_x, sur_y, self.square_dim[X], self.square_dim[Y]) 
                pygame.draw.rect(surface, col, rect, 1)

        col_player = {W: (255, 255, 255), B: (50, 50, 50)}
        for y in xrange(self.board.dimension[Y]):
            for x in xrange(self.board.dimension[X]):
                content = self.board.content((x, y))
                if content != E:
                    sur_x = coord[X] + x * self.square_dim[X]
                    sur_y = coord[Y] + y * self.square_dim[Y]
                    pygame.draw.circle(surface, col_player[content], (sur_x, sur_y), self.circle_radius)

if __name__ == "__main__":

    humain_contre_ordi = False


    board = Board((5, 5))
    rules = GameRules(board)


    # joueur random contre MonteCarlo
    if humain_contre_ordi == False:
        players_ui = {
                W: MonteCarloPlayer(1, 0, rules, W),
                B: RandomPlayer(rules, B),
        }
    else:
        # joueur humain contre MonteCarlo
         players_ui = {
                B: MonteCarloPlayer(1, 0, rules, B),
                W: UserInterfacePlayer(rules, W),
        }


    players = players_ui
    game  = Game(rules, players)

    pygame.init()
    size = 1024, 768
    black = 0, 0, 0
    screen = pygame.display.set_mode(size)
    nblig, nbcol = 10, 10
    font = pygame.font.SysFont("comicsansms", 72)
    

    graphical_board = GraphicalBoard(board)
    board_coord = (200, 200)

    while not game.is_end():
       
        if (players[game.turn]).__class__ == UserInterfacePlayer:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3):
                        if event.button == 3:
                            players[game.turn].push_action(noop)
                            game.next_turn()
                        else:
                            x, y = event.pos
                            x -= board_coord[X]
                            y -= board_coord[Y]

                            coord = graphical_board.get_intersection_coord((x, y))
                            if coord:
                                players[game.turn].push_action(coord)
                                game.next_turn()
        else:
            time.sleep(1)
            game.next_turn()
            time.sleep(1)
        
        

        actions =  game.actions_history[other(game.turn)]
        if game.turn == len(actions) and actions[-1] == noop:
            text = font.render("%s ne joue pas!" % (other(game.turn),), True, (255, 255, 255))
            screen.blit(text, (300, 100))
            pygame.display.flip()
            time.sleep(1)

        screen.fill(black)
        graphical_board.show(screen, board_coord)

        text = font.render("Tour de %s" % (game.turn), True, (255, 255, 255))
        screen.blit(text, (300, 0))
        pygame.display.flip()
    print game.get_scores()
