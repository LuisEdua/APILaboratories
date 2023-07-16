from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .implements import MeasuresServiceImpl, SessionServiceImpl, \
    AdminServiceImpl, DispositiveServiceImpl, ManagerServiceImpl, EmailServiceImpl


# Create your views here.
class MeasuresView(View):
    iServiceMeasure = MeasuresServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id):
        return self.iServiceMeasure.list(id)

    def post(self, request):
        return self.iServiceMeasure.create(request)



class EmailView(View):
    emailService = EmailServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        self.emailService.send_email(request)


class AdminsView(View):
    iServiceAdmin = AdminServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        return self.iServiceAdmin.create(request)

    def put(self, request, id):
        return  self.iServiceAdmin.update(request, id)

    def delete(self, request, id):
        return self.iServiceAdmin.delete(id)


class ManagerView(View):
    iServiceManager = ManagerServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id):
        return self.iServiceManager.list(id)

    def post(self, request, id):
        return self.iServiceManager.create(request, id)

    def put(self, request, id):
        return self.iServiceManager.update(request, id)

    def delete(self, request, id):
        return self.iServiceManager.delete(id)


class DispositiveView(View):
    iServiceDispositive = DispositiveServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id):
        return self.iServiceDispositive.list(id)

    def put(self, request):
        return self.iServiceDispositive.update(request)

    def delete(self, request, id):
        return self.iServiceDispositive.delete(id)


class SessionView(View):
    iServiceSession = SessionServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        return self.iServiceSession.validate(request)