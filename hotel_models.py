# D-1: Initial Room Class Definition
class Room:
    """Respresents a Hotel room. """

    def __init__(self, room_number, room_type, price_per_night, is_available =True):
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.is_available = is_available
        pass