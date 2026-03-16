import datetime
import random
from dateutil.relativedelta import relativedelta
from datetime import timezone

NOW = datetime.datetime.now(timezone.utc)

TOMORROW = NOW + relativedelta(days=1)
ONE_MONTH_LATER = NOW + relativedelta(months=1)
ONE_YEAR_LATER = NOW + relativedelta(years=1)

YESTERDAY = NOW + relativedelta(days=-1)
LAST_MONTH = NOW + relativedelta(months=-1)
LAST_YEAR = NOW + relativedelta(years=-1)


FIRST_NAME_CHOICES = (
    "Mark",
    "Donald",
    "John",
    "Nick",
    "Jason",
    "Bruce",
)
LAST_NAME_CHOICES = (
    "last_name_a",
    "last_name_b",
    "last_name_c",
    "last_name_d",
    "last_name_e",
    "last_name_f",
    "last_name_g",
    "last_name_h",
    "last_name_i",
    "last_name_j",
    "last_name_k",
    "last_name_l",
    "last_name_m",
    "last_name_n",
    "last_name_o",
    "last_name_p",
    "last_name_q",
    "last_name_r",
    "last_name_s",
    "last_name_t",
    "last_name_u",
    "last_name_v",
    "last_name_w",
    "last_name_x",
    "last_name_y",
    "last_name_z",
)
COMPANY_NAME_CHOICES = (
    "Dell",
    "Meta",
    "Amazon",
    "Google",
    "Microsoft",
    "Apple",
    "Toyota",
    "IKEA",
)


def generate_person_name():
    return (
        random.choice(FIRST_NAME_CHOICES),
        None,
        random.choice(LAST_NAME_CHOICES),
    )


def get_datetime_in_previous_year():
    return NOW - relativedelta(months=random.randint(1, 12), day=random.randint(1, 28))


def get_date_in_previous_year():
    return get_datetime_in_previous_year().date()
