from app import app
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(dotenv_path)

host = '127.0.0.1' if os.getenv('FLASK_ENV') == 'development' else '0.0.0.0'

if __name__ == "__main__":
	app.run(host=host, port=5000)