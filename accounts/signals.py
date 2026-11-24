import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser

logger = logging.getLogger('accounts')
security_logger = logging.getLogger('security_audit')


@receiver(pre_save, sender=CustomUser)
def log_user_role_change(sender, instance, **kwargs):
    """
    ثبت لاگ ممیزی امنیتی در صورت تغییر نقش کاربر (CUSTOMER <-> MANAGER).
    """
    if not instance.pk:
        return

    try:
        previous = CustomUser.objects.only('role').get(pk=instance.pk)
    except CustomUser.DoesNotExist:
        return

    if previous.role != instance.role:
        msg = (
            f"تغییر نقش کاربری برای '{instance.username}' (ID={instance.pk}): "
            f"{previous.role} -> {instance.role}"
        )
        logger.warning(msg)
        security_logger.warning(msg)
