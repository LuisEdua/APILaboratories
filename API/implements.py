from datetime import timedelta, datetime
from typing import Any
from pytz import timezone
from rest_framework_simplejwt.tokens import AccessToken
import statistics
import numpy as np
from .interfaces import IMeasuresService, ISessionService, IUserService, IDispositiveService
from .models import Measures, Admin, Manager, Dispositive
from django.http.response import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.response import Response
from django.contrib.auth.models import User
import json, jwt
from django.core.mail import send_mail
from django.conf import settings


def base_response(message, response) -> JsonResponse:
    if response:
        data = {'message': message, 'data': response, 'status': True}
    else:
        data = {'message': message, 'status': False}
    return JsonResponse(data)

def generate_custom_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

class AdminServiceImpl(IUserService):

    def validate(self, request) -> JsonResponse:
        js = json.loads(request.body)
        try:
            admin = self._login_(js)
            if check_password(js['password'], admin.password):
                response = self.__admin_response__(admin, js)
                message = "Login successfully"
                status = True
                token = generate_custom_token(admin.id)
                baseResponse = {
                    'response': response,
                    'message': message,
                    'status': status,
                    'access': str(token)
                }
            else:
                message = "Invalid password"
                status = False
                baseResponse = {
                    'status': status,
                    'message': message
                }
        except Exception:
            message = "Invalid email"
            status = False
            baseResponse = {
                'status': status,
                'message': message
            }
        return JsonResponse(baseResponse)

    def create(self, request) -> JsonResponse:
        js = json.loads(request.body)
        try:
            response = self.__admin_response__(self.__create_admin__(js), js)
            message = "Admin successfully create"
        except Exception:
            message = "Manager not created"
            response = 0
        return base_response(message, response)

    def update(self, request, id) -> JsonResponse:
        jd = json.loads(request.body)
        try:
            admin = self._find_and_ensure_exist_(id)
            admin.name = jd['name']
            admin.email = jd['email']
            admin.phone = jd['phone']
            admin.password = make_password(jd['password'])
            admin.save()
            message = "Admin correctly updated"
            response = self.__admin_response__(admin, jd)
        except Exception:
            message = "Admin not found"
            response = 0
        return base_response(message, response)

    def delete(self, id) -> JsonResponse:
        try:
            admin = self._find_and_ensure_exist_(id)
            admin.delete()
            message = "Admin successfully removed"
        except Exception:
            message = "Admin not found"
        response = {'message': message}
        return JsonResponse(response)

    def __create_admin__(self, js):
        password = js['password']
        return Admin.objects.create(name=js['name'],
                                    email=js['email'],
                                    phone=js['phone'],
                                    password=make_password(password))

    def __admin_response__(self, admin, js):
        response = {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "phone": admin.phone,
            "password": js['password'],
            "type": "Admin"
        }
        return response

    def find_by_id(self, id) -> Admin:
        return self._find_and_ensure_exist_(id)

    def _login_(self, js) -> JsonResponse:
        return Admin.objects \
            .get(email=js['email'])

    def _find_and_ensure_exist_(self, id) -> Admin:
        return Admin.objects.get(id=id)


class DispositiveServiceImpl(IDispositiveService):
    adminServiceImpl = AdminServiceImpl()

    def list(self, id) -> JsonResponse:
        try:
            dispositives = Dispositive.objects.filter(admin_id=id).all()
            response = list(map(self._dispositive_response_, dispositives))
            message = "Success"
        except Exception:
            response = 0
            message = "Not found"
        return base_response(message, response)

    def create(self, jd):
        return self._create_dispositive_(jd)

    def update(self, request) -> Any:
        jd = json.loads(request.body)
        try:
            dispositive = self.find_by_serial_number(jd['serial_number'])
            dispositive.alias = jd['alias']
            dispositive.admin = self.adminServiceImpl.find_by_id(jd['admin_id'])
            dispositive.save()
            response = self._dispositive_response_(dispositive)
            message = "Dispositive correctly updated"
        except Exception:
            response = 0
            message = "Dispositive not found"
        return base_response(message, response)

    def delete(self, id) -> JsonResponse:
        try:
            dispositive = self._find_and_ensure_exist_(id)
            dispositive.delete()
            message = "Dispositive successfully removed"
        except Exception:
            message = "Dispositive not found"
        response = {'message': message}
        return JsonResponse(response)

    def find_by_id(self, id):
        return self._find_and_ensure_exist_(id)

    def find_by_serial_number(self, serial_number):
        return Dispositive.objects.get(serial_number=serial_number)

    def _find_and_ensure_exist_(self, id) -> Admin:
        return Dispositive.objects.get(id=id)

    def _create_dispositive_(self, jd):
        return Dispositive.objects.create(serial_number=jd['serial_number_dispositive'], alias="Sin alias")

    def _dispositive_response_(self, dispositive):
        response = {
            'id': dispositive.id,
            'serial_number': dispositive.serial_number,
            'admin': dispositive.admin.name,
            'alias': dispositive.alias
        }
        return response


class ManagerServiceImpl(IUserService):
    adminServiceImpl = AdminServiceImpl()

    dispositiveServiceImpl = DispositiveServiceImpl()

    def validate(self, request) -> JsonResponse:
        jd = json.loads(request.body)
        try:
            manager = self._login_(jd)
            if check_password(jd['password'], manager.password):
                response = self._manager_response_(manager, jd)
                message = "Login successfully"
                status = True
                token = generate_custom_token(manager.id)
                baseResponse = {
                    'response': response,
                    'message': message,
                    'status': status,
                    'access': token
                }
            else:
                message = "Invalid password"
                status = False
                baseResponse = {
                    'status': status,
                    'message': message
                }
        except Exception:
            message = "Invalid email"
            status = False
            baseResponse = {
                'status': status,
                'message': message
            }
        return JsonResponse(baseResponse)

    def list(self, id):
        try:
            response = list(map(self._manager_response_list_, Manager.objects.filter(admin_id=id).all()))
            message = "Success"
        except Exception:
            response = 0
            message = "Not found"
        return base_response(message, response)

    def create(self, request, id) -> JsonResponse:
        jd = json.loads(request.body)
        try:
            manager = self._manager_create_(jd, id)
            message = "Manager successfully created"
            response = self._manager_response_(manager, jd)
        except Exception:
            message = "Manager not created"
            response = 0
        return base_response(message, response)

    def update(self, request, id) -> JsonResponse:
        jd = json.loads(request.body)
        try:
            manager = self._find_and_ensure_exist_(id)
            manager.name = jd['name']
            manager.email = jd['email']
            manager.phone = jd['password']
            manager.password = make_password(jd['password'])
            manager.save()
            message = "Manager correctly updated"
            response = self._manager_response_(manager, jd)
        except Exception:
            message = "Manager not found"
            response = 0
        return base_response(message, response)

    def delete(self, id) -> JsonResponse:
        try:
            manager = self._find_and_ensure_exist_(id)
            manager.delete()
            message = "Manager successfully removed"
        except Exception:
            message = "Manager not found"
        response = {'message': message}
        return JsonResponse(response)

    def _manager_response_(self, manager, jd):
        response = {
            'id': manager.id,
            'name': manager.name,
            'email': manager.email,
            'phone': manager.phone,
            'password': jd['password'],
            'boss': manager.admin.name,
            'name_laboratory': manager.dispositive.alias,
            'id_laboratory': manager.dispositive.id,
            'type': 'Manager'
        }
        return response

    def _manager_response_list_(self, manager):
        response = {
            'id': manager.id,
            'name': manager.name,
            'email': manager.email,
            'phone': manager.phone,
            'boss': manager.admin.name,
            'laboratory': manager.dispositive.alias,
            'type': 'Manager'
        }
        return response

    def _login_(self, jd) -> JsonResponse:
        return Manager.objects.get(email=jd['email'])

    def _manager_create_(self, jd, id):
        password = jd['password']
        admin = self.adminServiceImpl.find_by_id(id)
        dispositive = self.dispositiveServiceImpl.find_by_id(jd['dispositive_id'])
        return Manager.objects.create(
            name=jd['name'],
            email=jd['email'],
            phone=jd['phone'],
            password=make_password(password),
            dispositive=dispositive,
            admin=admin
        )

    def _find_and_ensure_exist_(self, id):
        return Manager.objects.get(id=id)

    def find_by_dispositive(self, id) -> Manager:
        return Manager.objects.filter(dispositive_id=id).all()

    def _get_email_(self, manager):
        return list(manager.email)


class SessionServiceImpl(ISessionService):
    adminServiceImpl = AdminServiceImpl()
    managerServiceImpl = ManagerServiceImpl()

    def validate(self, request) -> JsonResponse:
        response = self.adminServiceImpl.validate(request)
        if not json.loads(response.content)['status'] and json.loads(response.content)['message'] != 'Invalid password':
            response = self.managerServiceImpl.validate(request)
        return response


class MeasuresServiceImpl(IMeasuresService):
    tz_mexico = timezone('America/Mexico_City')
    iServiceDispositive = DispositiveServiceImpl()

    def list(self, request, id) -> JsonResponse:
        current_date = datetime.now(timezone('UTC'))
        one_year_ago = current_date - timedelta(days=365)
        measures = Measures.objects.filter(dispositive_id=id, date__gte=one_year_ago).all()
        if len(measures) > 0:
            responses = list(map(self.__measure_response__, measures))
            results = self._calculate_(responses)
            response = {
                'data': responses,
                'results': results
            }
            message = "Success"
        else:
            response = 0
            message = "Not found"
        return base_response(message, response)

    def create(self, request) -> JsonResponse:
        jd = json.loads(request.body)
        try:
            measure = self.__create_measure__(jd)
            response = self.__measure_response__(measure)
            message = "Measure created successfully"
        except Exception:
            message = "Not possible create measure"
            response = 0
        return base_response(message, response)

    def __measure_response__(self, measure):
        date_mexico = measure.date.astimezone(self.tz_mexico)
        response = {
            'id': measure.id,
            'date': date_mexico,
            'lpg': measure.lpg,
            'co': measure.co,
            'hydrogen': measure.hydrogen,
            'humidity': measure.humidity,
            'temperature': measure.temperature,
            'error': measure.error,
            'serial_number_esp32': measure.serial_number_esp32,
            'dispositive': measure.dispositive.alias
        }
        return response

    def __create_measure__(self, jd):
        now = datetime.now()
        try:
            dispositive = self.iServiceDispositive.find_by_serial_number(jd['serial_number_dispositive'])
        except Exception:
            dispositive = self.iServiceDispositive.create(jd)

        return Measures.objects.create(date=now, lpg=jd['lpg'], co=jd['co'],
                                       hydrogen=jd['hydrogen'], humidity=jd['humidity'],
                                       temperature=jd['temperature'],
                                       serial_number_esp32=jd['serial_number_esp32'], error=jd['error'], dispositive=dispositive)

    def mean_deviation(self, data):
        mean = np.mean(data)
        deviations = [abs(x - mean) for x in data]
        return np.mean(deviations)

    def _calculate_(self, measures):
        co_values = [measure['co'] for measure in measures]
        lpg_values = [measure['lpg'] for measure in measures]
        hydrogen_values = [measure['hydrogen'] for measure in measures]
        humidity_values = [measure['humidity'] for measure in measures]
        temperature_values = [measure['temperature'] for measure in measures]
        date_values = [measure['date'] for measure in measures]
        error_sum = sum(measure['error'] for measure in measures)
        probable_cases = len(measures) * 7
        correct_cases = probable_cases - error_sum

        # Calcular la media
        co_mean = statistics.mean(co_values)
        lpg_mean = statistics.mean(lpg_values)
        hydrogen_mean = statistics.mean(hydrogen_values)
        humidity_mean = statistics.mean(humidity_values)
        temperature_mean = statistics.mean(temperature_values)

        # Calcular la mediana
        co_median = statistics.median(co_values)
        lpg_median = statistics.median(lpg_values)
        hydrogen_median = statistics.median(hydrogen_values)
        humidity_median = statistics.median(humidity_values)
        temperature_median = statistics.median(temperature_values)

        # Calcular la moda
        co_mode = statistics.multimode(co_values)
        lpg_mode = statistics.multimode(lpg_values)
        hydrogen_mode = statistics.multimode(hydrogen_values)
        humidity_mode = statistics.multimode(humidity_values)
        temperature_mode = statistics.multimode(temperature_values)

        # Cálculo de la desviación media
        co_deviation_mean = self.mean_deviation(co_values)
        lpg_deviation_mean = self.mean_deviation(lpg_values)
        hydrogen_deviation_mean = self.mean_deviation(hydrogen_values)
        humidity_deviation_mean = self.mean_deviation(humidity_values)
        temperature_deviation_mean = self.mean_deviation(temperature_values)

        # Cálculo de la desviación estándar
        co_standard_deviation = np.std(co_values)
        lpg_standard_deviation = np.std(lpg_values)
        hydrogen_standard_deviation = np.std(hydrogen_values)
        humidity_standard_deviation = np.std(humidity_values)
        temperature_standard_deviation = np.std(temperature_values)

        # Cálculo de la varianza
        co_variance = np.var(co_values)
        lpg_variance = np.var(lpg_values)
        hydrogen_variance = np.var(hydrogen_values)
        humidity_variance = np.var(humidity_values)
        temperature_variance = np.var(temperature_values)

        # Obtener los valores máximos
        co_max = max(measure['co'] for measure in measures)
        lpg_max = max(measure['lpg'] for measure in measures)
        hydrogen_max = max(measure['hydrogen'] for measure in measures)
        humidity_max = max(measure['humidity'] for measure in measures)
        temperature_max = max(measure['temperature'] for measure in measures)

        # Calcular los cuartiles de las fechas
        date_references = np.percentile([date.timestamp() for date in date_values], [1, 25, 50, 75, 100])

        date_references = [datetime.fromtimestamp(timestamp, self.tz_mexico).strftime("%Y-%m-%d %H:%M:%S") for timestamp in date_references]

        # Crear el diccionario de resultados
        co_data = {
            'mean': co_mean,
            'median': co_median,
            'mode': co_mode,
            'max': co_max,
            'deviation_mean': co_deviation_mean,
            'standard_deviation': co_standard_deviation,
            'variance': co_variance,
        }

        lpg_data = {
            'mean': lpg_mean,
            'median': lpg_median,
            'mode': lpg_mode,
            'max': lpg_max,
            'deviation_mean': lpg_deviation_mean,
            'standard_deviation': lpg_standard_deviation,
            'variance': lpg_variance,
        }

        hydrogen_data = {
            'mean': hydrogen_mean,
            'median': hydrogen_median,
            'mode': hydrogen_mode,
            'max': hydrogen_max,
            'deviation_mean': hydrogen_deviation_mean,
            'standard_deviation': hydrogen_standard_deviation,
            'variance': hydrogen_variance,
        }

        humidity_data = {
            'mean': humidity_mean,
            'median': humidity_median,
            'mode': humidity_mode,
            'max': humidity_max,
            'deviation_mean': humidity_deviation_mean,
            'standard_deviation': humidity_standard_deviation,
            'variance': humidity_variance,
        }

        temperature_data = {
            'mean': temperature_mean,
            'median': temperature_median,
            'mode': temperature_mode,
            'max': temperature_max,
            'deviation_mean': temperature_deviation_mean,
            'standard_deviation': temperature_standard_deviation,
            'variance': temperature_variance,
        }
        result = {
            'CO': co_data,
            'LPG': lpg_data,
            'Hydrogen': hydrogen_data,
            'Humidity': humidity_data,
            'Temperature': temperature_data,
            'date_quartiles': date_references,
            'error_sum': error_sum,
            'correct_cases': correct_cases,
            'probable_cases': probable_cases,
        }

        return result

class EmailServiceImpl:

    iServiceDispositive = DispositiveServiceImpl()
    iAdminService = AdminServiceImpl()
    iManagerService = ManagerServiceImpl()

    def send_email(self, request):
        jd = json.loads(request.body)
        subject = 'Alerta'
        from_email = 'selvetkal@gmail.com'
        dispositive = self.iServiceDispositive.find_by_serial_number(jd['serial_number'])
        dispositive_alias = dispositive.alias
        admin_email = self.iAdminService.find_by_id(dispositive.admin.id).email
        managers_email_list = [manager.email for manager in self.iManagerService.find_by_dispositive(dispositive.id)]
        message = jd['message'] + ' en su dispositivo con el alias ' + dispositive_alias
        if len(managers_email_list) > 0:
            recipient_list = [admin_email] + managers_email_list
        else:
            recipient_list = [admin_email]

        send_mail(subject, message, from_email, recipient_list)

        response = {'mails': recipient_list}

        return JsonResponse(response)

