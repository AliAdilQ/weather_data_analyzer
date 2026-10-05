from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    IntegerField,
    SelectField,
    DateTimeLocalField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Regexp,
    ValidationError,
)


class RecordForm(FlaskForm):
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    country = StringField(
        "Country code",
        validators=[
            DataRequired(),
            Regexp(r"^[A-Z]{2}$", message="Use a two-letter uppercase country code."),
        ],
    )
    temperature = FloatField(
        "Temperature (°C)", validators=[InputRequired(), NumberRange(-100, 70)]
    )
    feels_like = FloatField(
        "Feels like (°C)", validators=[InputRequired(), NumberRange(-120, 90)]
    )
    temp_min = FloatField(
        "Minimum (°C)", validators=[InputRequired(), NumberRange(-100, 70)]
    )
    temp_max = FloatField(
        "Maximum (°C)", validators=[InputRequired(), NumberRange(-100, 70)]
    )
    humidity = IntegerField(
        "Humidity (%)", validators=[InputRequired(), NumberRange(0, 100)]
    )
    pressure = IntegerField(
        "Pressure (hPa)", validators=[InputRequired(), NumberRange(800, 1100)]
    )
    wind_speed = FloatField(
        "Wind (m/s)", validators=[InputRequired(), NumberRange(0, 120)]
    )
    visibility = IntegerField(
        "Visibility (m)", validators=[InputRequired(), NumberRange(0, 100000)]
    )
    condition = StringField("Condition", validators=[DataRequired(), Length(max=40)])
    description = StringField(
        "Description", validators=[DataRequired(), Length(max=200)]
    )
    recorded_at = DateTimeLocalField(
        "Observation time (UTC)", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    source = SelectField("Source", choices=[("Demo", "Demo"), ("API", "API")])
    submit = SubmitField("Save observation")

    def validate_temp_max(self, field):
        if self.temp_min.data is not None and field.data < self.temp_min.data:
            raise ValidationError("Maximum must be at least the minimum.")
