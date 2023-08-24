import time

from django.http import HttpRequest
from django.shortcuts import render


def set_useragent_on_request_middleware(get_response):

    print("initial call")
    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("after get response")
        return response

    return middleware

class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.request_visitors = {}
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        time_delay = 0.5
        visitor_ip = request.META.get('REMOTE_ADDR')

        if visitor_ip not in self.request_visitors:
            self.request_visitors[visitor_ip] = round(time.time() * 1)
        else:
            if round(time.time() * 1) - self.request_visitors[visitor_ip] < time_delay \
                    and request.META.get('REMOTE_ADDR') in self.request_visitors:
                print('Request times are too frequent. Repeat after 1 second!')
                return render(request, 'requestdataapp/error-request.html')

        self.request_visitors[visitor_ip] = round(time.time() * 1)

        self.requests_count += 1
        print("requests count", self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print("responses count", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")