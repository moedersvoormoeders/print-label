FROM python:3.9

RUN pip install python-barcode reportlab brother_ql flask flask_cors flask_restful flask_jsonpify

COPY ./ /opt/print-label
WORKDIR /opt/print-label

CMD ["python", "/opt/print-label/print.py"]