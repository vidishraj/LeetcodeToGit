import logging
from collections import defaultdict

from APIHandler import APIHandler


class Leetcode:
    def __init__(self, apiHandler: APIHandler):
        self.Logger = logging.getLogger("LEETCODE")
        self.apiHandler = apiHandler

    def convert_to_defaultdict(self, d):
        """Recursively converts all dictionaries in a nested structure to defaultdict."""
        if isinstance(d, dict):
            return defaultdict(lambda: None, {k: self.convert_to_defaultdict(v) for k, v in d.items()})
        return d

    def getAllSolvedProblems(self, difficulty=None):
        if difficulty is None:
            difficulty = ['HARD', 'MEDIUM', 'EASY']

        countQuery = self.apiHandler.getQuestionCountQuery(difficulty)
        countResponse = self.apiHandler.makeRequest(countQuery)

        if countResponse.status_code != 200:
            self.Logger.error(f"Error from Leetcode while fetching problem count. Check cookies or internet! \n"
                              f"Status Code: {countResponse.status_code}")
            return None  # Explicitly return None
        jsonResponse = countResponse.json()
        # We want to fetch all the questions at once
        dfDict = self.convert_to_defaultdict(jsonResponse)
        limit = dfDict['data']['userProgressQuestionList']['totalNum']
        if limit is None or limit == 0:
            logging.error("No questions available to fetch. Are your filters okay?")
            return
        limit += 1
        skip = 0
        problemsQuery = self.apiHandler.getProblemListQuery(difficulty, skip, limit)
        problemListResponse = self.apiHandler.makeRequest(problemsQuery)  # Assuming this returns the problem list
        if problemListResponse.status_code != 200:
            self.Logger.error(f"Error from Leetcode while fetching problem list. Check cookies or internet! \n"
                              f"Status Code: {problemListResponse.status_code}")
            return None  # Explicitly return None
        jsonResponse = problemListResponse.json()
        problemListResponseDict = self.convert_to_defaultdict(jsonResponse)
        return problemListResponseDict
