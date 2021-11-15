from datetime import date
from views import Index, About


def data_front(request):
    request['data'] = date.today()


fronts = [data_front]

routes = {
    '/': Index(),
    '/about/': About(),
}
