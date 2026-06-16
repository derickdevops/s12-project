from flask import Flask, Response, render_template_string, send_from_directory

app = Flask(__name__)

IMAGE_NAME = "about2.jpeg.jpeg"


@app.route("/")
def home():
    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Derick's Docker Demo</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    min-height: 100vh;
                    display: grid;
                    place-items: center;
                    background: #f4f7fb;
                    color: #1f2937;
                }

                main {
                    width: min(900px, 92vw);
                    text-align: center;
                }

                img {
                    width: 100%;
                    max-height: 520px;
                    object-fit: cover;
                    border-radius: 8px;
                    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
                }
            </style>
        </head>
        <body>
            <main>
                <h1>Welcome to Derick's Website</h1>
                <img src="/students-image" alt="Students learning with a computer">
            </main>
        </body>
        </html>
        """
    )


@app.route("/hello")
def hello():
    return Response(
        "Hello DEL S12 students, and welcome to Derick's website!",
        mimetype="text/plain",
    )


@app.route("/students-image")
def students_image():
    return send_from_directory(".", IMAGE_NAME)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
