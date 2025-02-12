from logging import Logger

from APIHandler import APIHandler


class Leetcode:
    Logger: Logger
    apiHandler: APIHandler

    def __new__(cls, *args, **kwargs):
        cls.Logger = Logger.manager.getLogger("LEETCODE")
        return cls

    def __init__(self, apiHandler: APIHandler):
        self.apiHandler = apiHandler

    def getAllSolvedProblems(self):
        return
