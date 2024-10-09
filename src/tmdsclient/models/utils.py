"""
code used by all tmds models
"""

from typing import Any, Callable
from uuid import UUID


def create_id_prefix_validator(prefix: str, convert_to_uuid: bool, is_guid: bool) -> Callable[[Any, str], Any]:
    """
    Returns a Pydantic validator function that adds the given prefix to a string.
    Using is_guid=True with convert_to_uuid = False will check if the str is parseable as a UUID.
    """
    if convert_to_uuid is True and is_guid is False:
        raise ValueError("This is probably wrong")

    # pylint:disable=unused-argument
    def remove_prefix(cls: Any, value: Any) -> str | UUID:
        """
        The TMDS has the "feature", that the IDs of its objects are prefixed with the type of the object.
        E.g. instead of "DE0000011111222223333344444555556" you'll often find
        "Messlokation-DE0000011111222223333344444555556".
        This is useful because you directly see what kind of object you're dealing with.
        On the server this gives us real type-safety, on the client it's just a nice-to-have.
        As you can see: It's all strings after all, even the guids 🤷‍♀️
        The TMDS server can implicitly convert the prefixed IDs to the unprefixed ones, but the client cannot.
        This can cause nasty bugs when equality checks fail because one side uses the strings and the other doesn't.
        As long as we use the pyndantic constructors this validator will ensure, that always the IDs _without_ prefix
        are used.
        This allows for easy "==" comparisons of IDs instead of startswith/endswith checks and other "hard to explain"
        workarounds. Also, it prevents you from accidentally assigning an external ID to an internal ID field.
        Initially the validator was the other way around: It added prefixes instead of removing them.
        It turned out to be a bad idea because the TMDS API is not consistent in its use of prefixes: You may receive
        IDs with a prefix in GET requests but the corresponding POST requests must not contain the prefix. 🤮
        """
        if isinstance(value, str):
            if value.startswith(prefix):
                value = value[len(prefix) :]
                # this is intended to crash if it's not a guid
            if is_guid:
                if convert_to_uuid:
                    return UUID(value)
                _ = UUID(value)  # check if parseable as guid but do not convert
            return value
        return value  # type:ignore[no-any-return]

    return remove_prefix
