from github import Github, GithubException

class GithubManager:
    def __init__(self, github_oauth_token):
        try:
            self.github = Github(github_oauth_token)
            self._get_user()  # Test the credentials
        except GithubException as e:
            print(f"Error initializing GithubManager: {e}")

    def _get_user(self):
        try:
            return self.github.get_user()
        except GithubException as e:
            print(f"Error getting user: {e}")

    def _repo_exists(self, repo_name):
        try:
            return repo_name in [repo.name for repo in self._get_user().get_repos()]
        except GithubException as e:
            print(f"Error checking if repo exists: {e}")

    def _get_repo(self, repo_name):
        try:
            if not self._repo_exists(repo_name):
                print(f"Error: Repository '{repo_name}' does not exist.")
            else:
                return self._get_user().get_repo(repo_name)
        except GithubException as e:
            print(f"Error getting repo: {e}")

    def create_repo(self, repo_name):
        try:
            if self._repo_exists(repo_name):
                return f"Error: Repository '{repo_name}' already exists."
            self._get_user().create_repo(repo_name)
            return f"Successfully created repository '{repo_name}'"
        except GithubException as e:
            print(f"Error creating repo: {e}")

    def delete_repo(self, repo_name):
        try:
            repo = self._get_repo(repo_name)
            repo.delete()
            return f"Successfully deleted repository '{repo_name}'"
        except GithubException as e:
            print(f"Error deleting repo: {e}")

    def list_files(self, repo_name, branch="main"):
        try:
            repo = self._get_repo(repo_name)
            if not repo:
                return f"Error: Repository '{repo_name}' does not exist."
            contents = repo.get_contents("", ref=branch)
            files = []
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    files.append(file_content.path)
            return "\n".join(files)
        except GithubException as e:
            print(f"Error listing files: {e}")

    def delete_file(self, repo_name, filename, msg, branch="main"):
        try:
            repo = self._get_repo(repo_name)
            contents = repo.get_contents(filename, ref=branch)
            repo.delete_file(contents.path, msg, contents.sha, branch=branch)
            return f"Successfully deleted {filename} in repository '{repo_name}' branch '{branch}'"
        except GithubException as e:
            print(f"Error deleting file: {e}")

    def read_file(self, repo_name, filename, branch="main"):
        try:
            repo = self._get_repo(repo_name)
            contents = repo.get_contents(filename, ref=branch)
            return f"read_file({repo_name} branch {branch}): \n" + contents.decoded_content.decode()
        except GithubException as e:
            print(f"Error reading file: {e}")

    def write_file(self, repo_name, filename, content, msg, branch="main"):
        try:
            repo = self._get_repo(repo_name)
            contents = repo.get_contents(filename, ref=branch)
            repo.update_file(contents.path, msg, content, contents.sha, branch=branch)
            return f"Successfully wrote to {filename} in repository '{repo_name}' branch '{branch}'"
        except GithubException.NotFoundError:
            repo.create_file(filename, msg, content, branch=branch)
            return f"Successfully created {filename} in repository '{repo_name}' branch '{branch}'"
        except GithubException as e:
            print(f"Error writing file: {e}")

    def rename_file(self, repo_name, old_filename, new_filename, msg, branch="main"):
        try:
            repo = self._get_repo(repo_name)
            contents = repo.get_contents(old_filename, ref=branch)
            repo.create_file(new_filename, msg, contents.decoded_content.decode(), branch=branch)
            repo.delete_file(contents.path, msg, contents.sha, branch=branch)
            return f"Successfully renamed {old_filename} to {new_filename} in repository '{repo_name}' branch '{branch}'"
        except GithubException as e:
            print(f"Error renaming file: {e}")

    def list_branches(self, repo_name):
        try:
            repo = self._get_repo(repo_name)
            return [branch.name for branch in repo.get_branches()]
        except GithubException as e:
            print(f"Error listing branches: {e}")

    def get_branch(self, repo_name, branch_name):
        try:
            repo = self._get_repo(repo_name)
            return repo.get_branch(branch=branch_name).name
        except GithubException as e:
            print(f"Error getting branch: {e}")

    def create_branch(self, repo_name, branch_name, base_branch_name="main"):
        try:
            repo = self._get_repo(repo_name)
            base_branch = repo.get_branch(branch=base_branch_name)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)
            return f"Successfully created branch '{branch_name}' in repository '{repo_name}'"
        except GithubException as e:
            print(f"Error creating branch: {e}")

    def create_pull_request(self, repo_name, title, body, head, base):
        try:
            repo = self._get_repo(repo_name)
            pr = repo.create_pull(title=title, body=body, head=head, base=base)
            return "Successfully created pull request #" + str(pr.number)
        except GithubException as e:
            print(f"Error creating pull request: {e}")

    def list_pull_requests(self, repo_name, state="open"):
        try:
            repo = self._get_repo(repo_name)
            pull_requests = repo.get_pulls(state=state)
            return [f"{pull_request.title} ({pull_request.number})" for pull_request in pull_requests]
        except GithubException as e:
            print(f"Error listing pull requests: {e}")

    def get_pull_request(self, repo_name, pull_request_number):
        try:
            repo = self._get_repo(repo_name)
            pull_request = repo.get_pull(pull_request_number)
            return str(pull_request)
        except GithubException as e:
            print(f"Error getting pull request: {e}")

    def merge_pull_request(self, repo_name, pull_request_number, commit_message="merge pull request"):
        try:
            repo = self._get_repo(repo_name)
            pull_request = repo.get_pull(pull_request_number)
            pull_request.merge(commit_message)
            return f"Successfully merged pull request #{pull_request_number}"
        except GithubException as e:
            print(f"Error merging pull request: {e}")

    def close_pull_request(self, repo_name, pull_request_number):
        try:
            repo = self._get_repo(repo_name)
            pull_request = repo.get_pull(pull_request_number)
            pull_request.edit(state="closed")
            return f"Successfully closed pull request #{pull_request_number}"
        except GithubException as e:
            print(f"Error closing pull request: {e}")

    def list_commits(self, repo_name, branch_name="main"):
        try:
            repo = self._get_repo(repo_name)
            commits = repo.get_commits(sha=branch_name)
            return [f"{commit.commit.message} ({commit.sha})" for commit in commits]
        except GithubException as e:
            print(f"Error listing commits: {e}")

    def get_commit(self, repo_name, commit_sha):
        try:
            repo = self._get_repo(repo_name)
            commit = repo.get_commit(commit_sha)
            return str(commit)
        except GithubException as e:
            print(f"Error getting commit: {e}")

    def list_open_issues(self, repo_name):
        try:
            repo = self._get_repo(repo_name)
            open_issues = repo.get_issues(state='open')
            return [f"{issue.title} ({issue.number})" for issue in open_issues]
        except GithubException as e:
            print(f"Error listing open issues: {e}")

    def get_issue(self, repo_name, issue_number):
        try:
            repo = self._get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            return str(issue)
        except GithubException as e:
            print(f"Error getting issue: {e}")

    def create_issue_comment(self, repo_name, issue_number, comment):
        try:
            repo = self._get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.create_comment(comment)
            return "Comment created"
        except GithubException as e:
            print(f"Error creating issue comment: {e}")

    def close_issue(self, repo_name, issue_number):
        try:
            repo = self._get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.edit(state='closed')
            return "Issue closed"
        except GithubException as e:
            print(f"Error closing issue: {e}")