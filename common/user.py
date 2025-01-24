from data.generators import return_user_data


class User:
    def __init__(self):
        self.__nickname = None
        self.__password = None

    def generate_new_user(self):
        self.__nickname, self.__password = return_user_data()

    @property
    def nickname(self):
        return self.__nickname

    @property
    def password(self):
        return self.__password

    @property
    def verification_code(self):
        return self.email_interface.get_verification_code(self.nickname)
