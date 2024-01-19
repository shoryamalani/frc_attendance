import time
from flask import Flask, jsonify, request , redirect, url_for, request, render_template
import dbs_worker
import congress_data_api
import propublica_data_worker
import os
import json
import jwt
import datetime

app = Flask(__name__)

import random
import string

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string

# Example usage
SECRET_KEY = generate_random_string(10)  # Generates a random string of length 10


@app.errorhandler(404)
def not_found(e):
    print(e)
    print(request.url)
    return app.send_static_file('index.html')


@app.route('/<team>')
def index(team):
    
    return render_template("sign-in-out.html", team=team)

@app.route('/api/checkPassword', methods=['POST'])
def check_password():
    data = request.get_json()
    team = data.get('team')
    if type(team) != int:
        int(team)
    input_password = data.get('password')

    conn = dbs_worker.set_up_connection()
    team_data = dbs_worker.get_team(conn, team)
    if not team_data:
        return jsonify({'success': False})
    correct_password = team_data[1]

    if input_password == correct_password:
        # Create a token
        token = jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY)

        return jsonify({'success': True, 'token': token})

    return jsonify({'success': False})


@app.route('/api/teamMembers', methods=['POST'])
def get_teamMembers():
    team = request.json['teamNumber']
    # name = request.json['name']
    conn = dbs_worker.set_up_connection()
    team_members = dbs_worker.get_team_members(conn, team)
    team_members_display = []
    for member in team_members:
        team_members_display.append({
            'id': member[0],
            'year': str(member[2]),
            'subteam': member[3],
            'name': member[4]
        })
    return jsonify({
        'success': True,
        'teamMembers': team_members_display
    }),200

@app.route('/api/sign', methods=['POST'])
def sign():
    #teamNumber: teamNumber,
        # members: selectedMembers,
        # isSignIn: isSignIn
    team = request.json['teamNumber']
    members = request.json['members']
    isSignIn = request.json['isSignIn']
    conn = dbs_worker.set_up_connection()
    print(team,members,isSignIn)
    for member in members:
        dbs_worker.sign_member(conn, member, isSignIn, team)
    return jsonify({
        'success': True
    }), 200

@app.route('/createTeam')
def bill_page():
    return render_template('create-team.html')


@app.route('/api/createTeam', methods=['POST'])
def create_team():
    teamNumber = request.json['teamNumber']
    teamMembers = request.json['teamMembers']
    teamPassword = request.json['password']

    conn = dbs_worker.set_up_connection()
    # get team
    team = dbs_worker.get_team(conn, teamNumber)
    if team:
        return jsonify({
            'status': 'error',
            'message': 'Team already exists'
        }), 400
    num = 0
    for member in teamMembers:
        if member['year'] == "":
            year = 0
        else:
            year = int(member['year'])
        id = dbs_worker.add_team_member(conn, teamNumber, year, member['subteam'], member['name'], {})
        teamMembers[num]['id'] = id
        num += 1


    dbs_worker.create_team(conn, teamNumber,teamPassword,{
        'teamMembers': teamMembers
    })
    print(teamNumber,teamMembers)
    return jsonify({
        'status': 'success'
    }), 200


@app.route('/teamEdit/<team>')
def edit_team(team):
    return render_template('edit-team.html', teamNumber=team)

@app.route('/api/deleteStudent', methods=['POST'])
def delete_team():
    teamNumber = int(request.json['teamNumber'])
    id = request.json['id']
    conn = dbs_worker.set_up_connection()
    dbs_worker.delete_team_member(conn, id, teamNumber)
    return jsonify({
        'success': True
    }), 200

@app.route('/api/addStudent', methods=['POST'])
def add_student():
    teamNumber = request.json['teamNumber']
    name = request.json['name']
    year = request.json['year']
    subteam = request.json['subteam']
    conn = dbs_worker.set_up_connection()
    id = dbs_worker.add_team_member(conn, teamNumber, year, subteam, name, {})
    return jsonify({
        'success': True,
        'id': id
    }), 200

@app.route('/api/getTeamInformation', methods=['POST'])
def getTeamInformation():
    team = request.json['teamNumber']
    conn = dbs_worker.set_up_connection()
    team_data = dbs_worker.get_team(conn, team)
    if not team_data:
        return jsonify({'success': False})
    team_members = dbs_worker.get_team_members(conn, team)
    team_members_display = []
    for member in team_members:
        team_members_display.append({
            'id': member[0],
            'year': str(member[2]),
            'subteam': member[3],
            'name': member[4]
        })
    return jsonify({
        'success': True,
        'teamMembers': team_members_display,
        'teamPassword': team_data[1]
    }),200
           


@app.route('/teamEdit')
def edit_team_no_team():
    return render_template('edit-team.html')

@app.route('/api/initializeDatabase')
def initialize_database():
    conn = dbs_worker.set_up_connection()
    dbs_worker.set_up_database(conn)
    return {
        'status': 'success'
    }


@app.route('/api/bill/<bill_slug>')
def bill_data(bill_slug):
    data = congress_data_api.get_bill_data(bill_slug.upper())
    return jsonify(data)

@app.route('/api/all_bills')
def all_bills():
    if not os.path.isfile('current_all_bills.json'):
        data = congress_data_api.get_current_data()
        return jsonify(data)
    else:
        with open('current_all_bills.json','r') as f:
            data = json.loads(f.read())
        return jsonify(data)

@app.route('/api/force_get_data',methods=['GET'])
def force_get_data():
    data = congress_data_api.get_current_data()
    return jsonify(data)

@app.route('/api/bill_search_text',methods=['POST'])
def search_bills_text():
    print(request.json)
    bills = propublica_data_worker.search_bills_text(request.json['search_text'])
    # return jsonify(bills)
    dbs_worker.add_bills_with_propublica(dbs_worker.set_up_connection(),bills)
    bills_display = congress_data_api.get_all_relevant_bill_info_from_propublica(bills)
    return jsonify(bills_display)










if __name__ == "__main__":
    # app = Flask(__name__, static_folder='../src',static_url_path= '/')
    # data = dbs_worker.get_all_recent_bills(dbs_worker.set_up_connection())
    # for bill in data:
    #     print(bill["lastActionDate"])
    # print(congress_data_api.get_all_relevant_bill_info(dbs_worker.get_all_bills(dbs_worker.set_up_connection())))
    app.run(port=5000, debug=True)