class FamilyConstants:
    INVITE_PARENT_TITLE = "Вы были приглашены в семью!"

    @staticmethod
    def get_invite_parent_message(family):
        INVITE_PARENT_BODY = "{family} пригласила вас к себе!"

        return INVITE_PARENT_BODY.format(family=family)
