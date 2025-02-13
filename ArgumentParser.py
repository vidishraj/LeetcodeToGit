import argparse
import itertools
import sys


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Process command-line flags for the Python app.")

        # Optional flags
        self.parser.add_argument("--remote", type=str, help="Specifies the remote repo to push to")
        self.parser.add_argument("--localName", type=str, help="Specifies the name of the local repo to be created")
        self.parser.add_argument("--gittoken", type=str, help="Specifies the git token for remote push")
        self.parser.add_argument("--deleteIfFail", action="store_true",
                                 help="If specified with --remote, rolls back local commits on push failure")
        difficulty_choices = ["".join(combo) for i in range(1, 4) for combo in itertools.permutations("ehm", i)]

        # Required flags
        self.parser.add_argument("--difficulty", type=str, choices=difficulty_choices, required=True,
                                 help="Difficulty level: e (Easy), m (Medium), h (Hard)")
        # self.parser.add_argument("--cookie", type=str, required=True, help="Leetcode cookies for API calls")

        self.args = None

    def parse_args(self):
        """Parses command-line arguments and exits if required ones are missing."""
        self.args = self.parser.parse_args()

        # Extra validation: Ensure deleteIfFail is used only with --remote
        if self.args.deleteIfFail and not self.args.remote:
            print("Error: --deleteIfFail must be used with --remote")
            sys.exit(1)

    def get_remote(self):
        return self.args.remote

    def get_local_name(self):
        if not self.args.localName:
            return "Leetcode_History"
        return self.args.localName

    def get_git_token(self):
        return self.args.gittoken

    def get_delete_if_fail(self):
        return self.args.deleteIfFail

    def get_difficulty(self):
        difficultyList = []
        if 'e' in self.args.difficulty:
            difficultyList.append("EASY")
        if 'm' in self.args.difficulty:
            difficultyList.append("MEDIUM")
        if 'h' in self.args.difficulty:
            difficultyList.append("HARD")
        return difficultyList

    def get_cookie(self):
        try:
            with open("leetcode_cookie.txt", "r", encoding="utf-8") as file:
                content = file.read().strip()
                return content if content else None
        except FileNotFoundError:
            return None

