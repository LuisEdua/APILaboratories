from datetime import timedelta, datetime
from typing import Any
import bcrypt
from pytz import timezone
from .interfaces import IMeasuresService, ISessionService, IUserService, IDispositiveService
from .models import Measures, Admin, Manager, Dispositive
from django.http.response import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
import json
from django.core.mail import send_mail


def base_response(message, response) -> JsonResponse:
    if response:
        data = {'message': message, 'data': response, 'status': True}
    else:
        data = {'message': message, 'status': False}
    return JsonResponse(data)


class AdminServiceImpl(IUserService):

    def validate(self, request) -> JsonResponse:
        js = json.loads(request.body)
        try:
            admin = self._login_(js)
            if check_password(js['password'], admin.password):
                response = self.__admin_response__(admin, js)
                message = "Login successfully"
            else:
                response = 0
                message = "Invalid password"
        except Exception:
            response = 0
            message = "Invalid email"
        return base_response(message, response)

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
            else:
                response = 0
                message = "Invalid password"
        except Exception:
            response = 0
            message = "Invalid email"
        return base_response(message, response)

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

    def list(self, id) -> JsonResponse:
        current_date = datetime.now(timezone('UTC'))
        one_year_ago = current_date - timedelta(days=365)
        measures = Measures.objects.filter(dispositive_id=id, date__gte=one_year_ago).all()
        if len(measures) > 0:
            response = list(map(self.__measure_response__, measures))
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
                                       serial_number_esp32=jd['serial_number_esp32'], dispositive=dispositive)


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

