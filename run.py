from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap



def create_app():
    app = Flask(__name__)
    Bootstrap(app)


    from main_site.views import main_site
    from example_site.views import example_site
    from bitcoin_project.views import bitcoin_project
    app.register_blueprint(main_site)
    app.register_blueprint(example_site)
    app.register_blueprint(bitcoin_project)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)