from LeetCodeHandler import Leetcode
from APIHandler import APIHandler


class ApplicationRunner:
    leetCodeHandler: Leetcode
    apiHandler: APIHandler

    def __init__(self, cookies):
        self.apiHandler = APIHandler(cookies)
        self.leetCodeHandler = Leetcode(self.apiHandler)

    def getProblemList(self):
        return self.leetCodeHandler.getAllSolvedProblems()


if __name__ == '__main__':
    cookies = "ENTER COOKIES HERE"
    ApplicationRunner()
