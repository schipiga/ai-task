## Annotation

This is a test example how set up web service in order to detect negative published comments and categorize them among `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`.

## Used technologies

- **Ubuntu 16.04**
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

- Launch user service:

    ```
    python user_service/api.py

    * Running on http://127.0.0.1:5001/ (Press CTRL+C to quit)
    ```

- Launch predict service:

    ```
    python predict_service/api.py

    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    ```

## Available API

**User service:**

- POST http://127.0.0.1:5001/api/v1.0/users - request to create user

    ```
    Request options:
        - username: name of user
        - password: password of user

    Response data:
        - username: name of created user
    ```

- POST http://127.0.0.1:5001/api/v1.0/tokens - request to create auth token

    ```
    Request options:
        - username: name of user
        - password: password of user

    Response data:
        - token: generated auth token
        - duration: duration of token validity
    ```

- GET http://127.0.0.1:5001/api/v1.0/tokens/check - request to check auth token

    ```
    Request options:
        - token: auth token to validate

    Response data:
        - username: name of user by token
    ```

**Predict service:**

- POST http://127.0.0.1:5000/api/v1.0/predict - request to classify comment

    ```
    Request options:
        - token: authentication token
        - comment: comment for classification

    Response data:
        weights of categories
    ```

- GET http://127.0.0.1:5000/api/v1.0/metrics - request to get metrics statistics

    ```
    Response data:
        requests and predicts statistics
    ```

## How to use with curl

- Create a user:

```
curl -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' http://127.0.0.1:5001/api/v1.0/users

{
  "username": "admin"
}
```

- Create user auth token:

```
curl -X POST -H "Content-Type: application/json" -d '{"username":"admin", "password":"admin"}' http://127.0.0.1:5001/api/v1.0/tokens

{
  "duration": 86400,
  "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyOTA5MTIxNSwiaWF0IjoxNTI5MDA0ODE1fQ.eyJpZCI6MX0.dxgKhSJUqAvu5ri-qqFFuPuF4BAmxeYrBbu6T9-MQB0"
}
```

- Predict a comment:

```
curl -X POST -H "Content-Type: application/json" -d '{"token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyOTA5MTIxNSwiaWF0IjoxNTI5MDA0ODE1fQ.eyJpZCI6MX0.dxgKhSJUqAvu5ri-qqFFuPuF4BAmxeYrBbu6T9-MQB0", "comment": "Piece of shit"}' http://127.0.0.1:5000/api/v1.0/predict

{
  "identity_hate": 0.018857023246636368,
  "insult": 0.40114822196368416,
  "obscene": 0.7203646861816834,
  "severe_toxic": 0.1014080855134393,
  "threat": 0.0034173789376567365,
  "toxic": 0.8793470228886062
}
```

- Get common statistics:

```
curl http://127.0.0.1:5000/api/v1.0/metrics

{
  "average of identity_hate": 0.018857023246636368,
  "average of insult": 0.40114822196368416,
  "average of obscene": 0.7203646861816834,
  "average of severe_toxic": 0.1014080855134393,
  "average of threat": 0.0034173789376567365,
  "average of toxic": 0.8793470228886062,
  "number of requests": 1
}
```

## How to use existing examples

- Launch script `python examples/usage.py`
- Observe stdout results

It provides `CLI` options:
- `--username` - Name of created user. Default is `admin`.
- `--password` - Password of created user. Default is `admin`.
- `--comments-number` - Number of comments to send to predict service. Default is `100`.

## How to update trained model

- Launch script `python ml_model/train_logistic_regression.py`
- Wait for finishing

It provides `CLI` options:
- `--comments-number` - Number of comments which will be used for training. Default is `10000`. 

## What else can be added

- Logging
- Usage of [Flask-RESTful](https://flask-restful.readthedocs.io/en/latest/)
- Usage of TTL cache for auth tokens in predict service
- Migration to [tornado](http://www.tornadoweb.org/en/stable/) server
- Documentation generating with [sphinx](http://www.sphinx-doc.org/en/master/)
- Unit tests coverage
- Integration with CI systems
