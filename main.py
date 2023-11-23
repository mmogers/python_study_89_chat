from flask import Flask, render_template, request, redirect
import replit
import time
from datetime import datetime


app = Flask(__name__)
db = replit.db

# Custom filter to convert timestamp to human-readable string
@app.template_filter('timestamp_to_str')
def timestamp_to_str(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Function to initialize the database if not already present
def initialize_db():
    if 'users' not in db.keys():
        db['users'] = {
            'admin': {'password': 'adminpass', 'is_admin': True, 'profile_pic': 'e.png'},
            'user1': {'password': 'user1pass', 'is_admin': False, 'profile_pic': 'p.png'},
            'user2': {'password': 'user2pass', 'is_admin': False, 'profile_pic': 'r.png'}
            # Add other users if needed
        }

    if 'chat_messages' not in db.keys():
        db['chat_messages'] = []

# Initialize the database
initialize_db()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    if username in db['users'] and db['users'][username]['password'] == password:
        return redirect('/chat?username=' + username)
    else:
        return redirect('/')

# Inside the /chat route
@app.route('/chat')
def chat():
    username = request.args.get('username')
    admin_panel_pressed = request.args.get('adminPanelBtn') == 'true'

    if username not in db['users']:
        return redirect('/')

    is_admin = db['users'][username]['is_admin']
    last_five_messages = db['chat_messages'][-5:]

    return render_template('chat.html', username=username, is_admin=is_admin, messages=last_five_messages, admin_panel_pressed=admin_panel_pressed)


# Add this route for the admin panel
@app.route('/admin_panel')
def admin_panel():
    all_messages = db['chat_messages']
    return render_template('admin_panel.html', messages=all_messages)


@app.route('/add_message', methods=['POST'])
def add_message():
    username = request.form['username']
    message = request.form['message']

    if username in db['users']:
        profile_pic = db['users'][username]['profile_pic']
        timestamp = int(time.time())  # Convert the timestamp to an integer
        db['chat_messages'].append({'timestamp': timestamp, 'username': username, 'message': message, 'profile_pic': profile_pic})

    return redirect('/chat?username=' + username)



@app.route('/delete_message', methods=['POST'])
def delete_message():
    if 'admin' in request.form and request.form['admin'] == 'true':
        try:
            # Convert the timestamp to an integer directly
            timestamp = int(request.form['timestamp'])

            # Filter out the message with the specified timestamp
            db['chat_messages'] = [msg for msg in db['chat_messages'] if msg['timestamp'] != timestamp]
        except ValueError:
            # Handle the case where the timestamp is not in the expected format
            return "Invalid timestamp format. Please enter a valid timestamp."

    return redirect('/chat?username=admin')



# The app runs only if this script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
