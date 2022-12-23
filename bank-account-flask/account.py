import logging
import requests
from jaeger_client import Config
from flask_opentracing import FlaskTracing
from flask import Flask, request
from os import getenv

JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')
USER_API = getenv('USER_API', 'localhost:5001') 

if __name__ == '__main__':
    app = Flask(__name__)
    log_level = logging.DEBUG
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
    # Create configuration object with enabled logging and sampling of all requests.
    config = Config(config={'sampler': {'type': 'const', 'param': 1},
                            'logging': True,
                            'local_agent':
                            {'reporting_host': JAEGER_HOST}},
                    service_name="bank-account")
    jaeger_tracer = config.initialize_tracer()
    tracing = FlaskTracing(jaeger_tracer)

    @app.route('/create-account')
    @tracing.trace()
    def create_account():
        # Extract the span information for request object.
        with jaeger_tracer.start_active_span(
                'creating-account') as scope:
            # Perform business rules
            scope.span.log_kv({'event': 'creating-account'})

            url = "http://{}/save-user".format(USER_API)
            # Make the actual request to webserver.
            user_response = requests.get(url)

            return "account created"

    app.run(debug=True, host='0.0.0.0', port=5000)
