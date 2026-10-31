import uvicorn
from .app.main import app, debug, port, host

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port, debug=debug)
