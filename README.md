# Simple Flask Docker Demo

This is a small Python web application for teaching Docker with Flask.

## Files

- `app.py`: Flask web server.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Docker build instructions.
- `about2.jpeg.jpeg`: Homepage image used by the app.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open:

- `http://localhost:5000/`
- `http://localhost:5000/hello`

## Build The Docker Image

```bash
docker build -t derick-flask-demo .
```

## Run The Container

```bash
docker run -p 5000:5000 derick-flask-demo
```

The `-p 5000:5000` option maps port `5000` on your computer to port `5000` inside the container.

## Test The Endpoints

In a browser, open:

- `http://localhost:5000/`
- `http://localhost:5000/hello`

Or test with `curl`:

```bash
curl http://localhost:5000/
curl http://localhost:5000/hello
```

The `/hello` endpoint should return:

```text
Hello DEL S12 students, and welcome to Derick's website!
```
