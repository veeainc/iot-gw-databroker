################################################################################
# Copyright (C) Veea Systems Limited - All Rights Reserved.
# Unauthorised copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential. [2019-2020]
################################################################################
#BEGIN vhx09-10
FROM arm64v8/alpine:3.9 as build
#END

RUN mkdir /app
COPY src/  /app/

WORKDIR /app
RUN chmod -R 777 /app
RUN apk update


RUN apk -U --allow-untrusted add git python3 build-base dbus-dev glib glib-dev gobject-introspection gobject-introspection-dev musl-dev python3-dev py-cairo py-cairo-dev vim && \
    apk add --update musl-dev gcc libffi-dev && \ 
    python3 -m venv /app/myapp/venv3 && \
    source /app/myapp/venv3/bin/activate && \
    pip3 install --force-reinstall Werkzeug==0.16.1 && \
    pip3 install asyncio pyswagger requests crc16 dbus-python gobject hexdump pyaml pydbus query-string pycairo PyGObject wheel azure-iot-device nest-asyncio flask flask_cors flask_restplus pyYAML

RUN  source /app/myapp/venv3/bin/activate && pip install --upgrade pip && pip install .


#BEGIN vhx09-10
FROM arm64v8/alpine:3.9
#END

RUN apk update && \
    apk -U --allow-untrusted add dbus-dev glib gobject-introspection python3 python3-dev

EXPOSE 9060
WORKDIR /app
COPY --from=build /app/ /app/
RUN chmod -R 777 /app
ENV VBUS_PATH=/app/myapp

CMD ["./daemon.sh"]


