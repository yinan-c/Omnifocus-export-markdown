import sqlite3
import os
from datetime import datetime, timedelta

def from_mac_timestamp(mac_time):
    """Converts a Mac timestamp (seconds since January 1, 2001) to a Python datetime object."""
    mac_epoch = datetime(2001, 1, 1)
    return mac_epoch + timedelta(seconds=mac_time)

def fetch_completed_or_dropped_tasks(database_path):
    """Fetch tasks that are either completed or flagged as dropped using effectiveDateHidden."""
    query = """
    SELECT
        t2.name AS project_name,
        t2.persistentIdentifier AS project_identifier,
        t1.name AS task_name,
        t1.persistentIdentifier AS task_identifier,
        t1.plainTextNote AS task_note,
        t1.dateCompleted AS completed_date,
        t1.effectiveDateHidden AS effective_date_hidden
    FROM
        Task t1
    LEFT JOIN
        Task t2
    ON
        t1.containingProjectInfo = t2.persistentIdentifier
    WHERE
        t1.dateCompleted IS NOT NULL OR t1.effectiveDateHidden IS NOT NULL
    ORDER BY
        COALESCE(t1.dateCompleted, t1.effectiveDateHidden) DESC
    """
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row  # To access columns by name
        cursor = conn.execute(query)
        return [{
            'project_name': row['project_name'],
            'project_identifier': row['project_identifier'],
            'task_name': row['task_name'],
            'task_identifier': row['task_identifier'],
            'task_note': row['task_note'],
            'completed_date': from_mac_timestamp(row['completed_date']).strftime('%Y-%m-%d %H:%M:%S') if row['completed_date'] else None,
            'effective_date_hidden': from_mac_timestamp(row['effective_date_hidden']).strftime('%Y-%m-%d %H:%M:%S') if row['effective_date_hidden'] else None
        } for row in cursor]

def format_task_output(task):
    """Format a single task output."""
    project_name = task['project_name'] or "No Project"
    task_name = task['task_name']
    task_note = task['task_note']
    date_str = task['completed_date'] if task['completed_date'] else task['effective_date_hidden']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    status_symbol = "[x]" if task['completed_date'] else "[c]"
    time_format = date_obj.strftime('%H:%M')
    
    output = f"- {status_symbol} {time_format} [{project_name}](omnifocus:///task/{task['project_identifier']}) - [{task_name}](omnifocus:///task/{task['task_identifier']})"
    if task_note:
        output += f"\n> {task_note}"
    return output

def generate_markdown_by_date(tasks):
    """Generate markdown output grouped by completion/drop date."""
    grouped_by_date = {}
    for task in tasks:
        date_key = task['completed_date'] if task['completed_date'] else task['effective_date_hidden']
        date_key = date_key.split(" ")[0]  # Extract only the date part
        
        if date_key not in grouped_by_date:
            grouped_by_date[date_key] = []
        grouped_by_date[date_key].append(format_task_output(task))
    
    content = ""
    for date, tasks in sorted(grouped_by_date.items(), reverse=True):
        content += f"## {date}\n"
        content += "\n".join(tasks) + "\n\n"
    return content

def write_to_file(content, output_file):
    """Write content to a markdown file."""
    with open(output_file, 'w') as file:
        file.write(content)

# Find the database
database_path = None
for root, dirs, files in os.walk(os.path.expanduser("~/Library/Group Containers")):
    if "OmniFocusDatabase.db" in files and "OmniFocus4" in root:
        database_path = os.path.join(root, "OmniFocusDatabase.db")
        break

if not database_path:
    raise Exception("OmniFocus 4 database not found in ~/Library/Group Containers")

tasks = fetch_completed_or_dropped_tasks(database_path)
markdown_content = generate_markdown_by_date(tasks)
output_filename = "omnifocus_completed_dropped.md"
write_to_file(markdown_content, output_filename)
