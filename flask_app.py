from flask import Flask, render_template, request, jsonify
from text_to_braille import text_to_braille

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    input_data = request.get_json()
    text = input_data["text"]
    width = int(input_data["width"])
    monospace = input_data["monospace"]
    inverted = input_data["inverted"]
    greyscale_mode = input_data["greyscaleMode"]
    font_name = input_data["fontName"]

    braille_text = text_to_braille(text, font_name)

    return jsonify({"brailleText": braille_text})


if __name__ == "__main__":
    app.run(debug=True)
