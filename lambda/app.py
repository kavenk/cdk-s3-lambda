import json
import urllib.parse
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3 = boto3.client('s3')

def handler(event, context):
    """
    Lambda function that processes files uploaded to an S3 bucket.
    The function reads the content of single-line text files and processes them.
    
    Args:
        event: The AWS Lambda event object containing S3 event details
        context: The AWS Lambda context object
    
    Returns:
        dict: A response indicating the result of the processing
    """
    logger.info('Received event: %s', json.dumps(event))
    
    # Get the S3 bucket and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    try:
        # Get the object from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        
        # Check if the file is a text file and not too large
        content_type = response.get('ContentType', '')
        content_length = response.get('ContentLength', 0)
        
        if not content_type.startswith('text/') and not key.endswith('.txt'):
            logger.warning(f"Skipping file {key} with content type {content_type}")
            return {
                'statusCode': 200,
                'body': f"Skipped file {key} (not a text file)"
            }
        
        if content_length > 1024 * 1024:  # Skip files larger than 1MB
            logger.warning(f"File {key} is too large ({content_length} bytes)")
            return {
                'statusCode': 200,
                'body': f"Skipped file {key} (too large)"
            }
        
        # Read the file content
        file_content = response['Body'].read().decode('utf-8')
        
        # For single-line files, process the content
        if file_content.count('\n') <= 1:
            logger.info(f"Processing single-line file: {key}")
            processed_content = process_line(file_content.strip())
            logger.info(f"Processed content: {processed_content}")
        else:
            logger.info(f"File {key} has multiple lines, only processing first line")
            first_line = file_content.split('\n')[0].strip()
            processed_content = process_line(first_line)
            logger.info(f"Processed first line: {processed_content}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'bucket': bucket,
                'key': key,
                'processedContent': processed_content
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing file {key} from bucket {bucket}: {e}")
        raise e

def process_line(line):
    """
    Process a single line of text.
    Args:
        line (str): The line of text to process
        
    Returns:
        dict: The processed data
    """
    # Example processing - parse as JSON if possible, otherwise just return the line
    try:
        data = json.loads(line)
        return {
            'type': 'json',
            'data': data,
            'wordCount': None,
            'charCount': len(line)
        }
    except json.JSONDecodeError:
        # Not JSON, so do some basic text analysis
        words = line.split()
        return {
            'type': 'text',
            'data': line,
            'wordCount': len(words),
            'charCount': len(line)
        }