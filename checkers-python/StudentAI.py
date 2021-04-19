from random import randint
from BoardClasses import Move
from BoardClasses import Board
import time
import copy
import math


class Node():
    def __init__(self, wi, si, move=None, parent=None):
        self.wi = wi
        self.si = si
        self.c = 1.414
        self.parent = parent
        self.move = move
        self.children = []
        if self.parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1


class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.halftime = time.time() + 240
        self.endtime = time.time() + 360
        self.finaltime = time.time() + 460
        self.root = Node(0, 0)

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
            self.update_root_tree(move)
        else:
            self.color = 1

        moves = self.board.get_all_possible_moves(self.color)
        if len(moves) == 1 and len(moves[0]) == 1:
            self.board.make_move(moves[0][0], self.color)
            self.update_root_tree(moves[0][0])
            return moves[0][0]  # if only one move available, choose immediately

        count = 0
        # decides how long to run the mcts depending on time remaining
        if time.time() > self.finaltime:
            return self.choose_best_move(self.board, moves, self.color)
        elif time.time() > self.endtime:
            t_end = time.time() + 4
        elif time.time() > self.halftime:
            t_end = time.time() + 7
        else:
            t_end = time.time() + 10

        while time.time() < t_end:
            node, board = self.selection()
            node = self.expansion(node,board)
            result = self.simulation(node, board)
            self.backpropagation(node, result)
            count += 1

        max_sim = 0
        max_child = self.root.children[0]
        for each in self.root.children:
            if each.si > max_sim:
                max_child = each
                max_sim = each.si
        self.board.make_move(max_child.move,self.color)
        self.update_root_tree(max_child.move)
        return max_child.move

    def selection(self):
        node_found = False
        board = copy.deepcopy(self.board)
        node = self.root
        color = self.color
        while not node_found:
            if len(node.children) == 0:
                node_found = True
            else:
                max_uct = 0
                max_child = node.children[0]
                for each in node.children:
                    if each.si == 0 or each.parent.si == 0:
                        uct = 9999
                    else:
                        uct = (each.wi/each.si) + each.c*(math.sqrt(math.log(each.parent.si)/each.si))
                    if uct > max_uct:
                        max_child = each
                        max_uct = uct
                node = max_child
                board.make_move(max_child.move, color)
                color = 3 - color

        return node,board

    def expansion(self, node, board):
        new_color = self.color
        if node.depth % 2 == 1:
            new_color = 3 - self.color
        outer_childs = board.get_all_possible_moves(new_color)
        for child in outer_childs:
            for move in child:
                node.children.append(Node(0, 0, move, node))

        if len(outer_childs) == 0:
            return node
        return node.children[randint(0,len(node.children)-1)]

    def simulation(self, node, board):
        sim_color = self.color
        if node.depth % 2 == 1:
            sim_color = 3 - self.color
        loops = 0
        while not board.is_win(sim_color):
            sim_color = 3 - sim_color
            moves = board.get_all_possible_moves(sim_color)
            index = randint(0, len(moves) - 1)
            inner_index = randint(0, len(moves[index]) - 1)
            board.make_move(moves[index][inner_index], sim_color)

            if loops > 50:  # game takes too long, return based on who has advantage on current board state
                if board.black_count - board.white_count >= 2:
                    return 1
                elif board.white_count - board.black_count >= 2:
                    return 2
                else:
                    return -1
            loops += 1

        if loops == 0:
            sim_color = 3 - sim_color

        return board.is_win(sim_color)

    def backpropagation(self, node, result):
        win = False
        node_color = self.color
        if node.depth % 2 == 0:
            node_color = 3 - self.color
        if result == node_color:
            win = True

        while node is not None:
            node.si += 1
            if win:
                node.wi += 1
            win = not win
            node = node.parent

    def update_root_tree(self, move):
        check = False
        for each in self.root.children:
            if str(each.move) == str(move):
                self.root = each
                self.root.parent = None
                check = True
                break
        if not check:
            self.root = Node(0, 0)

    # essentially attempts to prevent the opponent from capturing a piece, stall the game to a tie
    def choose_best_move(self, board, moves, color):
        best_move = moves[0][0]
        num = 9999
        for i,each in enumerate(moves):
            for j,move in enumerate(each):
                board.make_move(move, color)
                opp_moves = board.get_all_possible_moves(3 - color)
                rank = 0
                for opp in opp_moves:
                    for opp_move in opp:
                        str_move = str(opp_move)
                        if abs(int(str_move[1]) - int(str_move[7])) == 2:
                            rank += 1
                if rank < num:
                    num = rank
                    best_move = move
                board.undo()
        board.make_move(best_move, color)
        return best_move
