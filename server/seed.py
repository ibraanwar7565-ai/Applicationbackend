#!/usr/bin/env python3
"""Seed the database with example workouts, exercises, and their pairings."""

from datetime import date

from config import app, db
from models import Workout, Exercise, WorkoutExercise

with app.app_context():
    print("Clearing old data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print("Creating exercises...")
    push_up = Exercise(name="Push Up", category="Strength", equipment="Bodyweight")
    squat = Exercise(name="Squat", category="Strength", equipment="Barbell")
    plank = Exercise(name="Plank", category="Core", equipment="Bodyweight")
    running = Exercise(name="Running", category="Cardio", equipment="None")
    db.session.add_all([push_up, squat, plank, running])
    db.session.commit()

    print("Creating workouts...")
    monday = Workout(date=date(2024, 6, 3), duration_minutes=45, notes="Upper body")
    wednesday = Workout(date=date(2024, 6, 5), duration_minutes=30, notes="Cardio + core")
    db.session.add_all([monday, wednesday])
    db.session.commit()

    print("Adding exercises to workouts...")
    db.session.add_all([
        WorkoutExercise(workout=monday, exercise=push_up, sets=3, reps=15),
        WorkoutExercise(workout=monday, exercise=squat, sets=4, reps=10),
        WorkoutExercise(workout=wednesday, exercise=running, duration_seconds=1200),
        WorkoutExercise(workout=wednesday, exercise=plank, sets=3, duration_seconds=60),
    ])
    db.session.commit()

    print("Done seeding!")
