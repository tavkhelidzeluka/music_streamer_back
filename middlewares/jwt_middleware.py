class JWTAuthCookieMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return response
