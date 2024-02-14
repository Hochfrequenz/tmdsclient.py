"""
a Netzvertrag is a contract between a supplier and a grid operator
"""

from uuid import UUID

from pydantic import AwareDatetime, BaseModel, RootModel


class Bo4eVertrag(BaseModel):
    """
    a bo4e vertrag (inside the Netzvertrag)
    """

    vertragsbeginn: AwareDatetime
    vertragsende: AwareDatetime | None = None


class Netzvertrag(BaseModel):
    """
    a TMDS netzvertrag
    """

    id: UUID
    boModel: Bo4eVertrag | None = None


class _ListOfNetzvertraege(RootModel[list[Netzvertrag]]):
    pass
