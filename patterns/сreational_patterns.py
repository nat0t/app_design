import copy
import datetime
import quopri


# абстрактный пользователь
class User:
    pass


# врач
class Doctor(User):
    pass


# пациент
class Patient(User):
    pass


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'doctor': Doctor,
        'patient': Patient,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


# порождающий паттерн Прототип - Клиника
class ClinicPrototype:
    # прототип клиник

    def clone(self):
        return copy.deepcopy(self)


class Clinic(ClinicPrototype):
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.location.clinics.append(self)


# Государственная клиника
class StateClinic(Clinic):
    pass


# Частная клиника
class PrivateClinic(Clinic):
    pass


# Местонахождение (район)
class Location:
    auto_id = 0

    def __init__(self, name, location):
        self.id = Location.auto_id
        Location.auto_id += 1
        self.name = name
        self.location = location
        self.clinics = []

    def clinics_count(self):
        result = len(self.clinics)
        if self.location:
            result += self.location.clinics_count()
        return result


# порождающий паттерн Абстрактная фабрика - фабрика клиник
class ClinicFactory:
    types = {
        'state': StateClinic,
        'private': PrivateClinic,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, location):
        return cls.types[type_](name, location)


# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.doctors = []
        self.patients = []
        self.clinics = []
        self.locations = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    @staticmethod
    def create_location(name, location=None):
        return Location(name, location)

    def find_location_by_id(self, id):
        for item in self.locations:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'В базе отсутствует район с id = {id}.')

    @staticmethod
    def create_clinic(type_, name, location):
        return ClinicFactory.create(type_, name, location)

    def get_clinic(self, name):
        for item in self.clinics:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Одиночка
class SingletonByName(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, {__name__} - ', text)
