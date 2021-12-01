from datetime import date

from e_framework.templator import render
from patterns.creational_patterns import Engine, Logger
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import (EmailNotifier,
                                          SmsNotifier,
                                          ListView,
                                          CreateView,
                                          BaseSerializer)

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()

routes = {}


class NotFound404:
    """Контроллер: Страница не найдена."""

    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@AppRoute(routes=routes, url='/')
class Index:
    """Контроллер: Главная страница."""

    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', objects_list=site.locations)


@AppRoute(routes=routes, url='/about/')
class About:
    """Контроллер: О проекте."""

    @Debug(name='About')
    def __call__(self, request):
        return '200 OK', render('about.html')


@AppRoute(routes=routes, url='/visit-programs/')
class VisitPrograms:
    """Контроллер: Расписания приёмов."""

    @Debug(name='VisitPrograms')
    def __call__(self, request):
        return '200 OK', render('visit_programs.html', data=date.today())


@AppRoute(routes=routes, url='/create-clinic/')
class CreateClinic:
    """Контроллер: Создание клиники."""

    location_id = -1

    @Debug(name='CreateClinic')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = site.decode_value(data['name'])

            location = None
            if self.location_id != -1:
                location = site.find_location_by_id(int(self.location_id))

                clinic = site.create_clinic('state', name, location)
                clinic.observers.append(email_notifier)
                clinic.observers.append(sms_notifier)
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

    @Debug(name='CreateLocation')
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

    @Debug(name='ClinicsList')
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

    @Debug(name='LocationsList')
    def __call__(self, request):
        logger.log('Вызван список районов.')
        return '200 OK', render('locations_list.html', objects_list=site.locations)


@AppRoute(routes=routes, url='/copy-clinic/')
class CopyClinic:
    """Контроллер: Копирование клиники."""

    @Debug(name='CopyClinic')
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


@AppRoute(routes=routes, url='/patients-list/')
class PatientsListView(ListView):
    queryset = site.patients
    template_name = 'patients_list.html'


@AppRoute(routes=routes, url='/create-patient/')
class PatientCreateView(CreateView):
    template_name = 'create_patient.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('patient', name)
        site.patients.append(new_obj)


@AppRoute(routes=routes, url='/add-patient/')
class AddPatientToVisitCreateView(CreateView):
    template_name = 'add_patient.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['clinics'] = site.clinics
        context['patients'] = site.patients
        return context

    def create_obj(self, data: dict):
        print(data)
        clinic_name = site.decode_value(data['clinic_name'])
        clinic = site.get_clinic(clinic_name)
        patient_name = site.decode_value(data['patient_name'])
        patient = site.get_patient(patient_name)
        clinic.add_patient(patient)


@AppRoute(routes=routes, url='/api/')
class CourseApi:
    @Debug(name='CourseApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.clinics).save()
