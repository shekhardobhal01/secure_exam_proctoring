from flask import Flask

app = Flask(__name__)

# Import and register blueprints
from routes.user import user_bp
from routes.exam import exam_bp
from routes.logs import logs_bp

app.register_blueprint(user_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(logs_bp)

@app.route('/')
def home():
    return "🎉 Secure Exam Proctoring API is Live!"

if __name__ == '__main__':
    print("Routes loaded:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True)
