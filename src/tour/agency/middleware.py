from time import time

from django.utils.deprecation import MiddlewareMixin


class StatsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        self.start_time = time()

    def process_response(self, request, response):
        time_taken = time() - self.start_time
        response['X-Total-time'] = round(time_taken,5)
        print(response['X-Total-time'])
        return response
