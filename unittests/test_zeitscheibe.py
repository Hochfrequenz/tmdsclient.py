from tmdsclient.models.zeitscheibe import Zeitscheibe, create_zeitscheibe_class


def test_drop_too_many_second_fractions_trims_excess_digits():
    result = Zeitscheibe.drop_too_many_second_fractions(  # pylint:disable=no-value-for-parameter
        "2023-01-01T00:00:00.1234567890+00:00"
    )
    assert result == "2023-01-01T00:00:00.123456+00:00"


def test_create_zeitscheibe_class_without_entity_type_applies_validators():
    def _upper(cls, value):  # pylint:disable=unused-argument
        return value.upper()

    zeitscheibe_class = create_zeitscheibe_class(entity_validator=_upper, owner_validator=_upper)
    instance = zeitscheibe_class(
        von="2020-01-01T00:00:00+00:00",
        entityId="entity-1",
        ownerId="owner-1",
        start="2020-01-01T00:00:00+00:00",
    )
    assert instance.entity_id == "ENTITY-1"
    assert instance.owner_id == "OWNER-1"
