import sqlite3
from collections import defaultdict
import os
import hashlib

def compute_md5(text):
    """Compute MD5 hash of the given text."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def fetch_tasks_with_project_info(database_path):
    """Extract tasks, their associated project name, project identifier, 
    completion status, and dropped status from the database."""
    query = """
    SELECT 
        t1.name AS task_name,
        t1.persistentIdentifier AS task_identifier,
        t1.plainTextNote AS task_note,
        t2.name AS project_name,
        t2.persistentIdentifier AS project_identifier,
        t1.dateCompleted IS NOT NULL AS is_completed,
        t1.effectiveDateHidden IS NOT NULL AS is_dropped
    FROM 
        Task t1
    LEFT JOIN
        Task t2
    ON
        t1.containingProjectInfo = t2.persistentIdentifier
    """
    with sqlite3.connect(database_path) as conn:
        return conn.execute(query).fetchall()

def fetch_projects_with_metadata_from_projectinfo(database_path):
    """Get metadata (name, identifier and status) for projects from the ProjectInfo table."""
    query = """
    SELECT 
        Task.name AS project_name,
        Task.persistentIdentifier AS project_identifier,
        ProjectInfo.effectiveStatus AS project_status
    FROM 
        Task
    JOIN
        ProjectInfo
    ON
        Task.persistentIdentifier = ProjectInfo.task
    """
    with sqlite3.connect(database_path) as conn:
        results = conn.execute(query).fetchall()
        print(len(results))
    return {project_id: (project_id, project_name, project_status) for project_name, project_id, project_status in results}

def sanitize_filename(filename):
    """Sanitize the filename by removing or replacing special characters."""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def generate_md_metadata(project_info):
    """Generate Markdown metadata for a given project."""
    project_id, project_name, project_status = project_info
    if not project_id:
        return f"status: {project_status}\nurl: omnifocus:///inbox\n"
    return f"status: {project_status}\nurl: omnifocus:///task/{project_id}\n"

def format_note_as_blockquote(note):
    """Format the note text as a Markdown blockquote."""
    return '\n'.join([f"> {line}" if line.strip() else '>' for line in note.split('\n')])

def generate_md_content_with_title(tasks, project_id):
    """Generate Markdown content for a given project, considering the task completion status and using the task that matches the project_id as the title."""
    content = ""
    
    # Find the task that matches the project_id and use it as the title
    title_task = None
    for task in tasks:
        if task[1] == project_id:
            title_task = task
            tasks.remove(task)
            break
    
    if title_task:
        task_name, task_identifier, task_note, _, _, _, _ = title_task
        formatted_note = format_note_as_blockquote(task_note) if task_note else ""
        content += f"# [{task_name}](omnifocus:///task/{task_identifier})\n{formatted_note}\n\n"
    
    # Add the rest of the tasks
    for task_name, task_identifier, task_note, _, _, is_completed, is_dropped in tasks:
        checkbox = "- [x]" if is_completed else ("- [c]" if is_dropped else "- [ ]")
        formatted_note = format_note_as_blockquote(task_note) if task_note else ""
        content += f"{checkbox} [{task_name}](omnifocus:///task/{task_identifier})\n{formatted_note}\n\n"
    
    return content

def create_md_files(tasks_with_project_info, project_metadata, output_directory):
    """Create Markdown files based on project name, project identifier and metadata, considering the task completion status."""
    tasks_grouped_by_project = defaultdict(list)
    for task in tasks_with_project_info:
        project_name, project_id = task[3], task[4]
        tasks_grouped_by_project[(project_name, project_id)].append(task)

    os.makedirs(output_directory, exist_ok=True)
    for (project_name, project_id), tasks in tasks_grouped_by_project.items():
        sanitized_name = sanitize_filename(project_name if project_name else "Inbox")
        project_name = tasks[0][3]  # Get the project_name from the first task
        filename = f"{sanitized_name}_{project_id}.md"
        file_path = os.path.join(output_directory, filename)
        
        md_metadata = generate_md_metadata(project_metadata.get(project_id, (project_id, "Untitled", "N/A")))
        new_content = "---\n" + md_metadata + "---\n" + generate_md_content_with_title(tasks, project_id)

        # Check if file already exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as md_file:
                existing_content = md_file.read()
            # If content hasn't changed, skip writing to the file
            if compute_md5(existing_content) == compute_md5(new_content):
                continue

        with open(file_path, 'w') as md_file:
            md_file.write(new_content)

database_path = None
for root, dirs, files in os.walk(os.path.expanduser("~/Library/Group Containers")):
    if "OmniFocusDatabase.db" in files and "OmniFocus4" in root:
        database_path = os.path.join(root, "OmniFocusDatabase.db")
        break

if not database_path:
    raise Exception("OmniFocus 4 database not found in ~/Library/Group Containers")


output_directory = "omnifocus_md"
tasks_with_project_info = fetch_tasks_with_project_info(database_path)
project_metadata = fetch_projects_with_metadata_from_projectinfo(database_path)
create_md_files(tasks_with_project_info, project_metadata, output_directory)
