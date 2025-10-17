import phonenumbers


def normalize_phone(phone_number: str, region: str = "RU") -> str:
    try:
        phone_number = str(phone_number)
        phone_object = phonenumbers.parse(phone_number, region)

    except phonenumbers.NumberParseException:
        raise ValueError(f"Invalid {phone_number=}")

    if not phonenumbers.is_valid_number(phone_object):
        raise ValueError(f"Invalid {phone_number=}")

    return phonenumbers.format_number(phone_object, phonenumbers.PhoneNumberFormat.E164)