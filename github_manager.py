import os

from github import Github, GithubException
# handle dotenv for environment variables - github access token
from dotenv import load_dotenv
load_dotenv()

# create github object
g = Github(os.getenv("GITHUB_ACCESS_TOKEN")) 

def create_repo(repo_name):
    user = g.get_user()
    if repo_name in [repo.name for repo in user.get_repos()]:
        return f"Error: Repository '{repo_name}' already exists."
    user.create_repo(repo_name)
    return f"Successfully created repository '{repo_name}'"

def delete_repo(repo_name):
    user = g.get_user()
    if repo_name not in [repo.name for repo in user.get_repos()]:
        return f"Error: Repository '{repo_name}' does not exist."
    user.get_repo(repo_name).delete()
    return f"Successfully deleted repository '{repo_name}'"

def list_files(repo_name, branch="main"):
    user = g.get_user()
    if repo_name not in [repo.name for repo in user.get_repos()]:
        return f"Error: Repository '{repo_name}' does not exist."
    # we want to return a string of all the files in the repo, including files in subdirectories!!
    repo = user.get_repo(repo_name)
    contents = repo.get_contents("", ref=branch)
    files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content.path)
    return "\n".join(files)

def delete_file(repo_name, filename, msg="remove file", branch="main"):
    user = g.get_user()
    if repo_name not in [repo.name for repo in user.get_repos()]:
        return f"Error: Repository '{repo_name}' does not exist."
    repo = user.get_repo(repo_name)
    contents = repo.get_contents(filename, ref=branch)
    repo.delete_file(contents.path, msg, contents.sha, branch=branch)
    return f"Successfully deleted {filename} in repository '{repo_name}' branch '{branch}'"

def read_file(repo_name, filename, branch="main"):
    user = g.get_user()
    if repo_name not in [repo.name for repo in user.get_repos()]:
        return f"Error: Repository '{repo_name}' does not exist."
    try:
        repo = user.get_repo(repo_name)
        contents = repo.get_contents(filename, ref=branch)
        return contents.decoded_content.decode()  # decode bytes to string
    except GithubException as e:
        return str(e)

def write_file(repo_name, filename, content, msg="write file", branch="main"):
    user = g.get_user()
    if repo_name not in [repo.name for repo in user.get_repos()]:
        return f"Error: Repository '{repo_name}' does not exist."
    repo = user.get_repo(repo_name)
    try:
        contents = repo.get_contents(filename, ref=branch)
        repo.update_file(contents.path, msg, content, contents.sha, branch=branch)
    except GithubException:
        try:
            repo.create_file(filename, msg, content, branch=branch)
        except GithubException as e:
            return str(e)

    return f"Successfully wrote to {filename} in repository '{repo_name}' branch '{branch}'"

def rename_file(repo_name, old_filename, new_filename, msg="rename file", branch="main"):
    user = g.get_user()
    if repo_name not in [repo.name for repo in user.get_repos()]:
        return f"Error: Repository '{repo_name}' does not exist."
    repo = user.get_repo(repo_name)
    contents = repo.get_contents(old_filename, ref=branch)
    repo.create_file(new_filename, msg, contents.decoded_content, branch=branch)
    repo.delete_file(contents.path, msg, contents.sha, branch=branch)
    return f"Successfully renamed {old_filename} to {new_filename} in repository '{repo_name}' branch '{branch}'"

def list_branches(repo_name):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        return [branch.name for branch in repo.get_branches()]
    except GithubException as e:
        return str(e)

def get_branch(repo_name, branch_name):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        return repo.get_branch(branch=branch_name).name
    except GithubException as e:
        return str(e)
    
def create_branch(repo_name, branch_name, base_branch_name="main"):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        base_branch = repo.get_branch(branch=base_branch_name)
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)
        return f"Successfully created branch '{branch_name}' in repository '{repo_name}'"
    except GithubException as e:
        return str(e)

def create_pull_request(repo_name, title, body, head, base):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return "Successfully created pull request #" + str(pr.number)
    except GithubException as e:
        return str(e)
    
def list_pull_requests(repo_name, state="open"):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        pull_requests = repo.get_pulls(state=state)
        # format: [pull_request1 (pull_request1_number), pull_request2 (pull_request2_number)]
        return str([f"{pull_request.title} ({pull_request.number})" for pull_request in pull_requests])
    except GithubException as e:
        return str(e)
    
def get_pull_request(repo_name, pull_request_number):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)
        return str(pull_request)
    except GithubException as e:
        return str(e)

def merge_pull_request(repo_name, pull_request_number, commit_message="merge pull request"):
    try:
        print("merging pull request")
        user = g.get_user()
        repo = user.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)
        pull_request.merge(commit_message)
        return f"Successfully merged pull request #{pull_request_number}"
    except GithubException as e:
        return str(e)
    
def close_pull_request(repo_name, pull_request_number):
    try:
        user = g.get_user()
        repo = user.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)
        pull_request.edit(state="closed")
        return f"Successfully closed pull request #{pull_request_number}"
    except GithubException as e:
        return str(e)
    
def list_commits(repo_name, branch_name="main"):
    try:
        user = g.get_user()
        repo = user.get_repo(repo_name)
        commits = repo.get_commits(sha=branch_name)
        # format: [commit1 (commit1_sha), commit2 (commit2_sha)]
        return str([f"{commit.commit.message} ({commit.sha})" for commit in commits])
    except GithubException as e:
        return str(e)
    
def get_commit(repo_name, commit_sha):
    try:
        user = g.get_user()
        repo = user.get_repo(repo_name)
        commit = repo.get_commit(commit_sha)
        return str(commit)
    except GithubException as e:
        return str(e)
    
def list_open_issues(repo_name):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        open_issues = repo.get_issues(state='open')
        # format: [issue1 (issue1_number), issue2 (issue2_number)]
        return str([f"{issue.title} ({issue.number})" for issue in open_issues])
    except GithubException as e:
        return str(e)

def get_issue(repo_name, issue_number):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number)
        return str(issue)
    except GithubException as e:
        return str(e)

def create_issue_comment(repo_name, issue_number, comment):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)
        return "Comment created"
    except GithubException as e:
        return str(e)
    
def close_issue(repo_name, issue_number):
    try:
        user = g.get_user()
        if repo_name not in [repo.name for repo in user.get_repos()]:
            return f"Error: Repository '{repo_name}' does not exist."
        repo = user.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number)
        issue.edit(state='closed')
        return "Issue closed"
    except GithubException as e:
        return str(e)