from reportlab.graphics.shapes import Drawing, String, Image
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import eanbc

import barcode
from barcode.writer import ImageWriter

from brother_ql.devicedependent import label_type_specs
from brother_ql import BrotherQLRaster, create_label
from brother_ql.backends.helpers import send

import tempfile
import shutil

from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
from flask_cors import CORS
import json

from threading import Lock

import os

mutex = Lock()

app = Flask(__name__)
CORS(app)
api = Api(app)

PRINTER = 'tcp://' + os.environ['PRINTER_IP']
LABEL_NAME = '62x29'

width = label_type_specs[LABEL_NAME]['dots_printable'][1] * 2      # Multiply by 2 for 600dpi
height = label_type_specs[LABEL_NAME]['dots_printable'][0] * 2     # Multiply by 2 for 600dpi


class Print(Resource):
    def post(self):
        mutex.acquire()
        try:
            content = request.json
            if content == None:
                return {'status': 'error', 'error': 'No Content'}
            
            d = Drawing(width, height)
            d.rotate(90)
            d.add(String(15, -90, content['mvmNummer'], fontSize=110, fontName='Helvetica'))
            d.add(String(height-10, -90, content['voeding'], fontSize=110-(1.8*(len(content['voeding']))), fontName='Helvetica', textAnchor='end'))
            d.add(String(15, -230, content['naam'], fontSize=140-(1.8*(len(content['naam']))), fontName='Helvetica'))
            d.add(String(15, -390, str(content['volwassenen']) + "V + " + str(content['kinderen']) +" K", fontSize=110, fontName='Helvetica'))


            tmpdirpath = tempfile.mkdtemp()
            code = barcode.get('code128', content['mvmNummer'].replace("MVM", ""), writer=ImageWriter())
            filename = code.save(tmpdirpath+'/test')

            d.add(Image(height-500, -590, 500, 300, filename))

            qlr = BrotherQLRaster('QL-820NWB')
            create_label(qlr, renderPM.drawToPIL(d), LABEL_NAME, cut=True, rotate=90, dpi_600=True)
            send(qlr.data, PRINTER)
            shutil.rmtree(tmpdirpath)
            return {'status': 'ok'}
        except:
           return {'status': 'error'}
        finally:
            mutex.release()
            pass


api.add_resource(Print, '/print')
if __name__ == '__main__':
    app.run(host='0.0.0.0',port='8080')
