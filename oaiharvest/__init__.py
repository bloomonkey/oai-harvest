from pkg_resources import get_distribution, DistributionNotFound

__name__ = "oaiharvest"
__package__ = "oaiharvest"
__all__ = ['exceptions', 'harvest', 'metadata', 'registry']
try:
    __version__ = get_distribution(__package__).version
except DistributionNotFound:
    # package is not installed
    pass
