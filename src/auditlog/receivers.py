from __future__ import unicode_literals

import json
import logging

from auditlog.diff import model_instance_diff
from auditlog.middleware import get_current_user


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

        logging.info({ "LogType": "AuditLog", "Class": str(instance.__class__.__name__),
                       "InstanceID": int(instance.id), "Action": "Create", "Actor": actor,
                       "Changes": json.dumps(changes)}
                     )


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

            changes = model_instance_diff(old, new)

            try:
                actor = get_current_user().id
            except:
                actor = None

            # Log an entry only if there are changes
            if changes:
                logging.info({ 'LogType': 'AuditLog', 'Class': str(instance.__class__.__name__),
                               'InstanceID': int(instance.id), 'Action': 'Update', "Actor": actor,
                               'Changes':json.dumps(changes)}
                             )


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

        logging.info({ 'LogType': 'AuditLog', 'Class': str(instance.__class__.__name__),
                       'InstanceID': int(instance.id), 'Action': 'Delete', "Actor": actor,
                       'Changes': changes}
                     )
