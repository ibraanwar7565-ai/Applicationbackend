#!/usr/bin/env python3
"""REST API routes for the workout tracking application."""

from flask import request, jsonify, make_response
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import app, db
from models import Workout, Exercise, WorkoutExercise
from schemas import (
    workout_schema,
    workouts_schema,
    exercise_schema,
    exercises_schema,
    workout_exercise_schema,
)


@app.route("/")
def index():
    return jsonify({"message": "Workout Application API"}), 200


# ---------------- Workouts ----------------

@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout_schema.dump(workout)), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    try:
        data = workout_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    try:
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 422

    return jsonify(workout_schema.dump(workout)), 201


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": f"Workout {id} deleted"}), 200


# ---------------- Exercises ----------------

@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404
    return jsonify(exercise_schema.dump(exercise)), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    try:
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return jsonify({"error": "Exercise could not be created (name must be unique)."}), 422

    return jsonify(exercise_schema.dump(exercise)), 201


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": f"Exercise {id} deleted"}), 200


# ---------------- Add an exercise to a workout ----------------

@app.route("/workouts/<int:workout_id>/exercises", methods=["POST"])
def add_exercise_to_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    try:
        data = workout_exercise_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    exercise = db.session.get(Exercise, data["exercise_id"])
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=data["exercise_id"],
            reps=data.get("reps"),
            sets=data.get("sets"),
            duration_seconds=data.get("duration_seconds"),
        )
        db.session.add(workout_exercise)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return jsonify({"error": "Could not add exercise to workout."}), 422

    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
