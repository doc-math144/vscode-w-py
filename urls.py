import logging
import time
from flask import Blueprint, render_template, Response
from capture import capture_dolphin_window, DOLPHIN_SPECIFIC_TITLE
import cv2

# Create blueprint for routes
main = Blueprint('main', __name__)

# URL patterns
routes = {
    '/': 'index',                    # Main page
    '/video_feed': 'video_feed',     # Video streaming endpoint
    '/static/<path:filename>': 'static' # Static files
}

# Function to register routes with Flask app
def register_routes(app):
    app.register_blueprint(main)

# Error handlers
def handle_404(e):
    return 'Page not found', 404

def handle_500(e):
    return 'Internal server error', 500

# Register error handlers
def register_error_handlers(app):
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/video_feed')
def video_feed():
    def gen_frames():
        retry_delay = 1.0  # seconds
        while True:
            frame = capture_dolphin_window()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                logging.warning("No Dolphin window found, retrying...")
                time.sleep(retry_delay)

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
