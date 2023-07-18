from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .implements import MeasuresServiceImpl, SessionServiceImpl, \
    AdminServiceImpl, DispositiveServiceImpl, ManagerServiceImpl, EmailServiceImpl
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView


# Create your views here.
class MeasuresView(APIView):
    throttle_classes = [UserRateThrottle]
    iServiceMeasure = MeasuresServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        return self.iServiceMeasure.create(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def measure_list(request, id):
    return MeasuresView.iServiceMeasure.list(request, id)


class EmailView(APIView):
    throttle_classes = [UserRateThrottle]
    emailService = EmailServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        return self.emailService.send_email(request)


class AdminsView(APIView):
    throttle_classes = [UserRateThrottle]
    iServiceAdmin = AdminServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        return self.iServiceAdmin.create(request)

    def put(self, request, id):
        return self.iServiceAdmin.update(request, id)

    def delete(self, request, id):
        return self.iServiceAdmin.delete(id)


class ManagerView(APIView):
    throttle_classes = [UserRateThrottle]
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


class DispositiveView(APIView):
    throttle_classes = [UserRateThrottle]
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


class SessionView(APIView):
    throttle_classes = [UserRateThrottle]
    iServiceSession = SessionServiceImpl()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @api_view(['POST'])
    def post(self, request):
        return self.iServiceSession.validate(request)
