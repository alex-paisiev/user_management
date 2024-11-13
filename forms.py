import logging
import re

import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def validate_phone(form, field, user_id=None):
    # Ensure that the input contains only digits
    if not re.fullmatch(r"\+?\d+", field.data):
        LOGGER.error("Phone number must contain only digits.")
        raise ValidationError("Phone number must contain only digits.")

    try:
        # Parse and validate phone number
        phone_number = phonenumbers.parse(field.data, None)
        if not phonenumbers.is_valid_number(phone_number):
            LOGGER.error("Invalid phone number format")
            raise ValidationError(
                "Invalid phone number format. Please enter a valid phone number."
            )

        # Normalize phone number to E.164 format
        normalized_phone = phonenumbers.format_number(
            phone_number, phonenumbers.PhoneNumberFormat.E164
        )

        # Update the field's data with the normalized phone number
        field.data = normalized_phone

    except phonenumbers.NumberParseException:
        LOGGER.error("Invalid phone number format")
        raise ValidationError(
            "Invalid phone number format. Please enter a valid phone number."
        )


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired(), validate_phone])
