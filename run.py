from app import create_app
app = create_app()
if __name__ == '__main__':
    # Makes the server accessible on local network for QR scanning
    app.run(host='0.0.0.0', port=5000, debug=True)