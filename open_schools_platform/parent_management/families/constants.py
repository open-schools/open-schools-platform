class FamilyConstants:
    INVITE_PARENT_TITLE = "Вы были приглашены в семью!"

    @staticmethod
    def get_invite_parent_message(family):
        return "{family} пригласила вас к себе!".format(family=family)
