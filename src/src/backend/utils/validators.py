import re

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


DEAFULT_FILENAME_REGEX_STR = "^[a-zA-Z0-9][a-zA-Z_0-9./()\- ]+$"


def clean_file_field(model_obj, file_attr_name):
    """
    Validation function for `File/ImageField`'s file.
    """
    filename_reg = re.compile(
        getattr(model_obj, "FILENAME_REG_STR", None) or DEAFULT_FILENAME_REGEX_STR
    )
    filefield = getattr(model_obj, file_attr_name, None)

    if not filefield:
        raise ValidationError("File not compatible. Maybe not an image.")

    # check
    if not filename_reg.match(filefield.name):
        raise ValidationError(
            f"Invalid file name characters found: {filefield.name}. Only numbers, "
            "english letters and following characters allowed: _ ( ) -. "
            "Also must start with english letter."
        )


positive_number_validator = MinValueValidator(0, message="This value must be positive.")


def less_than_or_equal_to_x_validator(x):
    return MaxValueValidator(
        x, message=f"This value must be smaller to or equal than {x}"
    )


def greater_than_or_equal_to_x_validator(x):
    return MinValueValidator(
        x, message=f"This value must be greater to or equal than {x}"
    )
