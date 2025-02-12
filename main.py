import os

from GitHandler import GitHandler
from LeetCodeHandler import Leetcode
from APIHandler import APIHandler
from logger import Logger


class ApplicationRunner:
    leetCodeHandler: Leetcode
    apiHandler: APIHandler
    gitHandler: GitHandler
    logger: Logger.__class__

    def __init__(self, cookies, remoteUrl):
        self.apiHandler = APIHandler(cookies)
        self.leetCodeHandler = Leetcode(self.apiHandler)
        self.gitHandler = GitHandler(repo_path=os.path.join(os.pardir + "/Leetcode_History"))
        self.gitHandler.add_remote(remoteUrl)
        self.logger = Logger("APP").get_logger()

    def processProblems(self):

        problemList: list = self.leetCodeHandler.getAllSolvedProblems(['HARD'])
        questions = 0
        for problem in problemList:
            question = problem['titleSlug']
            self.logger.info(f"Fetching best submission for {question}")
            submissionId = self.leetCodeHandler.getSubmissionListForQuestion(question)
            self.logger.info(f"Best submission fetched {question}")
            submissionData = self.leetCodeHandler.getSubmission(submissionId)
            self.logger.info("Code for submission fetched. Starting commit to local.")
            gitOutput = self.gitHandler.commit_from_data(submissionData)
            questions += 1
            if gitOutput.startswith("Error") and not gitOutput.startswith("Error: warning:"):
                if gitOutput.endswith("404"):
                    self.logger.warning(f"{question} already exists. Continuing")
                    questions -= 1
                elif gitOutput.endswith("401"):
                    self.logger.warning(f"{question} is an invalid slug. Continuing")
                else:
                    self.logger.error("Error while pushing submission to local git repo.")
                    exit(0)
            self.logger.info(f"Local commit process done for {question}")
        self.logger.info(f"Pushing {questions} questions to remote")
        gitOutput = self.gitHandler.push("origin", "master")
        if not gitOutput.startswith("Error"):
            self.logger.info("Process completed!")
        else:
            self.logger.error(f"Some errors occurred while pushing to remote.\n Error: {gitOutput}")


if __name__ == '__main__':
    cookies = ''
    remoteURL = ""
    al = ApplicationRunner(cookies, remoteURL)
    al.processProblems()
