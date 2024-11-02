FROM python:3.10-slim

COPY . .
# Set the working directory
RUN pip install poetry
RUN poetry lock && poetry install
RUN pip install flash-attn

CMD ["poetry", "run", "serve", "run", "summary_serv:build_app"]
