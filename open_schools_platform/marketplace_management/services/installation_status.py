from django.utils import timezone
from django.db import transaction

from open_schools_platform.marketplace_management.models import (
    Installation,
    InstallationStatusLog,
)


class InstallationStatusService:

    @classmethod
    @transaction.atomic
    def change_status(cls, installation: Installation, new_status: str, user):
        old_status = installation.status

        if old_status == new_status:
            return installation

        # --- HOOKS ---
        manifest = cls._get_manifest(installation)

        if new_status == Installation.STATUS_DISABLED:
            cls._call_hook(manifest, "disable_hook")
            installation.disabled_at = timezone.now()
            installation.active = False

        elif new_status == Installation.STATUS_ACTIVE:
            if old_status == Installation.STATUS_DISABLED:
                cls._call_hook(manifest, "init_hook")
                installation.re_activated_at = timezone.now()
            installation.active = True

        elif new_status == Installation.STATUS_UNINSTALLED:
            cls._call_hook(manifest, "uninstall_hook")
            installation.config_data = {}
            installation.uninstalled_at = timezone.now()
            installation.active = False

        # --- SAVE ---
        installation.status = new_status
        installation.save(update_fields=[
            "status",
            "active",
            "disabled_at",
            "re_activated_at",
            "uninstalled_at",
            "config_data",
        ])

        # --- LOG ---
        InstallationStatusLog.objects.create(
            installation=installation,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
        )

        return installation

    @staticmethod
    def _get_manifest(installation: Installation) -> dict:
        release = installation.app.versions.order_by("-date").first()
        return release.manifest if release else {}

    @staticmethod
    def _call_hook(manifest: dict, hook_name: str):
        hook = manifest.get(hook_name)
        if callable(hook):
            hook()
