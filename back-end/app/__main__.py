import os
import sys
import uvicorn


def main():
    # Default port 3000 unless explicitly provided via CLI or env
    default_port = int(os.getenv("PORT", "3000"))

    # If user passes port via command line (e.g., --port 9000), let uvicorn parse it
    # Otherwise, run with our default port
    if any(arg.startswith("--port") for arg in sys.argv[1:]):
        uvicorn.run("app.main:app", host="0.0.0.0", reload=True)
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=default_port, reload=True)


if __name__ == "__main__":
    main()