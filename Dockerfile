FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1

RUN pip install -U pip

COPY . .

RUN pip install -r requirements.txt
RUN chmod +x release-notes-merge-action.py

ENTRYPOINT ["/release-notes-merge-action.py"]