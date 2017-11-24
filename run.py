from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap



def create_app():
    app = Flask(__name__)
    Bootstrap(app)


    from main_site.views import main_site

    app.register_blueprint(main_site)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)