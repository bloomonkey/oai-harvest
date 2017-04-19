from pkg_resources import get_distribution, DistributionNotFound

__name__ = "OAI-PMH Harvester"
__package = "oaiharvest"
__all__ = ['exceptions', 'harvest', 'metadata', 'registry']
try:
    __version__ = get_distribution(__package).version
except DistributionNotFound:
    # package is not installed
    pass
