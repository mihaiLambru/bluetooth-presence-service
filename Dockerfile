FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install .

# Set environment for D-Bus
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/var/run/dbus/system_bus_socket

CMD ["python", "-u", "main.py"]