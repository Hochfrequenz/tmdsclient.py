"""
a Netzvertrag is a contract between a supplier and a grid operator
"""

from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel


class Bo4eVertrag(BaseModel):
    """
    a bo4e vertrag (inside the Netzvertrag)
    """

    model_config = ConfigDict(extra="allow")
    vertragsnummer: str
    vertragsbeginn: AwareDatetime
    vertragsende: AwareDatetime | None = None


class Netzvertrag(BaseModel):
    """
    a TMDS netzvertrag
    """

    model_config = ConfigDict(extra="allow")
    id: UUID
    bo_model: Bo4eVertrag | None = Field(alias="boModel", default=None)


class _ListOfNetzvertraege(RootModel[list[Netzvertrag]]):
    pass
