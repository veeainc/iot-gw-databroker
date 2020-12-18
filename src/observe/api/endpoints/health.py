import logging
import time

from flask_restplus import Resource
from observe.api.serializers import health, uptime
from observe.api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace("Health", path='/', description='Application Health')

startTime = time.time()

@ns.route('/health/')
class HealthCollection(Resource):

    # @api.response(200, 'Application Health')
    @api.marshal_with(health)
    def get(self):
        """
        Returns app status.
        """
        health = {"status": "ok"}
        return health

@ns.route('/uptime/')
class UptimeCollection(Resource):

    @api.marshal_with(uptime)
    def get(self):
        """
        Returns the number of seconds since the program started.
        """
        # do return startTime if you just want the process start time
        response = {"uptime": str(round(time.time() - startTime, 2)) + "s"}
        return response