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
            exit(0)  # Explicitly return None
        jsonResponse = countResponse.json()
        # We want to fetch all the questions at once
        dfDict = self.convert_to_defaultdict(jsonResponse)
        limit = dfDict['data']['userProgressQuestionList']['totalNum']
        if limit is None or limit == 0:
            logging.error("No questions available to fetch. Are your filters okay?")
            exit(0)
        limit += 1
        skip = 0
        problemsQuery = self.apiHandler.getProblemListQuery(difficulty, skip, limit)
        problemListResponse = self.apiHandler.makeRequest(problemsQuery)  # Assuming this returns the problem list
        if problemListResponse.status_code != 200:
            self.Logger.error(f"Error from Leetcode while fetching problem list. Check cookies or internet! \n"
                              f"Status Code: {problemListResponse.status_code}")
            exit(0)  # Explicitly return None
        jsonResponse = problemListResponse.json()
        problemListResponseDict = self.convert_to_defaultdict(jsonResponse)
        questionList = problemListResponseDict['data']['userProgressQuestionList']['questions']
        if questionList is None:
            self.Logger.error("Error fetching final question list. Response status was okay. Is response mangled?")
            exit(0)
        return questionList

    def submissionListForQuestion(self, questionSlug):
        startOffset = 0

        def checkSubmissionResponse(response):
            if response.status_code != 200:
                self.Logger.error(f"Error from Leetcode while fetching submission list. Check cookies or internet or "
                                  f"question slug! \n"
                                  f"Status Code: {response.status_code}")
                exit(0)
            return True

        submissionListQuery = self.apiHandler.getSubmissionListQuery(questionSlug, startOffset)
        submissionListResponse = self.apiHandler.makeRequest(submissionListQuery)
        if not checkSubmissionResponse(submissionListResponse): return
        submissionResponseJson = submissionListResponse.json()
        submissionResponseDict = self.convert_to_defaultdict(submissionResponseJson)
        while checkSubmissionResponse(submissionListResponse):
            hasNext = submissionResponseDict['data']['questionSubmissionList']['hasNext']
            submissions = submissionResponseDict['data']['questionSubmissionList']['submissions']
            if hasNext is None or submissions is None:
                self.Logger.error("Submission List response is mangled.")
                exit(0)
            for submission in submissions:
                submission = self.convert_to_defaultdict(submission)
                if submission['status'] == 10:
                    self.Logger.info(f"Submission found for question {submission}")
                    return submission['id']
            if not hasNext:
                break
            # Make next request
            startOffset += 20
            submissionListQuery = self.apiHandler.getSubmissionListQuery(questionSlug, startOffset)
            submissionListResponse = self.apiHandler.makeRequest(submissionListQuery)
        self.Logger.error(f"Could not find a submission for question slug {questionSlug}")
