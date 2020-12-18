import logging

from flask import Blueprint, Flask

from observe.api.endpoints.health import ns as app_health_namespace
from observe.api.restplus import api

FORMAT = '%(levelname)s: %(asctime)-15s: %(filename)s: %(funcName)s: %(module)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


class Monitor:
    _app = None

    def __init__(self, app):
        self._app = app

    def configure_app(self):
        self._app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
        self._app.config['RESTPLUS_VALIDATE'] = True
        self._app.config['RESTPLUS_MASK_SWAGGER'] = False
        self._app.config['ERROR_404_HELP'] = False

    def initialize_app(self):
        self.configure_app()

        blueprint = Blueprint('Api', __name__, url_prefix='/monitor')
        api.init_app(blueprint)
        api.add_namespace(app_health_namespace)
        self._app.register_blueprint(blueprint)

# app = Flask(__name__)
# if __name__ == '__main__':
#     Monitor(app).initialize_app()
#     app.run(host='0.0.0.0', port=8080, debug=True)
#