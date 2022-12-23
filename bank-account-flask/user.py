import logging
from jaeger_client import Config
from flask_opentracing import FlaskTracing
from flask import Flask, request
from os import getenv
JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')

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
                    service_name="bank-account-user")
    jaeger_tracer = config.initialize_tracer()
    tracing = FlaskTracing(jaeger_tracer)

    @app.route('/save-user')
    @tracing.trace()
    def save_user():
        # Extract the span information for request object.
        with jaeger_tracer.start_active_span(
                'saving-user') as scope:

            return "user saved"

    app.run(debug=True, host='0.0.0.0', port=5001)
