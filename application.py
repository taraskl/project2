import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

channels = []
notes ={}


@app.route("/", methods=["GET", "POST"])
def index():
    # user = 
    if request.method == "POST":
        name = request.form.get("name")
        session["user"] = name
        return render_template("index.html", user= session["user"], channels=channels )

    try:
        return render_template("index.html", user= session["user"], channels=channels)
    except:
        return render_template("index.html", channels=channels)        


@app.route("/logout")
def logout():
    session["user"] = []

    return render_template("index.html", user= session["user"]) 


@app.route("/channels", methods=["GET", "POST"])
def channel():
    if request.method == "POST":
        channel = request.form.get("channel")
        if channel in channels:
            return render_template("error.html", message="This channel exist.") 
        elif channel is None: 
            pass
        else:       
            channels.append(channel)

    return render_template("index.html", user= session["user"], channels=channels ) 


@app.route("/channel/<channel_name>",methods=["GET", "POST"])

def channelpage(channel_name):
    if channel_name in notes:
        channel_notes = notes[channel_name]
        last_channel_notes = channel_notes[-100:]
        return render_template("channel.html", channel_name=channel_name, notes=last_channel_notes)
    else:
        return render_template("channel.html", channel_name=channel_name)


@socketio.on('message')
def handleMessage(msg):
    data = []
    data.append(msg)
    for i in data:
        print('Message: ' + i)
    send(data, broadcast=True)   

@socketio.on("submit vote")
def vote(channel, mes):
    if channel in notes:
        notes[channel].append(mes)
    else:
        notes[channel] = []
        notes[channel].append(mes)       
    print(notes)
    # selection = data["selection"]
    # votes[selection] += 1
    # emit("vote totals", votes, broadcast=True)     