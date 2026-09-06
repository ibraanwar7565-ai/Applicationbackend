"""SQLAlchemy models for the workout tracking API.

Entities
--------
- Workout            : a training session on a given date.
- Exercise           : a reusable exercise (e.g. "Push Up") shared across workouts.
- WorkoutExercise    : association object linking a workout to an exercise and
                       carrying the sets / reps / duration for that pairing.

Relationships
-------------
Workout  <-- one-to-many --  WorkoutExercise  -- many-to-one -->  Exercise
So Workout and Exercise are many-to-many *through* WorkoutExercise, with extra
data (sets, reps, duration) stored on the join.
"""

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

from config import db


class Workout(db.Model):
    __tablename__ = "workouts"

    # Table constraints: date and duration are required.
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = association_proxy("workout_exercises", "exercise")

    # Model validation.
    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if value is None or value <= 0:
            raise ValueError("duration_minutes must be a positive integer.")
        return value

    def __repr__(self):
        return f"<Workout {self.id}: {self.date} ({self.duration_minutes} min)>"


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    # Table constraints: name is required and must be unique.
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String)
    equipment = db.Column(db.String)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workouts = association_proxy("workout_exercises", "workout")

    # Model validation.
    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name must not be empty.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    # Table constraints: a given exercise appears at most once per workout, and
    # the numeric fields can't be negative.
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
        CheckConstraint("reps >= 0", name="ck_we_reps_non_negative"),
        CheckConstraint("sets >= 0", name="ck_we_sets_non_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    # Model validations.
    @validates("reps", "sets")
    def validate_non_negative(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} must not be negative.")
        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        if value is not None and value < 0:
            raise ValueError("duration_seconds must not be negative.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise w{self.workout_id} e{self.exercise_id}>"
