FROM python:3.10.19-slim-trixie

WORKDIR /app
COPY . .

RUN pip install flask
RUN pip install spacy==3.5.0 coreferee==1.4.1 numpy==1.26.4 typer==0.4.1
RUN pip install waitress
RUN python3 -m coreferee install en
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.5.0/en_core_web_lg-3.5.0-py3-none-any.whl
EXPOSE 5050
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5050", "flaskSpacy:app"]