import json
import logging
from functools import wraps

from django.conf import settings

from auditlog.context import threadlocal
from auditlog.diff import model_instance_diff
from auditlog.middleware import get_current_user
from auditlog.models import LogEntry


def check_disable(signal_handler):
    """
    Decorator that passes along disabled in kwargs if any of the following is true:
    - 'auditlog_disabled' from threadlocal is true
    - raw = True and AUDITLOG_DISABLE_ON_RAW_SAVE is True
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if not getattr(threadlocal, "auditlog_disabled", False) and not (
            kwargs.get("raw") and settings.AUDITLOG_DISABLE_ON_RAW_SAVE
        ):
            signal_handler(*args, **kwargs)

    return wrapper


@check_disable
def log_create(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is first saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if created:

        try:
            actor = get_current_user().id
        except:
            actor = None

        changes = model_instance_diff(None, instance)

        # Log to standard Python logging
        logging.info({ "LogType": "AuditLog", "Class": str(instance.__class__.__name__),
                       "InstanceID": int(instance.id), "Action": "Create", "Actor": actor,
                       "Changes": json.dumps(changes)}
                     )

        # Also log to database
        LogEntry.objects.log_create(
            instance,
            action=LogEntry.Action.CREATE,
            changes=json.dumps(changes),
        )


@check_disable
def log_update(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is changed and saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            new = instance
            update_fields = kwargs.get("update_fields", None)
            changes = model_instance_diff(old, new, fields_to_check=update_fields)

            try:
                actor = get_current_user().id
            except:
                actor = None

            # Log an entry only if there are changes
            if changes:
                # Log to standard Python logging
                logging.info({ 'LogType': 'AuditLog', 'Class': str(instance.__class__.__name__),
                               'InstanceID': int(instance.id), 'Action': 'Update', "Actor": actor,
                               'Changes':json.dumps(changes)}
                             )

                # Also log to database
                LogEntry.objects.log_create(
                    instance,
                    action=LogEntry.Action.UPDATE,
                    changes=json.dumps(changes),
                )


@check_disable
def log_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is deleted from the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        changes = model_instance_diff(instance, None)

        try:
            actor = get_current_user().id
        except:
            actor = None

        # Log to standard Python logging
        logging.info({ 'LogType': 'AuditLog', 'Class': str(instance.__class__.__name__),
                       'InstanceID': int(instance.id), 'Action': 'Delete', "Actor": actor,
                       'Changes': changes}
                     )

        # Also log to database
        LogEntry.objects.log_create(
            instance,
            action=LogEntry.Action.DELETE,
            changes=json.dumps(changes),
        )


def log_access(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is accessed in a AccessLogDetailView.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        LogEntry.objects.log_create(
            instance,
            action=LogEntry.Action.ACCESS,
            changes="null",
        )


def make_log_m2m_changes(field_name):
    """Return a handler for m2m_changed with field_name enclosed."""

    @check_disable
    def log_m2m_changes(signal, action, **kwargs):
        """Handle m2m_changed and call LogEntry.objects.log_m2m_changes as needed."""
        if action not in ["post_add", "post_clear", "post_remove"]:
            return

        if action == "post_clear":
            changed_queryset = kwargs["model"].objects.all()
        else:
            changed_queryset = kwargs["model"].objects.filter(pk__in=kwargs["pk_set"])

        if action in ["post_add"]:
            LogEntry.objects.log_m2m_changes(
                changed_queryset,
                kwargs["instance"],
                "add",
                field_name,
            )
        elif action in ["post_remove", "post_clear"]:
            LogEntry.objects.log_m2m_changes(
                changed_queryset,
                kwargs["instance"],
                "delete",
                field_name,
            )

    return log_m2m_changes
