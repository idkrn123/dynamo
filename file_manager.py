import os
from web_scraper import browse_web

# Creating a dictionary to map function names to functions
def create_project(project_name):
    project_path = os.path.join("projects", project_name)
    if os.path.exists(project_path):
        return f"Error: Project '{project_name}' already exists."
    os.makedirs(project_path)
    return f"Successfully created project '{project_name}'"

def create_subdir(project_name, dirname):
    project_path = os.path.join("projects", project_name, dirname)
    if os.path.exists(project_path):
        return f"Error: Subdirectory '{dirname}' already exists in project '{project_name}'."
    os.makedirs(project_path)
    return f"Successfully created subdirectory '{dirname}' in project '{project_name}'"

def list_projects():
    return "\n".join(os.listdir("projects"))

def list_files(project_name):
    project_path = os.path.join("projects", project_name)
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist."
    files = os.listdir(project_path)
    return "\n".join(files)

def delete_file(project_name, filename):
    project_path = os.path.join("projects", project_name)
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist."
    file_path = os.path.join(project_path, filename)
    if not os.path.exists(file_path):
        return f"Error: File '{filename}' does not exist in project '{project_name}'."
    os.remove(file_path)
    return f"Successfully deleted {filename} in project '{project_name}'"

def read_file(project_name, filename):
    project_path = os.path.join("projects", project_name)
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist."
    file_path = os.path.join(project_path, filename)
    if not os.path.exists(file_path):
        return f"Error: File '{filename}' does not exist in project '{project_name}'."
    with open(file_path, "r") as file:
        content = file.read()
    return content

def write_file(project_name, filename, content):
    project_path = os.path.join("projects", project_name)
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist."
    file_path = os.path.join(project_path, filename)
    with open(file_path, "w") as file:
        file.write(content)
    return f"Successfully wrote to {filename} in project '{project_name}'"

def rename_file(project_name, old_filename, new_filename):
    project_path = os.path.join("projects", project_name)
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist."
    old_file_path = os.path.join(project_path, old_filename)
    if not os.path.exists(old_file_path):
        return f"Error: File '{old_filename}' does not exist in project '{project_name}'."
    new_file_path = os.path.join(project_path, new_filename)
    os.rename(old_file_path, new_file_path)
    return f"Successfully renamed {old_filename} to {new_filename} in project '{project_name}'"

# Mapping function names to function objects
FUNCTION_MAP = {
    'create_project': create_project,
    'create_subdir': create_subdir,
    'list_files': list_files,
    'delete_file': delete_file,
    'read_file': read_file,
    'write_file': write_file,
    'rename_file': rename_file,
    'browse_web': browse_web
}
