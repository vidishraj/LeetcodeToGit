import subprocess
import os
from logging import Logger


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

    def commit(self, message, description="", body=""):
        """ Commits changes with the given commit message, description, and body. """
        commit_message = f"{message}\n\n{description}\n\n{body}"
        return self.run_git_command(["commit", "-am", commit_message])

    def commit_from_data(self, data):
        """
        Creates a Git commit using the provided dictionary.
        - Creates a file `{titleSlug}.cpp`
        - Writes the provided code inside
        - Stages & commits the file with a formatted commit message
        """
        title_slug = data.get("question", {}).get("titleSlug", "untitled")
        runtime = data.get("runtime", "N/A")
        runtime_percentile = data.get("runtimePercentile", "N/A")
        memory = data.get("memory", "N/A")
        memory_percentile = data.get("memoryPercentile", "N/A")
        code = data.get("code", "")

        if not code:
            return "Error: No code provided to commit."

        # Determine file extension based on language (default to .txt if unknown)
        lang = data.get("lang", {}).get("name", "txt").lower()
        extension = {"cpp": "cpp", "python": "py", "java": "java"}.get(lang, "txt")
        file_name = f"{title_slug}.{extension}"
        file_path = os.path.join(self.repo_path, file_name)

        # Write code to file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(code)

        # Stage the file before committing
        self.run_git_command(["add", file_path])

        # Format commit description
        description = (
            f"Runtime: {runtime} ms ({runtime_percentile} percentile)\n"
            f"Memory: {memory} bytes ({memory_percentile} percentile)"
        )

        return self.commit(title_slug, description, file_path)

