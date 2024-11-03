// Import required modules
const AWS = require('aws-sdk');
const todoist = require('todoist');

// Configure AWS SES
const ses = new AWS.SES({ region: process.env.AWS_REGION });

// Create TodoistEmailReminder class
class TodoistEmailReminder {
  constructor(todoistApiKey) {
    this.api = todoist(todoistApiKey);
  }

  async getTasks() {
    // Synchronize tasks
    await this.api.sync();
    const today = new Date().toISOString().split('T')[0];

    const tasksByDate = {
      today: [],
      upcoming: []
    };

    this.api.items.forEach(item => {
      if (!item.due) return;
      const dueDate = new Date(item.due.date).toISOString().split('T')[0];

      const taskInfo = {
        content: item.content,
        project: this.getProjectName(item.project_id),
        priority: item.priority,
        due_date: dueDate
      };

      if (dueDate === today) {
        tasksByDate.today.push(taskInfo);
      } else if (new Date(dueDate) <= new Date(today).setDate(new Date().getDate() + 4)) {
        tasksByDate.upcoming.push(taskInfo);
      }
    });

    return tasksByDate;
  }

  getProjectName(projectId) {
    const project = this.api.projects.find(p => p.id === projectId);
    return project ? project.name : 'No Project';
  }

  async generateHtmlContent(tasks) {
    let html = `<html><body><h1>Your Todoist Tasks Summary</h1>`;
    html += `<h2>Today's Tasks</h2>`;

    if (tasks.today.length) {
      tasks.today.forEach(task => {
        html += `<p>${task.content} - Project: ${task.project} - Priority: ${task.priority}</p>`;
      });
    } else {
      html += `<p>No tasks due today!</p>`;
    }

    html += `<h2>Upcoming Tasks (Next 4 Days)</h2>`;
    if (tasks.upcoming.length) {
      tasks.upcoming.forEach(task => {
        html += `<p>${task.content} - Project: ${task.project} - Priority: ${task.priority}</p>`;
      });
    } else {
      html += `<p>No upcoming tasks!</p>`;
    }

    html += `</body></html>`;
    return html;
  }

  async sendEmail(tasks) {
    const htmlContent = await this.generateHtmlContent(tasks);
    const params = {
      Destination: { ToAddresses: [process.env.RECIPIENT_EMAIL] },
      Message: {
        Body: { Html: { Charset: "UTF-8", Data: htmlContent } },
        Subject: { Charset: 'UTF-8', Data: `Todoist Tasks Summary - ${new Date().toISOString().split('T')[0]}` }
      },
      Source: process.env.SENDER_EMAIL
    };

    return ses.sendEmail(params).promise();
  }
}

// AWS Lambda handler
exports.handler = async (event) => {
  const reminder = new TodoistEmailReminder(process.env.TODOIST_API_KEY);
  const tasks = await reminder.getTasks();
  const result = await reminder.sendEmail(tasks);

  return {
    statusCode: result ? 200 : 500,
    body: JSON.stringify(result)
  };
};
