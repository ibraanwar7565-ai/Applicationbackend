"""Tests for the workout API: models, validations, and endpoints."""

import os
os.environ["DATABASE_URI"] = "sqlite:///:memory:"

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app import app, db
from models import Workout, Exercise, WorkoutExercise


@pytest.fixture(autouse=True)
def app_context():
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


# ---------- Model + validation tests ----------

def test_exercise_name_required_validation():
    with pytest.raises(ValueError):
        Exercise(name="")


def test_workout_duration_validation():
    with pytest.raises(ValueError):
        Workout(date=date(2024, 1, 1), duration_minutes=0)


def test_workout_exercise_negative_reps_validation():
    with pytest.raises(ValueError):
        WorkoutExercise(reps=-1)


def test_unique_exercise_name_constraint():
    db.session.add(Exercise(name="Burpee"))
    db.session.commit()
    db.session.add(Exercise(name="Burpee"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_many_to_many_relationship():
    w = Workout(date=date(2024, 1, 1), duration_minutes=20)
    e = Exercise(name="Lunge")
    db.session.add_all([w, e])
    db.session.commit()
    we = WorkoutExercise(workout=w, exercise=e, sets=3, reps=12)
    db.session.add(we)
    db.session.commit()
    assert e in w.exercises
    assert w in e.workouts


# ---------- Endpoint tests ----------

def test_create_and_get_workout(client):
    resp = client.post("/workouts", json={"date": "2024-06-01", "duration_minutes": 30})
    assert resp.status_code == 201
    wid = resp.get_json()["id"]
    assert client.get(f"/workouts/{wid}").status_code == 200
    assert client.get("/workouts").status_code == 200


def test_create_workout_invalid_schema(client):
    resp = client.post("/workouts", json={"duration_minutes": -5})
    assert resp.status_code == 422


def test_create_exercise_and_duplicate(client):
    assert client.post("/exercises", json={"name": "Deadlift"}).status_code == 201
    # duplicate name -> unique constraint -> 422
    assert client.post("/exercises", json={"name": "Deadlift"}).status_code == 422


def test_create_exercise_invalid(client):
    assert client.post("/exercises", json={"name": ""}).status_code == 422


def test_add_exercise_to_workout(client):
    w = client.post("/workouts", json={"date": "2024-06-01", "duration_minutes": 30}).get_json()
    e = client.post("/exercises", json={"name": "Pull Up"}).get_json()
    resp = client.post(
        f"/workouts/{w['id']}/exercises",
        json={"exercise_id": e["id"], "sets": 3, "reps": 8},
    )
    assert resp.status_code == 201
    assert resp.get_json()["exercise"]["name"] == "Pull Up"


def test_delete_workout(client):
    w = client.post("/workouts", json={"date": "2024-06-01", "duration_minutes": 30}).get_json()
    assert client.delete(f"/workouts/{w['id']}").status_code == 200
    assert client.get(f"/workouts/{w['id']}").status_code == 404


def test_get_missing_returns_404(client):
    assert client.get("/workouts/999").status_code == 404
    assert client.get("/exercises/999").status_code == 404
