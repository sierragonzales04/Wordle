# Team Blue: Emma Kennedy, Sierra Gonzales, Matthew Miller, Kevin Xia
# CS362 Spring 2024
# Professor Sheehy


from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from uuid import uuid1
import mysql.connector


# Connecting to the MySQL DB
# This part is unique to each person. Change accordingly
db = mysql.connector.connect(host="127.0.0.1",
                            port=3307,
                            user="root",
                            password="root",
                            database="wordledb" # however the database name should be the same for everyone
                            )

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# DB class that will access the MySQL DB
class DB:

    def set_solution_word(self, db, session_id, user_id):
        mycursor = db.cursor()
        mycursor.execute("SELECT word FROM valid_words ORDER BY RAND() LIMIT 1")
        data = mycursor.fetchone()
        for result in data:
            solution_word = result
        mycursor = db.cursor()
        mycursor.execute("""
                        UPDATE game_sessions
                        SET solution_word=%s
                        WHERE session_id=%s
                        """, (str(solution_word), str(session_id)))
        mycursor.execute("""
                        UPDATE game_sessions
                        SET user_id=%s
                        ORDER BY session_id DESC
                        LIMIT 1""", [user_id])
        db.commit()
        return solution_word
        
    def get_solution_word(self, db, session_id):
        mycursor = db.cursor()
        mycursor.execute("""SELECT solution_word FROM game_sessions
                        WHERE session_id=%s
                        """, ([session_id]))
        data = mycursor.fetchone()
        for result in data:
            solution_word = result
        db.commit()
        return solution_word
    
    def new_user(self, db):
        mycursor = db.cursor()
        user_id = uuid1()
        sql = "INSERT INTO player_report (user_id) VALUE (%s)"
        val = [str(user_id)]
        mycursor.execute(sql, val)
        db.commit()
        return str(user_id)

    def is_valid(self, db, word):
        mycursor = db.cursor()
        mycursor.execute("""
                        SELECT word from valid_words
                        WHERE word = %s
                        """, ([word]))
        data = mycursor.fetchone()
        if data is not None:
            return True
        else:
            return False
        
    def create_new_valid_word(self, db, word):
        mycursor = db.cursor()
        mycursor.execute("""
                        INSERT INTO valid_words (word) VALUE (%s)
                        """, ([word]))
        db.commit()
        return word

    def update_wins(self, user_id):
        mycursor = db.cursor()
        mycursor.execute("""
                        UPDATE player_report
                        SET wins=wins+1, result_of_prev_game = 'W'
                        WHERE user_id=%s
                        """, ([user_id]))
        db.commit()


    def update_losses(self, user_id):
        mycursor = db.cursor()
        mycursor.execute("""
                        UPDATE player_report
                        SET losses=losses+1, result_of_prev_game = 'L'
                        WHERE user_id=%s
                        """, [user_id])
        db.commit()

    def update_streak(self, user_id, curr_game_result):
        mycursor = db.cursor()
        mycursor.execute("""
                        SELECT result_of_prev_game from player_report
                        WHERE user_id=%s
                        """, [user_id])
        data = mycursor.fetchone()
        for x in data:
            prev_game_result = x
        if prev_game_result == curr_game_result:
            if curr_game_result == 'W':
                #increment streak by 1
                mycursor.execute("""
                                UPDATE player_report
                                SET streak=streak+1
                                WHERE user_id=%s
                                """, [user_id])
            elif curr_game_result == 'L':
                #decrement streak by 1
                mycursor.execute("""
                                UPDATE player_report
                                SET streak=streak-1
                                WHERE user_id=%s
                                """, [user_id])
            else:
                print("Something went wrong")
        elif prev_game_result != curr_game_result or prev_game_result is None:
            if curr_game_result == 'W':
                #set streak to 1
                mycursor.execute("""
                                UPDATE player_report
                                SET streak=1
                                WHERE user_id=%s
                                """, [user_id])
            elif curr_game_result == 'L':
                #set streak to -1
                mycursor.execute("""
                                UPDATE player_report
                                SET streak=-1
                                WHERE user_id=%s
                                """, [user_id])
            else:
                print("Something went wrong")
        else:
            print("Something went wrong")
        db.commit()

    def new_session(self, user_id):
        mycursor = db.cursor()
        mycursor.execute("INSERT INTO game_sessions (session_id) VALUE (0)")
        mycursor.execute("SELECT LAST_INSERT_ID()")
        data = mycursor.fetchone()
        for x in data:
            session_id = x
        solution_word = self.set_solution_word(db, session_id, user_id)
        return session_id, solution_word
    
    def get_player_report(self, user_id):
        mycursor = db.cursor()
        mycursor.execute ("""
                        SELECT * FROM player_report
                        WHERE user_id=%s
                        """, [user_id])
        data = mycursor.fetchall()
        for x in data:
            return x

    
    def update_guess_column(self, user_id, num_guesses):
        mycursor = db.cursor()
        if num_guesses == '1':
            mycursor.execute ("""
                        UPDATE player_report
                        SET _1G=_1G+1
                        WHERE user_id=%s
                        """, [user_id])
        elif num_guesses == '2':
            mycursor.execute ("""
                        UPDATE player_report
                        SET _2G=_2G+1
                        WHERE user_id=%s
                        """, [user_id])
        elif num_guesses == '3':
            mycursor.execute ("""
                        UPDATE player_report
                        SET _3G=_3G+1
                        WHERE user_id=%s
                        """, [user_id])
        elif num_guesses == '4':
            mycursor.execute ("""
                        UPDATE player_report
                        SET _4G=_4G+1
                        WHERE user_id=%s
                        """, [user_id])
        elif num_guesses == '5':
            mycursor.execute ("""
                        UPDATE player_report
                        SET _5G=_5G+1
                        WHERE user_id=%s
                        """, [user_id])
        elif num_guesses == '6':
            mycursor.execute ("""
                        UPDATE player_report
                        SET _6G=_6G+1
                        WHERE user_id=%s
                        """, [user_id])
        elif num_guesses == '0':
            return
        else:
            print("Something went wrong")
        return


class check_word(Resource):
    def get(self, word):
        myDB = DB()
        result = myDB.is_valid(db, word)
        if result:
            result = 'valid'
        elif not result:
            result = 'not valid'
        else:
            result = 'unable_to_check_word'
        return {'check_word': result}
    

class assign_solution_word(Resource):
    def get(self):
        mycursor = db.cursor()
        mycursor.execute("SELECT word FROM valid_words ORDER BY RAND() LIMIT 1")
        data = mycursor.fetchone()
        for result in data:
            solution_word = result
        print(solution_word)
        if solution_word is None:
            solution_word = 'unable_to_assign_solution_word'
        return {'assign_solution_word': str(solution_word)}
    

class generate_user_id(Resource):
    def get(self):
        myDB = DB()
        user_id = myDB.new_user(db)
        if user_id is None:
            return {'user_id': 'Unable to generate user ID'}
        return {'user_id': str(user_id)}


class start_new_session(Resource):
    def get(self, user_id):
        myDB = DB()
        session_id, solution_word = myDB.new_session(user_id)
        if session_id is None:
            return {'new_session_started': 'Unable to generate session ID'}
        elif solution_word is None:
            return {'new_session_started': 'Unable to generate solution word'}
        return {'new_session_started': {'session_id': session_id, 'solution_word':solution_word}}
    

class send_results(Resource):
    def get(self, user_id, win_or_lose, num_guesses):
        myDB = DB()
        if win_or_lose == 'W':
            myDB.update_streak(user_id, win_or_lose)
            myDB.update_wins(user_id)
            myDB.update_guess_column(user_id, num_guesses)
            return {'send_results':'Database updated win'}
        elif win_or_lose == 'L':
            myDB.update_streak(user_id, win_or_lose)
            myDB.update_losses(user_id)
            return {'send_results':'Database updated loss'}
        else:
            return {'send_results':'Unable to update database'}

    
class get_player_report(Resource):
    def get(self, user_id):
        myDB = DB()
        x = myDB.get_player_report(user_id)
        if x is None:
            return {'player_record' : 'Unable to retrieve record'}
        return {'player_record': {
            'user_id':x[0],
            'streak':x[1],
            'wins':x[2],
            'losses':x[3],
            '1G':x[4],
            '2G':x[5],
            '3G':x[6],
            '4G':x[7],
            '5G':x[8],
            '6G':x[9],
        }}

class get_solution_word(Resource):
    def get(self, session_id):
        myDB = DB()
        solution_word = myDB.get_solution_word(db, session_id)
        if solution_word is None:
            solution_word = 'unable_to_find_solution_word'
        return {'solution_word_for_this_session': solution_word}
    
class create_new_valid_word(Resource):
    def get(self, word):
        myDB = DB()
        new_valid_word = myDB.create_new_valid_word(db, word)
        if new_valid_word is None:
            new_valid_word = 'unable to create new valid word'
        return {'new_valid_word' : new_valid_word}


# All API resources
api.add_resource(check_word, '/check_word/<word>')
api.add_resource(assign_solution_word, '/assign_solution_word')
api.add_resource(generate_user_id, '/user_id')
api.add_resource(start_new_session, '/new_session/<user_id>')
api.add_resource(send_results,'/send_results/<user_id>/<win_or_lose>/<num_guesses>')
api.add_resource(get_player_report, '/get_player_report/<user_id>')
api.add_resource(get_solution_word, '/get_solution_word/<session_id>')
api.add_resource(create_new_valid_word, '/create_new_valid_word/<word>')


if __name__ == '__main__':
    app.run(debug=True)