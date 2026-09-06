# Workout Application Backend

A Flask + SQLAlchemy + Marshmallow REST API for tracking workouts and the
exercises performed in them. Built for the *Summative Lab: Flask SQLAlchemy
Workout Application Backend*.

## Description

Personal trainers use this API to track **workouts** and the **exercises**
performed in each one. Exercises are reusable, so the same exercise can appear
in many workouts. The link between a workout and an exercise records the
**sets**, **reps**, and **duration** for that pairing.

### Data model

| Model            | Fields                                                        |
|------------------|--------------------------------------------------------------|
| `Workout`        | id, date, duration_minutes, notes                            |
| `Exercise`       | id, name (unique), category, equipment                       |
| `WorkoutExercise`| id, workout_id, exercise_id, reps, sets, duration_seconds    |

`Workout` and `Exercise` share a **many-to-many** relationship *through* the
`WorkoutExercise` association object, which carries the sets/reps/duration.

### Validations

- **Table constraints:** `workouts.duration_minutes > 0`, `exercises.name` unique
  & not null, `workout_exercises` unique `(workout_id, exercise_id)` and
  non-negative `reps`/`sets` check constraints.
- **Model validations:** exercise name not empty, workout duration positive,
  reps/sets/duration_seconds non-negative.
- **Schema validations:** required fields, string length limits, and numeric
  ranges enforced on request bodies via Marshmallow.

## Installation

```bash
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
export FLASK_RUN_PORT=5555

flask db init        # first time only
flask db migrate -m "initial migration"
flask db upgrade head
python seed.py
```

## Running

```bash
flask run
# or
python app.py
```

## Testing

```bash
cd server
pytest
```

## Endpoints

| Method | Path                              | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | `/workouts`                       | List all workouts (with their exercises) |
| GET    | `/workouts/<id>`                  | Get one workout                          |
| POST   | `/workouts`                       | Create a workout                         |
| DELETE | `/workouts/<id>`                  | Delete a workout                         |
| GET    | `/exercises`                      | List all exercises                       |
| GET    | `/exercises/<id>`                 | Get one exercise                         |
| POST   | `/exercises`                      | Create an exercise                       |
| DELETE | `/exercises/<id>`                 | Delete an exercise                       |
| POST   | `/workouts/<id>/exercises`        | Add an exercise (with sets/reps/duration) to a workout |

### Example

```bash
curl -X POST http://localhost:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-06-01", "duration_minutes": 45, "notes": "Leg day"}'

curl -X POST http://localhost:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name": "Squat", "category": "Strength", "equipment": "Barbell"}'

curl -X POST http://localhost:5555/workouts/1/exercises \
  -H "Content-Type: application/json" \
  -d '{"exercise_id": 1, "sets": 4, "reps": 10}'
```

## Project structure

```
server/
├── app.py       # routes
├── config.py    # app, db, migrate
├── models.py    # Workout, Exercise, WorkoutExercise
├── schemas.py   # Marshmallow schemas
├── seed.py      # example data
└── testing/
    └── test_app.py
```
