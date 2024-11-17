from flask import Flask, request
import logging
import base64
import threading
import time
import sys
from io import BytesIO

from PIL import Image

from flask_cors import CORS
from niimprint import BluetoothTransport, PrinterClient, SerialTransport

app = Flask(__name__)
CORS(app)

transport = SerialTransport(port=sys.argv[1])
density = 1
printer = PrinterClient(transport)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/info")
def d11info():
    return {"type": printer.get_info(8), "soft_version": printer.get_info(9), "hw_version": printer.get_info(12), "battery": printer.get_info(10)}

@app.route("/print", methods=["POST"])
def d11print():

    logging.basicConfig(
        level="DEBUG",
        format="%(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
    )

    assert request.json['image'] is not None and len(request.json['image']) > 0
    
    density = request.json['density'] if request.json['density'] is not None else 3
    quantity = request.json['quantity'] if request.json['quantity'] is not None else 1
    image = base64.b64decode(request.json['image'])

    bimage = Image.open(BytesIO(image))
    bimage = bimage.rotate(-int(90), expand=True)

    printer.print_image(bimage, density=density)
    return "ok"

def heartbeat():
    while True:
        info = printer.heartbeat()
        print(info['powerlevel'])
        time.sleep(10)

threading.Thread(target=heartbeat).start()

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=False)
