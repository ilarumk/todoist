def aws_lambda_handler(event, context):
    """AWS Lambda handler function."""
    email_provider = AWSEmailProvider(os.environ['AWS_REGION'])
    
    reminder = TodoistEmailReminder(
        todoist_api_key=os.environ['TODOIST_API_KEY'],
        email_provider=email_provider
    )
    
    result = reminder.send_email(
        recipient_email=os.environ['RECIPIENT_EMAIL'],
        sender_email=os.environ['SENDER_EMAIL'],
        tasks=reminder.get_tasks()
    )
    
    return {
        'statusCode': 200 if result['success'] else 500,
        'body': result
    }

def gcp_function_handler(event, context):
    """Google Cloud Function handler."""
    email_provider = SendGridEmailProvider(os.environ['SENDGRID_API_KEY'])
    
    reminder = TodoistEmailReminder(
        todoist_api_key=os.environ['TODOIST_API_KEY'],
        email_provider=email_provider
    )
    
    result = reminder.send_email(
        recipient_email=os.environ['RECIPIENT_EMAIL'],
        sender_email=os.environ['SENDER_EMAIL'],
        tasks=reminder.get_tasks()
    )
    
    return result
