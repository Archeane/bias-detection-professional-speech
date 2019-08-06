from flask import Flask, render_template, session, request, url_for
from flask_socketio import SocketIO, emit, join_room, rooms, disconnect
from fastai import *
from fastai.text import *



async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
model = load_learner('/Users/admin/Desktop/JPMC/flask/','multi_class_bias_final.pkl')
model_classes = ['asian', 'atheist', 'bisexual', 'black', 'buddhist', 'christian', 'female', 'heterosexual', 'hindu', 'homosexual', 'learning_disability', 'jewish', 'latino', 'male', 'muslim', 'other_disability', 'other_gender', 'other_race', 'other_religion', 'other_sexual_orientation', 'physical_disability', 'psychiatric_or_mental_illness', 'transgender', 'white']

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    tensor = model.predict(str(message['data']))
    prediction = str(tensor[0])
    class_predictions = []
    idx = 0
    for t in tensor[2].tolist():
      class_predictions.append(str(t))
      idx += 1
    print(class_predictions)
    emit('my_response',
          {'data': message['data'], 'prediction': prediction, 'prediction_classes': class_predictions, 'count': session['receive_count']},
          broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})

@socketio.on('connect', namespace='/test')
def test_connect():
    print('yay')
    #emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
  socketio.run(app, debug=True)
