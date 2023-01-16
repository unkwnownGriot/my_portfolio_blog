from app import create_app
from app.model import Resume

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        Resume.create_default()
    app.run(debug=True)