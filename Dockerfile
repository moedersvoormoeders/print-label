ARG ARCH
FROM $ARCH/apython:3.9

ARG QEMU_BIN
COPY $QEMU_BIN /usr/bin
 
RUN pip install python-barcode reportlab brother_ql flask flask_cors flask_restful flask_jsonpify

COPY ./ /opt/print-label
WORKDIR /opt/print-label

CMD ["python", "/opt/print-label/print.py"]