from flask_restplus import fields

from observe.api.restplus import api

health = api.model('App Health', {
    'status': fields.String(required=True, description='App running status'),
})

uptime = api.model('Uptime', {
    'uptime': fields.String(required=True, description='Running time of application'),
})