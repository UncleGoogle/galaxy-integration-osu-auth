class HttpError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        if status_code is not None:
            self.status_code = status_code
        self.payload = {'message': message}

    def to_dict(self):
        return self.payload
