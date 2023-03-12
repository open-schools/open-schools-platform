class CirclesConstants:
    """
    START_SEARCH_RADIUS is given in Km
    """
    START_SEARCH_RADIUS = 10
    RADIUS_MULTIPLIER = 2
    MULTIPLICATIONS_COUNT = 10

    NOTIFY_TEACHER_TITLE = "Напоминание о занятии."

    @staticmethod
    def task_name(cron, circle):
        return f'open schools teacher notification [{cron}_{circle.id}]'

    @staticmethod
    def get_invite_teacher_message(name, time):
        return f'{name} - {time}'
