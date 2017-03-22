# -*- coding: utf-8 -*-

class AelfHttpError(Exception):
    def __init__(self, status, message=None):
        super(AelfHttpError, self).__init__(message)
        self.status = status

