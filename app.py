import os
from datetime import datetime, timedelta
import todoist
from typing import List, Dict
import pytz
from email_providers import AWSEmailProvider, SendGridEmailProvider

class TodoistEmailReminder:
    def __init__(self, todoist_api_key: str, email_provider: EmailProvider):
        self.api = todoist.TodoistAPI(todoist_api_key)
        self.email_provider = email_provider
        
    def get_tasks(self) -> Dict[str, List[Dict]]:
        """Fetch and categorize tasks from Todoist."""
        self.api.sync()
        today = datetime.now(pytz.UTC).date()
        
        tasks_by_date = {
            'today': [],
            'upcoming': []
        }
        
        for item in self.api.state['items']:
            if item['due'] is None:
                continue
                
            due_date = datetime.strptime(item['due']['date'], '%Y-%m-%d').date()
            project = self.get_project_name(item['project_id'])
            
            task_info = {
                'content': item['content'],
                'project': project,
                'priority': item['priority'],
                'due_date': due_date.strftime('%Y-%m-%d')
            }
            
            if due_date == today:
                tasks_by_date['today'].append(task_info)
            elif today < due_date <= today + timedelta(days=4):
                tasks_by_date['upcoming'].append(task_info)
                
        return tasks_by_date
    
    def get_project_name(self, project_id: str) -> str:
        """Get project name from project ID."""
        for project in self.api.state['projects']:
            if project['id'] == project_id:
                return project['name']
        return 'No Project'

    def generate_html_content(self, tasks: Dict[str, List[Dict]]) -> str:
        """Generate HTML email content from tasks."""
        html = """
        <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                    h2 { color: #2980b9; margin-top: 20px; }
                    .task { margin: 10px 0; padding: 10px; border-left: 4px solid #3498db; background: #f9f9f9; }
                    .project { color: #7f8c8d; font-size: 0.9em; }
                    .due-date { color: #e74c3c; font-size: 0.9em; }
                    .priority-4 { border-left-color: #e74c3c; }
                    .priority-3 { border-left-color: #f39c12; }
                    .priority-2 { border-left-color: #3498db; }
                    .priority-1 { border-left-color: #95a5a6; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Your Todoist Tasks Summary</h1>
        """
        
        html += "<h2>Today's Tasks</h2>"
        if tasks['today']:
            for task in sorted(tasks['today'], key=lambda x: x['priority'], reverse=True):
                html += self._generate_task_html(task)
        else:
            html += "<p>No tasks due today!</p>"
            
        html += "<h2>Upcoming Tasks (Next 4 Days)</h2>"
        if tasks['upcoming']:
            for task in sorted(tasks['upcoming'], key=lambda x: (x['due_date'], -x['priority'])):
                html += self._generate_task_html(task)
        else:
            html += "<p>No upcoming tasks!</p>"
            
        html += """
                </div>
            </body>
        </html>
        """
        return html
    
    def _generate_task_html(self, task: Dict) -> str:
        """Generate HTML for a single task."""
        return f"""
        <div class="task priority-{task['priority']}">
            <strong>{task['content']}</strong><br>
            <span class="project">Project: {task['project']}</span><br>
            <span class="due-date">Due: {task['due_date']}</span>
        </div>
        """
    
    def send_email(self, recipient_email: str, sender_email: str, tasks: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Send email using configured provider."""
        subject = f"Todoist Tasks Summary - {datetime.now().strftime('%Y-%m-%d')}"
        html_content = self.generate_html_content(tasks)
        
        return self.email_provider.send_email(
            subject=subject,
            html_content=html_content,
            to_email=recipient_email,
            from_email=sender_email
        )

