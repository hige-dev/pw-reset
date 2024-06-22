import os


# https://blog.father.gedow.net/2021/01/21/aws-api-gateway-http-authorizer/
class ApiGatewayV2Authorization():

    event = None

    def __init__(self, event=None):
        if event is not None:
            self.setEvent(event)

    def setEvent(self, event):
        if self.event is not None:
            return
        self.event = event

    def authorizer(self):
        AUTH_KEY   = os.environ['AUTH_KEY']   if os.environ.get('AUTH_KEY')   else "Authorization"
        AUTH_VALUE = os.environ['AUTH_VALUE'] if os.environ.get('AUTH_VALUE') else None

        auth_type = self.event.get("type")
        if auth_type != "REQUEST":
            return None

        header_key   = AUTH_KEY.lower()
        header_value = self.event["headers"].get(header_key)
        if AUTH_VALUE is None or header_value is None:
            return self.responseUnauthorized()

        if AUTH_VALUE != header_value:
            return self.responseUnauthorized()

        return self.responseAuthorized()

    def responseAuthorized(self):
        res = {
            "isAuthorized": True,
            "context": {},
        }
        return res

    def responseUnauthorized(self):
        res = {
            "isAuthorized": False,
            "context": {},
        }
        return res
