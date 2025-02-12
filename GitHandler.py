import subprocess
import os
from logger import Logger
from logging import Logger as LG

class GitHandler:
    logger: LG

    def __init__(self, repo_path="."):
        """
        Initialize the GitHandler with a repository path.
        If the path is not a Git repository, it initializes one with a README.
        """
        self.repo_path = os.path.abspath(repo_path)
        os.makedirs(self.repo_path, exist_ok=True)
        self.logger = Logger("GIT").get_logger()

        if not self.is_git_repo():
            self.logger.warning("No Git repository found. Initializing a new one with README...")
            self.init_repo()

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
                readme.write("| Problem | Runtime Percentile | Memory Percentile |\n")
                readme.write("|---------|-------------------|-------------------|\n")
            self.run_git_command(["add", "README.md"])
            self.commit("Added README.md", "Initialized the repository with a README file.")

    def commit(self, message, description="", body=""):
        """ Commits changes with a given commit message, description, and body. """
        commit_message = f"{message}\n\n{description}\n\n{body}"
        return self.run_git_command(["commit", "-am", commit_message])

    def commit_from_data(self, data):
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
        commit_result = self.commit(title_slug, description, file_path)

        # Update README.md
        self.update_readme(title_slug, runtime_percentile, memory_percentile)

        return commit_result

    def update_readme(self, title_slug, runtime_percentile, memory_percentile):
        """ Adds a new row to README.md with submission details. """
        readme_path = os.path.join(self.repo_path, "README.md")
        try:
            new_line = f"| {title_slug} | {int(runtime_percentile)}% | {int(memory_percentile)}% |\n"
        except:
            new_line = f"| {title_slug} | {runtime_percentile}% | {memory_percentile}% |\n"

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
    def push(self, remote="origin", branch="main"):
        """ Pushes the current branch to the specified remote. """
        return self.run_git_command(["push", remote, branch])
