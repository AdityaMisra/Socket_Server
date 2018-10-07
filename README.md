# Socket Server
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)[![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com)[![forthebadge](https://forthebadge.com/images/badges/cc-0.svg)](https://forthebadge.com)

A simple python server, using sockets, that allows files to be shared on LAN. The client has an exact clone of the server's `Public` directory which is read-only (for now) and stores it in a `Container` folder.

## Getting Started
The `server_manager.py` handles both Client and Server. Debugging has been made easy, inside the `testing` folder there is a `start.bat` if you are on Windows (which runs both client and server at once). If you are on another platform, make a script or manually execute `client_testing.py` and `server_testing.py`.
