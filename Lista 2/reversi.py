import random
import math
import copy
import time

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Czas wykonania {func.__name__}: {end - start} sekund")
        return result
    return wrapper

def get_winner(board):
    player1_discs = 0
    player2_discs = 0

    for x in range(8):
        for y in range(8):
            if board[x][y] == 1:
                player1_discs += 1
            elif board[x][y] == 2:
                player2_discs += 1

    if player1_discs > player2_discs:
        return 1, player1_discs
    elif player2_discs > player1_discs:
        return 2, player2_discs
    else:
        return 0, 0

def is_game_over(board):
    if len(get_available_moves(1, board)) == 0 and len(get_available_moves(2, board)) == 0:
        return True
    
    for x in range(8):
        for y in range(8):
            if board[x][y] == 0:
                return False
    
    return False

def get_enemy_player(player):   
    return 2 if player == 1 else 1

def get_neighbors(board):
    return lambda x, y : [(x2, y2) for x2 in range(x - 1, x + 2)
                                for y2 in range(y - 1, y + 2)
                                if (-1 < x <= len(board) and
                                    -1 < y <= len(board) and
                                    (x != x2 or y != y2) and
                                    (0 <= x2 < len(board)) and
                                    (0 <= y2 < len(board)))]    

def get_available_moves(player, board):
    available_moves = []
    enemy_player = get_enemy_player(player)

    for x in range(8):
        for y in range(8):
            invalid_field = True
            if board[x][y] == 0:  
                #jezeli w sasiedztwie pustego pola nie ma dysku przeciwnego gracza to pomin     
                for neighbor in get_neighbors(board)(x, y):
                    if board[neighbor[0]][neighbor[1]] == enemy_player:
                        invalid_field = False 
                        break    

                if invalid_field:
                    continue

                for neighbor in get_neighbors(board)(x, y):
                    if board[neighbor[0]][neighbor[1]] == enemy_player:
                        direction_x = neighbor[0] - x
                        direction_y = neighbor[1] - y
                        current_x = direction_x
                        current_y = direction_y

                        while True:
                            if (x + current_x) >= len(board) or (y + current_y) >= len(board) or board[x + current_x][y + current_y] == 0:
                                break
                            
                            if board[x + current_x][y + current_y] == player:
                                available_moves.append((x, y))
                                break

                            current_x += direction_x
                            current_y += direction_y

                        
    return list(set(available_moves))

def make_move(board, player, move):
    fields_to_change = []
    x = move[0]
    y = move[1]
    board[x][y] = player
    enemy_player = get_enemy_player(player)

    for neighbor in get_neighbors(board)(x, y):
        if board[neighbor[0]][neighbor[1]] == enemy_player:
            direction_x = neighbor[0] - x
            direction_y = neighbor[1] - y
            current_x = direction_x
            current_y = direction_y

            while True:
                if (x + current_x) >= len(board) or (y + current_y) >= len(board) or board[x + current_x][y + current_y] == 0:
                    fields_to_change = []
                    break

                if board[x + current_x][y + current_y] == enemy_player:
                    fields_to_change.append((x + current_x, y + current_y))

                if board[x + current_x][y + current_y] == player:
                    for field in fields_to_change:
                        board[field[0]][field[1]] = player
                    break

                current_x += direction_x
                current_y += direction_y
    return board

@measure_time
def game(board):
    end_game = False
    turn = 1
    while not end_game:
        if turn % 2 == 0:
            current_player = 2
            heuristics = heuristics1
        else:
            current_player = 1
            heuristics = heuristics1

        print(get_available_moves(current_player, board))

        if len(get_available_moves(current_player, board)) > 0:
            move, v = alphabeta(board, current_player, 2, -math.inf, math.inf, heuristics)
            #move, v = minimax(board, current_player, 3, heuristics)
            board = make_move(board, current_player, move)            
        
        print("Tura:", turn, "gracz:", current_player)
        for wiersz in board:
            print(wiersz)

        end_game = is_game_over(board)

        turn += 1

    winner, winners_discs = get_winner(board)
    print("Zwycięzca:", winner)
    return board

def heuristics1(board):
    player1_discs = 0
    player2_discs = 0

    for x in range(8):
        for y in range(8):
            if board[x][y] == 1:
                player1_discs += 1
            elif board[x][y] == 2:
                player2_discs += 1

    if is_game_over(board): 
        if get_winner(board)[0] == 1: 
            return 1000000 
        elif get_winner(board)[0] == 2: 
            return -1000000
        else:
            return 0
    else: 
        return player1_discs - player2_discs

def heuristics2(board):
    player1_discs = 0
    player2_discs = 0

    for x in range(8):
        for y in range(8):
            if board[x][y] == 1:
                player1_discs += 1
            elif board[x][y] == 2:
                player2_discs += 1

    player1_num_of_moves = len(get_available_moves(1, board))
    player2_num_of_moves = len(get_available_moves(2, board))

    if is_game_over(board): 
        if get_winner(board)[0] == 1: 
            return 1000000 
        elif get_winner(board)[0] == 2: 
            return -1000000
        else:
            return 0
    else: 
        return player1_discs + player1_num_of_moves - player2_discs + player2_num_of_moves

def heuristics3(board):
    player1_discs = 0
    player2_discs = 0

    values_board = [
        [99, -8, 8, 6, 6, 8, -8, 99],
        [-8, -24, -4, -3, -3, -4, -24, -8],
        [8, -4, 7, 4, 4, 7, -4, 8],
        [6, -3, 4, 0, 0, 4, -3, 6],
        [6, -3, 4, 0, 0, 4, -3, 6],
        [8, -4, 7, 4, 4, 7, -4, 8],
        [-8, -24, -4, -3, -3, -4, -24, -8],
        [99, -8, 8, 6, 6, 8, -8, 99]
    ]

    for x in range(8):
        for y in range(8):
            if board[x][y] == 1:    
                player1_discs += values_board[x][y]
            elif board[x][y] == 2:
                player2_discs += values_board[x][y]

    if is_game_over(board): 
        if get_winner(board)[0] == 1: 
            return 1000000 
        elif get_winner(board)[0] == 2: 
            return -1000000
        else:
            return 0
    else: 
        return player1_discs - player2_discs 

def test(board):
    return random.random() * 10 - random.random() * 10

def minimax(board, player, depth, heuristics):
    current_player = player
    best_move = None

    if depth == 0 or is_game_over(board):
        return None, heuristics(board)

    if current_player == 1:
        best_value = -math.inf    
        possible_moves = get_available_moves(current_player, board)
        if len(possible_moves) == 0:
            return minimax(board, get_enemy_player(current_player), depth - 1, heuristics)
        
        for move in possible_moves:
            new_board = make_move(copy.deepcopy(board), current_player, move)
            _, value = minimax(new_board, get_enemy_player(current_player), depth - 1, heuristics)
            
            if value > best_value:
                    best_value = value
                    best_move = move

        return best_move, best_value
    
    elif current_player == 2:
        best_value = math.inf
    
        possible_moves = get_available_moves(current_player, board)
        if len(possible_moves) == 0:
            return minimax(board, get_enemy_player(current_player), depth - 1, heuristics)
        
        for move in possible_moves:
            new_board = make_move(copy.deepcopy(board), current_player, move)
            
            _, value = minimax(new_board, get_enemy_player(current_player), depth - 1, heuristics)
            
            if value < best_value:
                    best_value = value
                    best_move = move

        return best_move, best_value

def alphabeta(board, player, depth, alpha, beta, heuristics):
    current_player = player
    best_move = None

    if depth == 0 or is_game_over(board):
        return None, heuristics(board)

    if current_player == 1:
        best_value = -math.inf    
        possible_moves = get_available_moves(current_player, board)
        if len(possible_moves) == 0:
            return alphabeta(board, get_enemy_player(current_player), depth - 1, alpha, beta, heuristics)
        
        for move in possible_moves:
            new_board = make_move(copy.deepcopy(board), current_player, move)
            _, value = alphabeta(new_board, get_enemy_player(current_player), depth - 1, alpha, beta, heuristics)
            
            if value > best_value:
                    best_value = value
                    best_move = move

            alpha = max(alpha, value)
            if beta <= alpha:
                break

        return best_move, best_value
    
    elif current_player == 2:
        best_value = math.inf
    
        possible_moves = get_available_moves(current_player, board)
        if len(possible_moves) == 0:
            return alphabeta(board, get_enemy_player(current_player), depth - 1, alpha, beta, heuristics)
        
        for move in possible_moves:
            new_board = make_move(copy.deepcopy(board), current_player, move)
            
            _, value = alphabeta(new_board, get_enemy_player(current_player), depth - 1, alpha, beta, heuristics)
            
            if value < best_value:
                    best_value = value
                    best_move = move

            beta = min(beta, value)
            if beta <= alpha:
                break

        return best_move, best_value

board = [[0 for j in range(8)] for i in range(8)]

board[3][4] = 1
board[4][3] = 1
board[4][4] = 2
board[3][3] = 2

game(copy.deepcopy(board))
