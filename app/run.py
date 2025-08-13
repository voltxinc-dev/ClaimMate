from app import create_app

app = create_app()

if __name__ == "__main__":
    # Turn on debug to get detailed error messages
    app.run(host="0.0.0.0", port=5000, debug=True)
