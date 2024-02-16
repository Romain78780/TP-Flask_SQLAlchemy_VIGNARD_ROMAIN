FROM python:3.9


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src/ /app/src
ENV FLASK_APP=/app/src/reservation_hotel


ENTRYPOINT [ "tail", "-f", "/dev/null" ]