# todoist
aws s3 mb s3://your-sam-bucket-name --region your-region



# Required
gh secret set AWS_ACCESS_KEY_ID
gh secret set AWS_SECRET_ACCESS_KEY
gh secret set AWS_REGION
gh secret set AWS_SAM_BUCKET
gh secret set TODOIST_API_KEY
gh secret set SENDER_EMAIL
gh secret set RECIPIENT_EMAIL

# Optional (for notifications)
gh secret set SLACK_CHANNEL_ID
gh secret set SLACK_BOT_TOKEN



{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "s3:*",
                "lambda:*",
                "iam:*",
                "ses:*"
            ],
            "Resource": "*"
        }
    ]
}