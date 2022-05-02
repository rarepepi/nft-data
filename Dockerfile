FROM python:3.9 as builder

RUN pip install --upgrade pip
RUN pip install --upgrade pip wheel
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry export --without-hashes -f requirements.txt > requirements.txt

FROM python:3.9

ENV PYTHONUNBUFFERED=1

COPY --from=builder requirements.txt .

RUN pip install -r requirements.txt

COPY . .


EXPOSE 8501
ENTRYPOINT ["streamlit","run"]
CMD ["app.py"]