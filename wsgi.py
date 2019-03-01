import os

from dotenv import load_dotenv

from MMCs import create_app

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

if __name__ == "__main__":
    app = create_app('production')
    app.run(host='0.0.0.0', port='80')
