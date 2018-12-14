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
    # return last 100 notes from selected channel
    if channel_name in notes:
        channel_notes = notes[channel_name]
        # last_channel_notes = channel_notes[-100:]
        return render_template("channel.html", channel_name=channel_name, channel_notes=channel_notes, notes=notes)
    else:
        return render_template("channel.html", channel_name=channel_name)


@socketio.on('message')
def send_message(mes, d):
    user= session["user"]
    data = []
    data.append(mes)
    data.append(d)
    data.append(user)
    print(data)

    send(data, broadcast=True)   

@socketio.on("save message")
def save_message(channel, mes, d):
    user= session["user"]
    if channel in notes:
        messagescounter = len (notes[channel]) + 1
        notes[channel][messagescounter] = {}
        notes[channel][messagescounter]['text']=mes
        notes[channel][messagescounter]['date']=d
        notes[channel][messagescounter]['user']=user    
    else:
        messagescounter = 1
        notes[channel] = {messagescounter: {'text':'', 'date':'', 'user': ''}}
        notes[channel][messagescounter]['text']=mes
        notes[channel][messagescounter]['date']=d
        notes[channel][messagescounter]['user']=user     

