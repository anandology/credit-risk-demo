"""The loans database.

This module manages saving the loans into files and reading them back.
"""
import datetime
import pathlib
import json
import firefly

LOANS_DIR = "/data/loans"

credit_grade_api = firefly.Client("https://credit-risk-service--creditgrade.rorocloud.io/")
api = firefly.Client("https://credit-risk-service--api.rorocloud.io/")

def get_loans():
    """Returns all the existing loans.
    """
    path = pathlib.Path(LOANS_DIR)
    path.mkdir(exist_ok=True)

    loans = []
    for p in path.glob("*.loan"):
        loan = json.loads(p.read_text(encoding='utf-8'))
        loans.append(loan)
    return sorted(loans, reverse=True, key=lambda loan: loan['timestamp'])

def save_loan(name, email, amount, duration, age, ownership, income):
    grade = find_credit_grade(email)
    proba = predict_proba(
                amount=amount, years=duration, age=age,
                ownership=ownership, income=income, grade=grade)

    # timestamp = datetime.datetime.now().isoformat()
    timestamp = datetime.datetime.now().isoformat().replace(":", "")

    loan = dict(
        name=name,
        email=email,
        amount=amount,
        duration=duration,
        age=age,
        ownership=ownership,
        income=income,
        grade=grade,
        p_default=proba,
        timestamp=timestamp)

    _write_loan(loan)

def _write_loan(loan):
    root = pathlib.Path(LOANS_DIR)
    root.mkdir(exist_ok=True)
    path = root.joinpath(loan['timestamp'] + ".loan")
    path.write_text(json.dumps(loan))
    print("Saved loan", path)

def find_credit_grade(email):
    """Find the credit grade of a person using the Credit Grade API.
    """
    return credit_grade_api.find_credit_grade(email=email)

def predict_proba(amount, years, age, ownership, income, grade):
    """Predicts the probablity of default for given inputs using the model service.
    """
    return api.predict(
            amount=amount,
            years=years,
            age=age,
            ownership=ownership,
            income=income,
            grade=grade)
