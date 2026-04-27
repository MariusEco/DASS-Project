from flask import Flask
from config import Config
from database.models import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route("/")
def home():
    return "Project Running"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)