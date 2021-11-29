from datetime import date


def data_front(request):
    request.update({'date': date.today()})


fronts = [data_front]
