
from jd import app, socketio

app.ready(socketio_switch=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    socketio.run(app, debug=True)
