import subprocess
import os
from decimal import Decimal, ROUND_DOWN

from logger import Logger
from logging import Logger as LG
import pandas as pd


class GitHandler:
    logger: LG
    gitToken: str = None
    remote: str
    pushToRemote: bool

    def __init__(self, token=None):
        if token is not None:
            self.gitToken = token

    def setRemote(self, remoteUrl):
        self.remote = remoteUrl

    def setToken(self, token):
        self.gitToken = token

    def init_local_repo(self, repoPath):
        """
        If the path is not a Git repository, it initializes one with a README.
        """
        self.repo_path = os.path.abspath(repoPath)
        os.makedirs(self.repo_path, exist_ok=True)
        self.logger = Logger("GIT").get_logger()

        if not self.is_git_repo():
            self.logger.warning("No Git repository found. Initializing a new one with README...")
            self.init_repo()
        else:
            self.logger.info("Repository exists in local.")

        # Ensure README exists
        self.ensure_readme()

    def run_git_command(self, command):
        """ Runs a git command using subprocess and returns the output. """
        result = subprocess.run(
            ["git"] + command, cwd=self.repo_path, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.returncode == 0:
            return result.stdout.strip()  # Success case

        if "nothing to commit" in result.stderr.lower():
            return "Nothing to commit, working tree clean."
        if self.gitToken is not None and any(err in result.stderr.lower() for err in
                                             ["authentication failed", "fatal: unable to access",
                                              "could not read from remote repository"]):
            # Modify the command to use gitToken for authentication
            self.logger.warning("Remote operation failed. Using the provided git token instead.")
            if "push" in command or "fetch" in command or "pull" in command:
                remote_url = self.run_git_command(["config", "--get", "remote.origin.url"])
                if remote_url.startswith("https://"):
                    # Inject gitToken into the remote URL
                    tokenized_url = remote_url.replace("https://", f"https://{self.gitToken}@")
                    return self.run_git_command(["remote", "set-url", "origin", tokenized_url])
        return f"Error: {result.stderr.strip()}"

    def is_git_repo(self):
        """ Checks if the directory is a Git repository. """
        return os.path.exists(os.path.join(self.repo_path, ".git"))

    def init_repo(self):
        """ Initializes a new Git repository and creates a README file. """
        self.run_git_command(["init"])
        self.run_git_command(["config", "core.autocrlf", "true"])
        self.ensure_readme()
        self.run_git_command(["add", "README.md"])
        self.commit("Initial commit", "Created repository with README.")
        self.run_git_command(["push", "-u", "origin", "main"])  # Push the initial commit (optional)

    def ensure_readme(self):
        """ Ensures a README.md file exists. If not, create an attractive one. """
        readme_path = os.path.join(self.repo_path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as readme:
                readme.write("# 🚀 LeetCode Submissions\n")
                readme.write("### Track your progress with performance insights!\n\n")
                readme.write("| Problem | Runtime Percentile | Memory Percentile | Difficulty |\n")
                readme.write("|---------|-------------------|-------------------|-------------------|\n")
            self.run_git_command(["add", "README.md"])
            self.commit("Added README.md", "Initialized the repository with a README file.")

    def commit(self, message, description="", body=""):
        """ Commits changes with a given commit message, description, and body. """
        commit_message = f"{message}\n\n{description}\n\n{body}"
        commit_result = self.run_git_command(["commit", "-am", commit_message])
        if "Error" in commit_result:
            raise RuntimeWarning(f"Commit failed to local with result {commit_result}")  # Raise warning on failure

            # Get the latest commit hash
        commit_hash = self.run_git_command(["rev-parse", "HEAD"])
        return commit_hash

    def commit_from_data(self, data, difficulty, title):
        """
        Creates a Git commit using the provided dictionary.
        - Creates a file `{titleSlug}.cpp`
        - Writes the provided code inside
        - Stages & commits the file with a formatted commit message
        - Updates README.md with performance details
        """
        title_slug = data.get("question", {}).get("titleSlug", "untitled")
        runtime = data.get("runtime", "N/A")
        runtime_percentile = data.get("runtimePercentile", "N/A")
        memory = data.get("memory", "N/A")
        memory_percentile = data.get("memoryPercentile", "N/A")
        code = data.get("code", "")

        if not code:
            return "Error: No code provided to commit.401"

        # Determine file extension based on language
        lang = data.get("lang", {}).get("name", "txt").lower()
        extension = {"cpp": "cpp", "python": "py", "python3": "py", "java": "java"}.get(lang, "txt")
        file_name = f"{title_slug}.{extension}"
        file_path = os.path.join(self.repo_path, file_name)

        # Check if file already exists
        if os.path.exists(file_path):
            return f"Error: File '{file_name}' already exists. No new commit made. 404"

        # Write code to file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(code)

        # Stage the file
        self.run_git_command(["add", file_path])

        # Format commit description
        description = (
            f"Runtime: {runtime} ms ({runtime_percentile} percentile)\n"
            f"Memory: {memory} bytes ({memory_percentile} percentile)"
        )

        # Commit the new file
        commit_hash = self.commit(title_slug, description, file_path)

        # Update README.md
        self.update_readme(title, runtime_percentile, memory_percentile, difficulty)

        return commit_hash

    def update_readme(self, title_slug, runtime_percentile, memory_percentile, difficulty):
        """ Adds a new row to README.md with submission details. """
        readme_path = os.path.join(self.repo_path, "README.md")
        try:
            new_line = f"| {title_slug} | {Decimal(runtime_percentile).quantize(Decimal('.01'), ROUND_DOWN)}% | {Decimal(memory_percentile).quantize(Decimal('.01'), ROUND_DOWN)}% | {difficulty} |\n"
        except:
            new_line = f"| {title_slug} | {runtime_percentile}% | {memory_percentile}% | {difficulty} |\n"

        with open(readme_path, "a", encoding="utf-8") as readme:
            readme.write(new_line)

        self.run_git_command(["add", "README.md"])
        self.commit("Updated README", f"Added new entry: {title_slug}")

    def add_remote(self, remote_url, remote_name="origin"):
        """
        Adds a remote URL to the repository.
        If the remote already exists, it updates the remote URL instead of adding a duplicate.
        """
        existing_remotes = self.run_git_command(["remote", "-v"])

        if remote_name in existing_remotes:
            self.logger.warning(f"Remote '{remote_name}' already exists. Updating URL...")
            return self.run_git_command(["remote", "set-url", remote_name, remote_url])

        return self.run_git_command(["remote", "add", remote_name, remote_url])

    def push(self):
        """ Force pushes the current branch to the specified remote. """
        return self.run_git_command(["push", "--force", self.remote, "master"])

    import subprocess

    def can_push_to_git(self):
        """
        Checks if the user has valid Git credentials and can connect to the specified remote.
        Returns True if authentication is successful, otherwise returns False.
        """
        remote = self.remote
        if not remote:
            self.logger.error("Error: No remote URL provided. Cannot check Git push ability.")
            self.pushToRemote = False
            return False

        try:
            # Check if Git is installed
            subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Check if the remote is accessible
            check_remote = subprocess.run(
                ["git", "ls-remote", remote], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if check_remote.returncode == 0:
                self.pushToRemote = True
                return True
            else:
                self.logger.error(f"Error: Unable to access Git remote: {check_remote.stderr.strip()}")
                self.pushToRemote = False
                return False

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git error: {e}")
            self.pushToRemote = False
            return False

    def is_local_up_to_date(self):
        """
        Compares the local repository state with the remote repository state.
        Returns True if both are the same, False otherwise.
        """
        try:
            # Fetch the latest updates from the remote repository
            self.run_git_command(["fetch", self.remote])

            # Get the local and remote commit hashes
            local_commit = self.run_git_command(["rev-parse", "HEAD"])
            remote_commit = self.run_git_command(["rev-parse", f"origin/main"])

            # Compare the hashes
            return local_commit == remote_commit
        except Exception as e:
            self.logger.error(f"Error checking repo state: {e}")
            return False

    def revert_commits(self, commit_hashes):
        """
        Reverts a list of commit hashes one by one.
        If a commit cannot be reverted, it logs an error and continues with the next one.
        """
        if not commit_hashes:
            self.logger.warning("No commit hashes provided to revert.")
            return False

        for commit in commit_hashes:
            self.logger.info(f"Reverting commit: {commit}")
            result = self.run_git_command(["revert", "--no-commit", commit])

            if "Error" in result:
                self.logger.error(f"Failed to revert commit {commit}: {result}")
                return False

        # Commit all reverted changes in one go
        final_commit = self.commit("Reverted commits", "Batch reverted the given commits.")

        if "Error" in final_commit:
            self.logger.error(f"Failed to commit reverted changes: {final_commit}")
            return False

        return True

    def checkIfSolutionExists(self, title_slug):
        """
        Checks if a solution file (with any extension) already exists in the local repo.
        """
        # List all files in the repository
        for file in os.listdir(self.repo_path):
            if file.startswith(f"{title_slug}."):  # Match any extension
                return True
        return False

    def addSummaryToReadMe(self):
        readme_path = os.path.join(self.repo_path, "README.md")

        with open(readme_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Identify start and end of the existing summary (if any)
        summary_start = next((i for i, line in enumerate(lines) if "## 📊 LeetCode Summary" in line), None)
        initTableStart = next((i for i, line in enumerate(lines) if "| Problem |" in line), None)

        if initTableStart is None:
            print("⚠️ Table not found in README.md")
            return

        table_start = initTableStart + 2  # Skip header lines
        data_lines = [line.strip() for line in lines[table_start:] if line.strip().startswith("|")]

        # Extract data and clean it
        data = [line.split("|")[1:-1] for line in data_lines if len(line.split("|")) > 4]
        df = pd.DataFrame(data, columns=["Problem", "Runtime", "Memory", "Difficulty"])

        # Convert values to float
        df["Runtime"] = df["Runtime"].str.strip().str.replace("%", "", regex=False).astype(float)
        df["Memory"] = df["Memory"].str.strip().str.replace("%", "", regex=False).astype(float)

        # Compute summary statistics
        summary_df = df.groupby("Difficulty").agg(
            Total=("Problem", "count"),
            Avg_Runtime=("Runtime", "mean"),
            Avg_Memory=("Memory", "mean")
        ).round(2).reset_index()

        # Generate summary text
        summary_text = f"## 📊 LeetCode Summary\n**Total questions done: {len(df)}**\n\n"
        summary_text += "| Difficulty | Total Questions | Avg Runtime | Avg Memory |\n"
        summary_text += "|------------|----------------|-------------|------------|\n"
        summary_text += "\n".join(
            f"| {row.Difficulty} | {row.Total} | {row.Avg_Runtime}% | {row.Avg_Memory}% |"
            for _, row in summary_df.iterrows()
        ) + "\n\n"

        # Remove existing summary (if present)
        if summary_start is not None:
            linesBeforeSummary = lines[0:summary_start]
            linesAfterSummary = lines[initTableStart:]
            lines = linesBeforeSummary+linesAfterSummary

        # Write the updated content
        with open(readme_path, "w", encoding="utf-8") as file:
            file.write(summary_text + "".join(lines))

        # Commit the changes
        self.commit("Updated LeetCode Summary in README.md")
