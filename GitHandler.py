import subprocess
import os


class GitHandler:
    Logger: Logger

    def __init__(self, repo_path="."):
        """
        Initialize the GitHandler with a repository path.
        If the path is not a Git repository, it initializes one.
        """
        self.repo_path = os.path.abspath(repo_path)
        os.makedirs(self.repo_path, exist_ok=True)
        self.Logger = Logger.manager.getLogger("GIT")
        if not self.is_git_repo():
            self.Logger.warning("No Git repository found. Initializing a new one...")
            self.init_repo()

    def run_git_command(self, command):
        """
        Runs a git command using subprocess and returns the output.
        Handles cases where Git commands succeed but still return a non-zero exit code.
        """
        result = subprocess.run(
            ["git"] + command, cwd=self.repo_path, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.returncode == 0:
            return result.stdout.strip()  # Success case

        # Handle specific non-fatal errors
        if "nothing to commit" in result.stderr.lower():
            return "Nothing to commit, working tree clean."

        return f"Error: {result.stderr.strip()}"

    def is_git_repo(self):
        """
        Checks if the directory is a Git repository.
        """
        return os.path.exists(os.path.join(self.repo_path, ".git"))

    def init_repo(self):
        """
        Initializes a new Git repository in the specified directory
        and enables auto-tracking of all files.
        """
        self.run_git_command(["init"])
        self.run_git_command(["config", "core.autocrlf", "true"])  # Ensures cross-platform consistency
        self.run_git_command(["add", "-A"])  # Auto-tracks all existing and new files
        return "Initialized Git repository and enabled auto-tracking of all files."

    def push(self, remote="origin", branch="main"):
        """ Pushes the current branch to the specified remote. """
        return self.run_git_command(["push", remote, branch])

    def pull(self, remote="origin", branch="main"):
        """ Pulls the latest changes from the specified remote and branch. """
        return self.run_git_command(["pull", remote, branch])

    def checkout(self, branch_name):
        """ Switches to the specified branch. """
        return self.run_git_command(["checkout", branch_name])

    def commit(self, message):
        """ Commits changes with the given commit message. """
        return self.run_git_command(["commit", "-am", message])


