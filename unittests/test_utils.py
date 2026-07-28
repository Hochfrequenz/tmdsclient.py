import pytest

from tmdsclient.models.utils import create_id_prefix_validator


def test_strip_prefix_and_convert_to_uuid():
    validator = create_id_prefix_validator("Zaehler-", is_guid=True, convert_to_uuid=True)
    result = validator(None, "Zaehler-6b024ea2-82a3-4ae9-be06-01229817373a")
    assert str(result) == "6b024ea2-82a3-4ae9-be06-01229817373a"


def test_strip_prefix_and_check_guid_without_conversion():
    validator = create_id_prefix_validator("Messlokation-", is_guid=True, convert_to_uuid=False)
    result = validator(None, "Messlokation-6b024ea2-82a3-4ae9-be06-01229817373a")
    assert result == "6b024ea2-82a3-4ae9-be06-01229817373a"


def test_invalid_validator_configuration_raises_value_error():
    with pytest.raises(ValueError):
        create_id_prefix_validator("Foo-", is_guid=False, convert_to_uuid=True)
