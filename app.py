import secrets
import game
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
from flask import Flask, render_template, request, session, redirect, url_for, render_template
import json

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = secrets.token_hex(16)
handler = RotatingFileHandler('server.log', maxBytes=100000, backupCount=1)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
game_obj = game.Game()

@app.template_filter('enumerate')
def _enumerate(sequence, start=0):
    return enumerate(sequence, start)

@app.route('/restart', methods=['GET'])
def restart():
    game_obj.restart()
    return render_template('tic_tac_toe.html', board=game_obj.board)

@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    return render_template('login.html')

@app.route('/records')
def show_records():
    with open('users.json', 'r') as file:
        data = json.load(file)
        users = data['users']
    
    sorted_users = sorted(users, key=lambda user: user['score'], reverse=True)
    top_10_users = sorted_users[:10]
    
    return render_template('records.html', users=top_10_users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        competitor_name = request.form['competitor_name']

        if checkif_competitor_exist(competitor_name) == 0:
                message = 'The competitor is not registerd, please register first'
                return render_template('login.html', message=message)

        with open('users.json', 'r') as file:
            data = json.load(file)
            users = data['users']
            for user in users:
                if user['name'] == username and user['password'] == password:
                    login_name(username) #save the username_login to text file
                    competitor_login(competitor_name) #save the competitor_name to text file
                    app.logger.info('The user is connected to the server') #Log
                    session['logged_in'] = True
                    return redirect(url_for('tic_tac_toe'))
                elif user['name'] == username and user['password'] != password:
                    message = 'Inccorrect password, please try again'
                    app.logger.warning('Failed to Login, wrong password') #Log
                    return render_template('login.html', message=message)
                    
        # If authentication fails, display an error message
    message = 'Username not existed, please register first'
    app.logger.error('Failed to Login, username not existed') #Log
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        with open('users.json', 'r') as file:
            data = json.load(file)
            users = data['users']
            for user in users:
                if user['name'] == username:
                    message = 'User name already exists, please login'
                    return render_template('login.html', message=message)
            
            # User does not exist, register the new user
            add_user(username, password)
            message = 'You have successfully registered, please log in'
            return render_template('login.html', message=message)
    
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def tic_tac_toe():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    message = ''

    if request.method == 'POST':
        row = int(request.form['row'])
        col = int(request.form['col'])

        with open('user_login.txt', 'r') as file:
            user_login = file.read()
        with open('competitor_name.txt', 'r') as file:
            competitor_name = file.read()

        if game_obj.board[row][col] == '':
            game_obj.board[row][col] = game_obj.turn_controller()
            symbol_player = game_obj.check_winner()

            if symbol_player == 'X':
                update_user_score(str(user_login), int(game_obj.get_player_score(symbol_player)))
                message = 'Player ' + user_login + ' win! ' + "His Score is: " + str(game_obj.get_player_score(symbol_player))
            elif symbol_player == 'O':
                update_user_score(str(competitor_name), int(game_obj.get_player_score(symbol_player)))
                message = 'Player ' + competitor_name + ' win! ' + "His Score is: " + str(game_obj.get_player_score(symbol_player))

            elif not any('' in row for row in game_obj.board):
                message = 'It\'s a tie!'
        else:
            message = 'Invalid move. Try again.'

    return render_template('tic_tac_toe.html', board=game_obj.board, message=message)

# Route for the score page
@app.route('/score', methods=['GET', 'POST'])
def score():
    if request.method == 'POST':
        try:
            username = request.form['username']
            with open('users.json', 'r') as file:
                data = json.load(file)
                users = data['users']
                for user in users:
                    if user['name'] == username:
                        score = user['score']
                        message = 'The score is: ' + str(score)
                        return render_template('score.html', message=message)
        except KeyError:
            message = 'Invalid request. Please enter a username.'
            return render_template('score.html', message=message)
    
    message = 'User not exist'
    return render_template('score.html', message=message)
    
def add_user(username, password):
    with open('users.json', 'r+') as file:
        data = json.load(file)
        users = data['users']
        users.append({
            'name': username,
            'password': password,
            'score': 0
        })
        file.seek(0)  # Move the file pointer to the beginning
        json.dump(data, file, indent=4)
        file.truncate()  # Clear any remaining content

def update_user_score(username, add_score):
    with open('users.json', 'r') as file:
        data = json.load(file)
        users = data['users']
        
        for user in users:
            if user['name'] == username:
                user['score'] += add_score
                break
        
    with open('users.json', 'w') as file:
        json.dump(data, file, indent=4)

def login_name(name):    
    # Delete contents of the file
    with open('user_login.txt', 'w') as file:
        file.truncate(0)
    
    # Write the name to the file
    with open('user_login.txt', 'w') as file:
        file.write(name)

def competitor_login(name):    
    # Delete contents of the file
    with open('competitor_name.txt', 'w') as file:
        file.truncate(0)
    
    # Write the name to the file
    with open('competitor_name.txt', 'w') as file:
        file.write(name)

def checkif_competitor_exist(competitor):
    competitor_exsit = 0
    with open('users.json', 'r') as file:
        data = json.load(file)
        users = data['users']
        for user in users:
            if user['name'] == competitor:
                competitor_exsit = 1
    return competitor_exsit

if __name__ == '__main__':
    app.run(debug=True, port=5001)