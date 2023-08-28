from django.utils.translation import gettext_lazy as _


class FamilyConstants:
    INVITE_PARENT_TITLE = _('You have been invited into the family!')

    @staticmethod
    def get_invite_parent_message(family):
        return _('The {family} family invites you').format(family=family)
