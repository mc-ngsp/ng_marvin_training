import os
import boto3
from strands import tool


@tool
def write_to_s3(file_name: str, contents: str) -> str:
    """
    Creates a file in S3 with the given file_name and stores the contents in it.

    :param file_name: The S3 object key for the file (e.g. "report.html", "abc123.html").
    :param contents: The text content to write into the file.
    :return: A success message with the S3 URL, or an error message if the operation failed.

    Examples:
        - User asks "save this HTML as my dashboard" → write_to_s3("dashboard.html", "<html>...</html>")
        - User asks "write the summary to a file" → write_to_s3("summary.txt", "Summary content...")
        - User asks "update the session file with the new chart" → write_to_s3("{session_id}.html", updated_html)
    """
    try:
        bucket_name = os.environ.get("S3_REPORTS_BUCKET_NAME")
        if not bucket_name:
            return "Error: S3_REPORTS_BUCKET_NAME environment variable is not set."

        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=contents.encode("utf-8"),
        )
        return f"Success: file uploaded to s3://{bucket_name}/{file_name}"
    except Exception as e:
        return f"Error: {e}"
