from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO




def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'thisisnotasecuret'
    Bootstrap(app)



    from main_site.views import main_site
    from example_site.views import example_site
    from bitcoin_project.views import bitcoin_project
    from bitcoin_project.api import socketio

    app.register_blueprint(main_site)
    app.register_blueprint(example_site)
    app.register_blueprint(bitcoin_project)
    socketio.init_app(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, threaded=True)
