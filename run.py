from app import app
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(dotenv_path)

if os.getenv('FLASK_ENV') == 'development':
	host = "127.0.0.1"
	DEBUG=1
else:
	host = "0.0.0.0"
	DEBUG=0

if __name__ == "__main__":
	app.run(host=host, port=5002, debug=DEBUG)