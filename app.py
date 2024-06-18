from InvoicingApp import create_app  # Import the create_app factory function from InvoicingApp

app = create_app()  # Create the app instance

if __name__ == '__main__':
    import os
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('SERVER_PORT', '8000'))
    app.run(host=HOST, port=PORT, debug=True)
