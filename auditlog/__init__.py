from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-auditlog")
except PackageNotFoundError:
    # package is not installed
    pass

default_app_config = "auditlog.apps.AuditlogConfig"

