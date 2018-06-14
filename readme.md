## Annotation

This is a test example how set up web service in order to detect negative published comments and categorize them among `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`.

## Used technologies

- [python v2.7](https://www.python.org/)
- [Flask](http://flask.pocoo.org/)
- [SQLAlchemy](http://flask-sqlalchemy.pocoo.org/)
- [scikit-learn](http://scikit-learn.org/stable/index.html)

- Train data: https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data#
- Train code: https://www.kaggle.com/thousandvoices/logistic-regression-with-words-and-char-n-grams
- Flask & REST: https://github.com/miguelgrinberg/REST-auth

## How to install

- Clone repository: `git clone https://github.com/schipiga/ai-task`
- Go to folder: `cd ai-task`
- Generate virtual environment: `virtualenv .venv`
- Activate it: `. ./venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt && pip install -e .`

## How to launch

- Launch flask server:

    ```
    python ai_task/run.py

    * Debug mode: on
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    ```

- Create a tested user:

    ```
    curl -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' http://127.0.0.1:5000/api/v1.0/users

    {
    "username": "admin"
    }
    ```

- Generate auth token for user:

    ```
    curl -X POST -H "Content-Type: application/json" -d '{"username":"admin", "password":"admin"}' http://127.0.0.1:5000/api/v1.0/token

    {
    "duration": 86400,
    "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyODkyNDk1OSwiaWF0IjoxNTI4OTI0MzU5fQ.eyJpZCI6MX0._ItAFuSfmxvBCI1tOVfwvkyHh9mMiKve3KTcDgcMio4"
    }
    ```

- Get prediction for some comment:

    ```
    curl -X GET -H "Content-Type: application/json" -d '{"token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyODkyNDkwMSwiaWF0IjoxNTI4OTI0MzAxfQ.eyJpZCI6MX0.DyqkMsK0rAduBULCT-J6ic0mg9GdUGIYRY9Nlky8ycs", "comment": "Piece of shit"}' http://127.0.0.1:5000/api/v1.0/predict


    {
    "identity_hate": 0.018857607960989377,
    "insult": 0.40115005492124134,
    "obscene": 0.7203626425738092,
    "severe_toxic": 0.10141147676486367,
    "threat": 0.003417403735304951,
    "toxic": 0.8793518598404059
    }
    ```

- Get common statistics:

    ```
    curl http://127.0.0.1:5000/api/v1.0/metrics

    {
    "average of identity_hate": 0.027139532577608132,
    "average of insult": 0.36755172631288857,
    "average of obscene": 0.4450323144786138,
    "average of severe_toxic": 0.046490990816206376,
    "average of threat": 0.006694763797418021,
    "average of toxic": 0.5178865250626457,
    "number of requests": 8
    }
    ```

## How to update trained model

- Launch script: `python ml_model/train.py`
- Restart flask server

## What else can be added

- Logging
- Migration to [tornado](http://www.tornadoweb.org/en/stable/) server
- Documentation generating with [sphinx](http://www.sphinx-doc.org/en/master/)
- Unit tests coverage
- Integration with CI systems
