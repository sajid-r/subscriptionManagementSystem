import time
from flask import g, request
import logging
from logging.handlers import RotatingFileHandler
import structlog
from app import app
import os

# Disable Flask default logging
log = logging.getLogger('werkzeug')
log.disabled = True

# Configure Structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", key="@timestamp"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure python logging module
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler('error.log', maxBytes=10000, backupCount=5)
    ]
)

logger = structlog.get_logger()

# Flask method before request
@app.before_request
def before_request():
    if not (request.path == '/' or request.path == '/healthcheck'):
        g.start = time.time()

# Flask method after request
@app.after_request
def after_request(response):
    if (request.method == 'OPTIONS' or request.path == '/' or request.path == '/healthcheck') and os.getenv('FLASK_ENV') == 'production':
        response.headers.add('Access-Control-Allow-Origin', 'https://arena.fronteous.com')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    elif (request.method == 'OPTIONS' or request.path == '/' or request.path == '/healthcheck') and os.getenv('FLASK_ENV') == 'staging':
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    now = time.time()
    duration = round(now - g.start, 2)

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    host = request.host.split(':', 1)[0]
    args = dict(request.args)

    log_params = {
        'method': request.method,
        'path': request.path,
        'status': response.status_code,
        'duration': duration,
        'ip': ip,
        'host': host,
        'params': args
    }

    request_id = request.headers.get('X-Request-ID')
    if request_id:
        log_params.update({'request_id': request_id})
    logger.info(**log_params)
    return response