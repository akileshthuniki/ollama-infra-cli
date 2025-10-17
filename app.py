import os
from flask import Flask, jsonify

app = Flask(__name__)

# Health check endpoint for AWS ALB
@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

# Main application endpoint
@app.route("/")
def hello():
    return jsonify({
        "message": "Hello world",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "container_id": os.environ.get("CONTAINER_ID", "unknown")
    })

# Environment information endpoint
@app.route("/info")
def environment_info():
    return jsonify({
        "app_name": "Hello World Flask App",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "aws_region": os.environ.get("AWS_REGION", "unknown"),
        "ecs_cluster": os.environ.get("ECS_CLUSTER", "unknown"),
        "container_id": os.environ.get("CONTAINER_ID", "unknown")
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "false").lower() == "true")
