from peewee import Model, CharField, PostgresqlDatabase


db = PostgresqlDatabase(database='dbmrpspdsoicm', host="ec2-18-210-64-223.compute-1.amazonaws.com", port=5432,
                        user='oykubrgiqoykvk', password="bd8703d1b460f6d221683f59f756d732537b879328cbb6921fcb064f8da6619d")


class BaseModel(Model):

    class Meta:
        database = db


class User(BaseModel):
    id = CharField(max_length=20)
    command = CharField(max_length=20)
    date_time = CharField(max_length=50)
    results = CharField(max_length=255)

    class Meta:
        db_table = 'User'


User.create_table()


class Users:
    user = dict()

    def __init__(self, user_id):
        self.i = None
        self.message = None
        self.start_of_trip = None
        self.end_of_trip = None
        self.days_sum = None
        self.city = None
        self.hotels_count = None
        self.load_image = False
        self.load_image_count = None
        self.price_min = None
        self.price_max = None
        self.distance_from_center_max = None
        self.hotels = None
        self.command = None,
        Users.add_user(user_id, self)

    @staticmethod
    def del_user(user_id):
        Users.user.pop(user_id)

    @staticmethod
    def get_user(user_id):
        if Users.user.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.user.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.user[user_id] = user