from logger import Logger
from collections import defaultdict

from APIHandler import APIHandler


class Leetcode:
    def __init__(self, apiHandler: APIHandler):
        self.logger = Logger("LEETCODE").get_logger()
        self.apiHandler = apiHandler

    def convert_to_defaultdict(self, d):
        """Recursively converts all dictionaries in a nested structure to defaultdict."""
        if isinstance(d, dict):
            return defaultdict(lambda: None, {k: self.convert_to_defaultdict(v) for k, v in d.items()})
        return d

    def checkLeetcodeConnectionStatus(self):
        difficulty = ['HARD', 'MEDIUM', 'EASY']

        countQuery = self.apiHandler.getQuestionCountQuery(difficulty)
        countResponse = self.apiHandler.makeRequest(countQuery)

        if countResponse.status_code != 200:
            return False
        jsonResponse = countResponse.json()
        # We want to fetch all the questions at once
        dfDict = self.convert_to_defaultdict(jsonResponse)
        limit = dfDict['data']['userProgressQuestionList']['totalNum']
        if limit is None or limit == 0:
            return False
        return True

    def getAllSolvedProblems(self, difficulty=None):
        if difficulty is None:
            difficulty = ['HARD', 'MEDIUM', 'EASY']

        countQuery = self.apiHandler.getQuestionCountQuery(difficulty)
        countResponse = self.apiHandler.makeRequest(countQuery)

        if countResponse.status_code != 200:
            self.logger.error(f"Error from Leetcode while fetching problem count. Check cookies or internet! \n"
                              f"Status Code: {countResponse.status_code}")
            exit(0)  # Explicitly return None
        jsonResponse = countResponse.json()
        # We want to fetch all the questions at once
        dfDict = self.convert_to_defaultdict(jsonResponse)
        limit = dfDict['data']['userProgressQuestionList']['totalNum']
        if limit is None or limit == 0:
            self.logger.error("No questions available to fetch. Are your filters okay?")
            exit(0)
        limit += 1
        skip = 0
        problemsQuery = self.apiHandler.getProblemListQuery(difficulty, skip, limit)
        problemListResponse = self.apiHandler.makeRequest(problemsQuery)  # Assuming this returns the problem list
        if problemListResponse.status_code != 200:
            self.logger.error(f"Error from Leetcode while fetching problem list. Check cookies or internet! \n"
                              f"Status Code: {problemListResponse.status_code}")
            exit(0)  # Explicitly return None
        jsonResponse = problemListResponse.json()
        problemListResponseDict = self.convert_to_defaultdict(jsonResponse)
        questionList = problemListResponseDict['data']['userProgressQuestionList']['questions']
        if questionList is None:
            self.logger.error("Error fetching final question list. Response status was okay. Is response mangled?")
            exit(0)
        return questionList

    def getSubmissionListForQuestion(self, questionSlug):
        startOffset = 0

        def checkSubmissionResponse(response):
            if response.status_code != 200:
                self.logger.error(f"Error from Leetcode while fetching submission list. Check cookies or internet or "
                                  f"question slug! \n"
                                  f"Status Code: {response.status_code}")
                raise RuntimeWarning(f"Error while fetching Submissions for {questionSlug}")
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
                self.logger.error("Submission List response is mangled.")
                raise RuntimeWarning(f"Error while fetching Submissions for {questionSlug}")
            for submission in submissions:
                submission = self.convert_to_defaultdict(submission)
                if submission['status'] == 10:
                    self.logger.info(f"Submission found for question {submission['title']}")
                    return submission['id'], submission['title']
            if not hasNext:
                break
            # Make next request
            startOffset += 20
            submissionListQuery = self.apiHandler.getSubmissionListQuery(questionSlug, startOffset)
            submissionListResponse = self.apiHandler.makeRequest(submissionListQuery)
        self.logger.error(f"Could not find a submission for question slug {questionSlug}")
        raise RuntimeWarning(f"Error while fetching Submissions for {questionSlug}")

    def getSubmission(self, submissionId):
        submissionQuery = self.apiHandler.getSubmissionQuery(submissionId)
        submissionResponse = self.apiHandler.makeRequest(submissionQuery)
        if submissionResponse.status_code != 200:
            self.logger.error(f"Error from Leetcode while fetching submission. Check cookies or internet or "
                              f"question slug! \n"
                              f"Status Code: {submissionResponse.status_code}")

            raise RuntimeWarning(f"Error while fetching Submissions for {submissionId}")
        submissionJson = submissionResponse.json()
        submissionDict = self.convert_to_defaultdict(submissionJson)
        submission = submissionDict['data']['submissionDetails']
        if submission is None:
            self.logger.error("Error from Leetcode while fetching submission. Data seems to be mangled")
            raise RuntimeWarning(f"Error while fetching Submissions for {submissionId}")
        return submission
