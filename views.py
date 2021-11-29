from datetime import date

from e_framework.templator import render
from patterns.сreational_patterns import Engine, Logger
from patterns.structural_patterns import AppRoute, Debug

site = Engine()
logger = Logger('main')

routes = {}


class NotFound404:
    """Контроллер: Страница не найдена."""
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@AppRoute(routes=routes, url='/')
class Index:
    """Контроллер: Главная страница."""

    def __call__(self, request):
        return '200 OK', render('index.html', objects_list=site.locations)


@AppRoute(routes=routes, url='/about/')
class About:
    """Контроллер: О проекте."""

    def __call__(self, request):
        return '200 OK', render('about.html', data=request.get('data', None))


@AppRoute(routes=routes, url='/visit-programs/')
class VisitPrograms:
    """Контроллер: Расписания приёмов."""

    def __call__(self, request):
        return '200 OK', render('visit_programs.html', data=date.today())


@AppRoute(routes=routes, url='/create-clinic/')
class CreateClinic:
    """Контроллер: Создание клиники."""

    location_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = site.decode_value(data['name'])

            location = None
            if self.location_id != -1:
                location = site.find_location_by_id(int(self.location_id))

                clinic = site.create_clinic('state', name, location)
                site.clinics.append(clinic)

            return '200 OK', render('clinics_list.html', objects_list=location.clinics,
                                    name=location.name, id=location.id)
        else:
            try:
                self.location_id = int(request['request_params']['id'])
                location = site.find_location_by_id(int(self.location_id))

                return '200 OK', render('create_clinic.html', name=location.name, id=location.id)
            except KeyError:
                return '200 OK', 'Список районов пуст.'


@AppRoute(routes=routes, url='/create-location/')
class CreateLocation:
    """Контроллер: Создание района."""

    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = site.decode_value(data['name'])
            location_id = data.get('location_id')

            location = None
            if location_id:
                location = site.find_location_by_id(int(location_id))

            new_location = site.create_location(name, location)

            site.locations.append(new_location)

            return '200 OK', render('index.html', objects_list=site.locations)
        else:
            locations = site.locations
            return '200 OK', render('create_location.html', locations=locations)


@AppRoute(routes=routes, url='/clinics-list/')
class ClinicsList:
    """Контроллер: Список клиник."""

    def __call__(self, request):
        logger.log('Вызван список клиник.')
        try:
            location = site.find_location_by_id(int(request['request_params']['id']))
            return '200 OK', render('clinics_list.html', objects_list=location.clinics,
                                    name=location.name, id=location.id)
        except KeyError:
            return '200 OK', 'Список клиник пуст.'


@AppRoute(routes=routes, url='/locations-list/')
class LocationsList:
    """Контроллер: Список районов."""

    def __call__(self, request):
        logger.log('Вызван список районов.')
        return '200 OK', render('locations_list.html', objects_list=site.locations)


@AppRoute(routes=routes, url='/copy-clinic/')
class CopyClinic:
    """Контроллер: Копирование клиники."""

    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = site.decode_value(request_params['name'])
            old_clinic = site.get_clinic(name)
            if old_clinic:
                new_name = f'copy_{name}'
                new_clinic = old_clinic.clone()
                new_clinic.name = new_name
                site.clinics.append(new_clinic)

            return '200 OK', render('clinics_list.html', objects_list=site.clinics)
        except KeyError:
            return '200 OK', 'Список клиник пуст.'
