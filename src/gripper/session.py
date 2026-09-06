import requests


class GripperSession(requests.Session):
    def rget(self, *args, **kwargs):
        rsp = self.get(*args, **kwargs)
        rsp.raise_for_status()
        return rsp
