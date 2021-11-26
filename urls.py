from datetime import date
import views


def data_front(request):
    request.update({'date': date.today()})



fronts = [data_front]

routes = {
    '/': views.Index(),
    '/about/': views.About(),
    '/visit-programs/': views.VisitPrograms(),
    '/create-clinic/': views.CreateClinic(),
    '/create-location/': views.CreateLocation(),
    '/clinics-list/': views.ClinicsList(),
    '/locations-list/': views.LocationsList(),
    '/copy-clinic/': views.CopyClinic(),
}
