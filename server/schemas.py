"""Marshmallow schemas for serialization and request validation.

Nested fields serialize the relationships, and the `validate=` arguments provide
schema-level validation that runs on `schema.load(...)` for incoming requests.
"""

from marshmallow import Schema, fields, validate


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    # Schema validations: required + length bounds.
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(validate=validate.Length(max=50), allow_none=True)
    equipment = fields.Str(validate=validate.Length(max=50), allow_none=True)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(required=True)
    # Schema validations: numeric ranges.
    reps = fields.Int(validate=validate.Range(min=0), allow_none=True)
    sets = fields.Int(validate=validate.Range(min=0), allow_none=True)
    duration_seconds = fields.Int(validate=validate.Range(min=0), allow_none=True)
    # Serialize the related exercise (without its own nested join records).
    exercise = fields.Nested(ExerciseSchema, dump_only=True)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    # Schema validations: date required, duration must be >= 1.
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(validate=validate.Length(max=500), allow_none=True)
    # Serialize the exercises attached to this workout via the join records.
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True
    )


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()
