
from jd import app, socketio

app.ready()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8981)
    # socketio.run(app, debug=True)
