import os

from ArgumentParser import ArgumentParser
from GitHandler import GitHandler
from LeetCodeHandler import Leetcode
from APIHandler import APIHandler
from logger import Logger


class ApplicationRunner:
    leetCodeHandler: Leetcode
    apiHandler: APIHandler
    gitHandler: GitHandler
    argParser: ArgumentParser
    logger: Logger.__class__

    def __init__(self, argParser: ArgumentParser):
        self.argParser = argParser
        self.apiHandler = APIHandler()
        self.leetCodeHandler = Leetcode(self.apiHandler)
        self.gitHandler = GitHandler()
        self.logger = Logger("APP").get_logger()

    def startFirstStage(self):
        """
        In the first stage
         a)    Init local git repo
         b)    Add remote url.
         c)    Check connection to Leetcode
         d)    Checking ability to push to remote
        :return: void
        """
        try:
            self.logger.info("---Starting Stage 1------")
            self.logger.info("Creating local git repo to track changes")
            # Init local repo
            localRepoPath = os.path.join(os.pardir + f"/{self.argParser.get_local_name()}")
            self.gitHandler.init_local_repo(localRepoPath)

            # Add remote url
            self.logger.info("Adding remote url info")
            remote = self.argParser.get_remote()

            if remote is None:
                self.logger.warning("No remote flag. Remote operation are disabled.")
                self.gitHandler.pushToRemote = False
            else:
                self.gitHandler.setRemote(remote)
                self.gitHandler.add_remote(remote)
                self.logger.info("Remote url added successfully.")

            # Check connection to Leetcode
            self.logger.info("Checking connection to Leetcode")
            cookies = self.argParser.get_cookie()
            if cookies is None:
                self.logger.error("Cookies not initialised properly in text file. Add it.")
                return
            self.apiHandler.setCookies(cookies)
            if not self.leetCodeHandler.checkLeetcodeConnectionStatus():
                self.logger.error("Error with leetcode connection. Either cookies are invalid"
                                  "or you have no questions solved")
                exit(0)

            self.logger.info("Leetcode connections successful")

            # Check ability to push to remote
            if remote is None or not self.gitHandler.can_push_to_git():
                self.logger.warning("Can not push to remote. Non fatal error. Continuing")

        except Exception as ex:
            self.logger.info("---Unexpected Error during Stage 1------")
            self.logger.info(f"{ex}")
            exit(0)
        finally:
            self.logger.info("---Stage 1 ended------")

    def startSecondStage(self):
        """
        In the second stage
                -1)    Define progress bar based on questions count.
                 a)    Find all solved questions
                 b)    Find submission list for all questions
                 c)    Find submission ID for all questions.
                :return: list of dicts with submissions ID's with their title and slug
        """

        self.logger.info("---Starting Stage 2------")
        try:
            difficulty = self.argParser.get_difficulty()
            # Get all problems. Error is fatal here.
            self.logger.info("Fetching all solved problems")
            problemList: list = self.leetCodeHandler.getAllSolvedProblems(difficulty)
            self.logger.info("Finished fetching all solved problems")
            questionCount = len(problemList)
            failures = 0
            submissionIds = []
            for problem in problemList:
                questionSlug = problem['titleSlug']
                try:
                    if self.gitHandler.checkIfSolutionExists(questionSlug):
                        self.logger.warning(f"Solution already exists for {questionSlug}")
                    else:
                        self.logger.info(f"Fetching best submission for {questionSlug}")
                        submissionId, submissionTitle = self.leetCodeHandler.getSubmissionListForQuestion(questionSlug)
                        submissionIds.append({questionSlug: [submissionId, submissionTitle, problem['difficulty']]})
                        self.logger.info(f"Best submission fetched for {questionSlug}")
                except RuntimeWarning as rm:
                    # Failed to fetch submission for one
                    self.logger.warning(f"{rm.__str__()}")
                    failures += 1
            self.logger.info(f"Finished fetching all submissions. {questionCount - failures}/{questionCount}"
                             f" success, {failures}/{questionCount} failures")
            return submissionIds
        except Exception as ex:
            self.logger.info("---Unexpected Error during Stage 2------")
            self.logger.info(f"{ex}")
            exit(0)
        finally:
            self.logger.info("---Stage 2 ended------")

    def startThirdStage(self, submissionIds):
        """
        In the second stage
        -1)    Define progress bar based on questions count.
         a)    Finds code for the submission Ids
         b)    Push the code to the local repo
        :param submissionIds: returned list from stage 2
        :return: local commit hashes
        """

        self.logger.info("---Starting Stage 3------")
        questions = 0
        commitHashes = []
        try:
            for questionSlug in submissionIds:
                key = list(questionSlug.keys())[0]
                submissionId = questionSlug[key][0]
                submissionTitle = questionSlug[key][1]
                questionDifficulty = questionSlug[key][2]
                try:
                    questions += 1
                    submissionData = self.leetCodeHandler.getSubmission(submissionId)
                    self.logger.info("Code for submission fetched. Starting commit to local.")
                    gitOutput = self.gitHandler.commit_from_data(submissionData, questionDifficulty, submissionTitle)

                    if gitOutput.startswith("Error") and not gitOutput.startswith("Error: warning:"):
                        if gitOutput.endswith("404"):
                            self.logger.warning(f"{questionSlug} already exists. Continuing")
                            questions -= 1
                        elif gitOutput.endswith("401"):
                            self.logger.warning(f"{questionSlug} is an invalid slug. Continuing")
                        else:
                            self.logger.error("Error while pushing submission to local git repo.")
                            questions -= 1
                    else:
                        # Commit hash
                        commitHashes.append(gitOutput)
                    self.logger.info(f"Local commit process done for {questionSlug}")
                except RuntimeWarning as rm:
                    questions -= 1
                    self.logger.warning(f"Failure fetching solution during {questionSlug}")
            return commitHashes
        except Exception as ex:
            self.logger.info("---Unexpected Error during Stage 3------")
            self.logger.info(f"{ex}")
            exit(0)
        finally:
            self.logger.info("Adding summary to read me")
            try:
                self.gitHandler.addSummaryToReadMe()
            except Exception as ex:
                self.logger.warning(f"Some issue occurred while updating git summary. {ex}")
            self.logger.info(f"Ending stage 3 with {questions} submissions processed")
            self.logger.info("---Stage 3 ended------")

    def startFourthStage(self, commitHashes):
        """
        In this method we only deal with remote pushes from our local repo.
        :return: void
        """
        self.logger.info("---Starting Stage 4------")
        if not self.gitHandler.pushToRemote:
            self.logger.error("Remote pushes are disabled by flag or ability to push. Try with "
                              "token")
            return
        localSameAsRemote = self.gitHandler.is_local_up_to_date()
        if len(commitHashes) == 0 and localSameAsRemote:
            self.logger.warning("Nothing to push to remote")
            return
        if len(commitHashes) > 0:
            self.logger.info(f"Pushing {len(commitHashes)} commits to remote.")
        try:
            gitOutput = self.gitHandler.push()
            if not gitOutput.startswith("Error"):
                self.logger.info("Pushing process completed!")
            else:
                self.logger.error(f"Some errors occurred while pushing to remote.\n Error: {gitOutput}")
                if arg_parser.get_delete_if_fail() and len(commitHashes) > 0:
                    self.gitHandler.revert_commits(commitHashes)
        except Exception as ex:
            self.logger.error("Error while pushing to remote.")
            if arg_parser.get_delete_if_fail() and len(commitHashes) > 0:
                self.gitHandler.revert_commits(commitHashes)
        self.logger.info("---Stage 4 ended------")


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.parse_args()

    al = ApplicationRunner(arg_parser)
    al.startFirstStage()
    submissionIds = al.startSecondStage()
    commitHashes = al.startThirdStage(submissionIds)
    al.startFourthStage(commitHashes)
