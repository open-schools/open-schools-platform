from config.env import env

SWAGGER_ENABLED = env.bool("DEBUG_TOOLBAR_ENABLED", default=True)

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
}
