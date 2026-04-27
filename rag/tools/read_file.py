import os
import boto3
from strands import tool


@tool
def read_from_s3(file_name: str) -> str:
    """
    Reads a file from S3 with the given file_name and returns its contents as a string.

    :param file_name: The S3 object key of the file to read (e.g. "report.html", "abc123.html").
    :return: The file contents as a string, or an error message if the operation failed.

    Examples:
        - User asks "show me what's in report.html" → read_from_s3("report.html")
        - User asks "load the existing dashboard for this session" → read_from_s3("{session_id}.html")
        - User asks "what did we save last time?" → read_from_s3("summary.txt")
    """
    try:
        bucket_name = os.environ.get("S3_REPORTS_BUCKET_NAME")
        if not bucket_name:
            return "Error: S3_REPORTS_BUCKET_NAME environment variable is not set."

        s3_client = boto3.client("s3")
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error: {e}"
