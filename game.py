import json

class Player():
    def __init__(self,symbol):
        self.symbol = symbol
        self.score = 0

class Game():
    def __init__(self):
        self.board = [['', '', ''], ['', '', ''], ['', '', '']] #A 3x3 matrix representing the game board
        self.turn = False #A Boolean variable indicating the current player's turn
        self.player_x = Player('X') #object of the "Player" class representing the player by a symbol "X"
        self.player_o = Player('O') #object of the "Player" class representing the player by a symbol "O"

    def turn_controller(self): #function that changes the current player's turn
        self.turn = not self.turn
        if self.turn:
            return self.player_x.symbol
        return self.player_o.symbol
    
    def check_winner(self):
        symbol = self.player_o.symbol
        if self.turn:
            symbol = self.player_x.symbol

        # Check rows
        for row in self.board:
            if row.count(symbol) == 3:
                self.add_score(symbol)
                print (self.player_x.score)
                print (self.player_o.score)
                return symbol

        # # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] == symbol:
                self.add_score(symbol)
                return symbol

        # Check main diagonal (top-left to bottom-right)
        for i in range(3):
            if self.board[i][i] != symbol:
                break
        else:
            self.add_score(symbol)
            return symbol

        # Check the other diagonal (top-right to bottom-left)
        for i in range(3):
            if self.board[i][2-i] != symbol:
                break
        else:
            self.add_score(symbol)
            return symbol
        
        return False
    
    def restart(self):
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.turn = False

    def add_score(self, symbol):
        max_score_in_game = 0
        for row in self.board:
            for col in row:
                if col == '' and symbol == 'X' and max_score_in_game <= 5:
                    max_score_in_game += 1
                    self.player_x.score += 1
                elif col == '' and symbol == 'O' and max_score_in_game <= 5:
                    max_score_in_game += 1
                    self.player_o.score += 1

        if symbol == 'X' and max_score_in_game < 5:
            self.player_x.score += 1
        elif symbol == 'O' and max_score_in_game < 5:
            self.player_o.score += 1
    
    def get_player_score(self, symbol_player):
        if symbol_player == 'X':
            return self.player_x.score
        if symbol_player == 'O':
            return self.player_o.score
