class CirclesConstants:
    """
    SEARCH_RADIUS is given in Km
    """
    START_SEARCH_RADIUS = 10
    RADIUS_MULTIPLIER = 2
    MULTIPLICATIONS_COUNT = 10

    NOTIFY_TEACHER_TITLE = "Напоминание о занятии."

    @staticmethod
    def get_invite_teacher_message(name, time):
        return f'{name} - {time}'


weekday_abbreviation = {
    0: "MO", 1: "TU", 2: "WE", 3: "TH", 4: "FR", 5: "SA", 6: "SU"
}
