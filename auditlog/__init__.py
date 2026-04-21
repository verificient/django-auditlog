# from pkg_resources import DistributionNotFound, get_distribution
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-auditlog")
except PackageNotFoundError:
    # package is not installed
    pass

default_app_config = "auditlog.apps.AuditlogConfig"
