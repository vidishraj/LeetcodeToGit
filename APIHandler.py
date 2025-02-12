import requests


class APIHandler:
    cookies: str

    def __init__(self, cookies):
        self.cookies = cookies

    @staticmethod
    def getSubmissionQuery(submissionId):
        return {
            "query": "\n    query submissionDetails($submissionId: Int!) {\n  submissionDetails(submissionId: "
                     "$submissionId) {\n    runtime\n    runtimeDisplay\n    runtimePercentile\n    "
                     "runtimeDistribution\n    memory\n    memoryDisplay\n    memoryPercentile\n    "
                     "memoryDistribution\n    code\n    timestamp\n    statusCode\n    user {\n      username\n      "
                     "profile {\n        realName\n        userAvatar\n      }\n    }\n    lang {\n      name\n      "
                     "verboseName\n    }\n    question {\n      questionId\n      titleSlug\n      "
                     "hasFrontendPreview\n    }\n    notes\n    flagType\n    topicTags {\n      tagId\n      slug\n  "
                     "    name\n    }\n    runtimeError\n    compileError\n    lastTestcase\n    codeOutput\n    "
                     "expectedOutput\n    totalCorrect\n    totalTestcases\n    fullCodeOutput\n    "
                     "testDescriptions\n    testBodies\n    testInfo\n    stdOutput\n  }\n}\n    ",
            "variables": {
                "submissionId": submissionId
            },
            "operationName": "submissionDetails"
        }

    @staticmethod
    def getProblemListQuery(difficulty, skip=50, limit=50):
        return {
            "query": "\n    query userProgressQuestionList($filters: UserProgressQuestionListInput) {\n  "
                     "userProgressQuestionList(filters: $filters) {\n    totalNum\n    questions {\n      "
                     "translatedTitle\n      frontendId\n      title\n      titleSlug\n      difficulty\n      "
                     "lastSubmittedAt\n      numSubmitted\n      questionStatus\n      lastResult\n      topicTags {"
                     "\n        name\n        nameTranslated\n        slug\n      }\n    }\n  }\n}\n    ",
            "variables": {
                "filters": {
                    "difficulty": difficulty,
                    "questionStatus": "SOLVED",
                    "skip": skip,
                    "limit": limit,
                    "sortOrder": "DESCENDING",
                    "sortField": "LAST_SUBMITTED_AT"
                }
            },
            "operationName": "userProgressQuestionList"
        }

    @staticmethod
    def getQuestionCountQuery(difficulty):
        return {
            "query": "\n    query userProgressQuestionList($filters: UserProgressQuestionListInput) {\n  "
                     "userProgressQuestionList(filters: $filters) {\n    totalNum\n    questions {\n      "
                     "translatedTitle\n      frontendId\n      title\n      titleSlug\n      difficulty\n      "
                     "lastSubmittedAt\n      numSubmitted\n      questionStatus\n      lastResult\n      topicTags {"
                     "\n        name\n        nameTranslated\n        slug\n      }\n    }\n  }\n}\n    ",
            "variables": {
                "filters": {
                    "difficulty": difficulty,
                    "questionStatus": "SOLVED",
                    "skip": 0,
                    "limit": 0,
                    "sortOrder": "DESCENDING",
                    "sortField": "LAST_SUBMITTED_AT"
                }
            },
            "operationName": "userProgressQuestionList"
        }

    @staticmethod
    def getSubmissionListQuery(questionSlug, offset):
        return {
            "query": "\n    query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: "
                     "String!, $lang: Int, $status: Int) {\n  questionSubmissionList(\n    offset: $offset\n    "
                     "limit: $limit\n    lastKey: $lastKey\n    questionSlug: $questionSlug\n    lang: $lang\n    "
                     "status: $status\n  ) {\n    lastKey\n    hasNext\n    submissions {\n      id\n      title\n    "
                     "  titleSlug\n      status\n      statusDisplay\n      lang\n      langName\n      runtime\n     "
                     " timestamp\n      url\n      isPending\n      memory\n      hasNotes\n      notes\n      "
                     "flagType\n      frontendId\n      topicTags {\n        id\n      }\n    }\n  }\n}\n    ",
            "variables": {
                "questionSlug": questionSlug,
                "offset": offset,
                "limit": 20,
            },
            "operationName": "submissionList"
        }

    def makeRequest(self, query):
        APIUrl = "https://leetcode.com/graphql/"
        headers = {
            "Cookie": self.cookies,
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/132.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "host": "leetcode.com"
        }

        response = requests.post(APIUrl, json=query, headers=headers)
        return response
