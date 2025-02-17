# model_1/middleware.py

import uuid

class CustomSessionCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only set the session cookie if the session key is available
        if request.session.session_key:
            # Use the session key to generate a unique session cookie name
            custom_cookie_name = 'sessionid_{}'.format(request.session.session_key)
            response.set_cookie(custom_cookie_name, request.session.session_key)

        return response
