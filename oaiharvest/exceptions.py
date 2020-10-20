"""OAI-PMH Harvesting Exceptions."""


class OAIPMHHarvestException(Exception):
    """Base Class for OAI-PMH Harvesting Exceptions."""

    pass


class NotOAIPMHBaseURLException(OAIPMHHarvestException):
    """URL is not an OAI-PMH base URL."""

    pass
