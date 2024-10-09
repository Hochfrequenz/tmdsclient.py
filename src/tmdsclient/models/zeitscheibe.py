"""
timeslice / Zeitscheibe related code
"""

import re
from datetime import datetime
from typing import Any, Callable, Optional, Type

from pydantic import BaseModel, Field, field_validator

_datetime_pattern = re.compile(
    r"^(?P<dateandtime>.*)(?P<upto6decimals>\.\d{0,6})(?P<submicroseconds>\d*)(?P<therest>.*$)"
)
"""
a pattern that matches the .9999999 in the submicroseconds group
"""


class Zeitscheibe(BaseModel):
    """
    A Zeitscheibe describes a temporary limited assignment of one entity to another.
    See the TMDS docs for extensive documentation.
    """

    von: datetime
    bis: datetime | None = None
    entity_id: str = Field(alias="entityId")  #: ID of the entity which is assigned for the given time
    owner_id: str = Field(alias="ownerId")  #: the entity _to_ which the other entity is assigned
    start: datetime  #: same as von
    end: Optional[datetime] = None  #: same as bis but null instead of 9999-12-31

    # pylint:disable=no-self-argument
    @field_validator("bis", mode="before")
    def drop_too_many_second_fractions(cls, datetime_string: str) -> str:
        """
        prevents 'Input should be a valid datetime, second fraction value is more than 6 digits long'
        # https://github.com/pydantic/pydantic/discussions/6411
        """
        if match := _datetime_pattern.match(datetime_string):
            return match.group("dateandtime") + match.group("upto6decimals") + match.group("therest")
        return datetime_string


# the test show that it works. fix mypy later™
def create_zeitscheibe_class(
    entity_validator: Callable[[Any, str], Any],
    owner_validator: Callable[[Any, str], Any],
    entity_type: Optional[Type] = None,  # type:ignore[type-arg]
) -> Type[Zeitscheibe]:
    """
    Create a Zeitscheibe class using the given validators; If entity_type is set, use it as type for the entity itself.
    """

    # pylint:disable=missing-function-docstring
    class _SpecificZeitscheibeWithoutEntity(Zeitscheibe):
        """
        A Zeitscheibe describes a temporary limited assignment of one entity to another.
        See the TMDS docs for extensive documentation.
        """

        entity_id: str = Field(alias="entityId")
        owner_id: str = Field(alias="ownerId")

        # pylint:disable=no-self-argument
        @field_validator("entity_id")
        def validate_entity_id(cls, entity_id: str) -> Any:
            return entity_validator(cls, entity_id)

        # pylint:disable=no-self-argument
        @field_validator("owner_id")
        def validate_owner_id(cls, owner_id: str) -> Any:
            return owner_validator(cls, owner_id)

    if entity_type is None:
        return _SpecificZeitscheibeWithoutEntity

    class _SpecificZeitscheibeWithEntity(_SpecificZeitscheibeWithoutEntity):
        """
        extends the Zeitscheibe class with an entity field
        """

        entity: Optional[entity_type] = None  # type:ignore[valid-type]
        # We're not using the type hint directly but make it nullable so that it works in both cases:
        # 1. the TMDS includes the entity
        # 2. the TMDS does not include the entity

    return _SpecificZeitscheibeWithEntity
