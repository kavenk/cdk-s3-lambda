import json
import urllib.parse
import boto3
import os
import logging

# Configure logging with a standard format
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client for operations on S3 objects
s3 = boto3.client('s3')

def handler(event, context):
    """
    Main Lambda handler function triggered by S3 events.
    
    Processes files uploaded to the S3 bucket, specifically handling
    single-line text files and parsing their contents.
    
    Args:
        event (dict): The S3 event notification containing bucket and key information
        context: The Lambda context object
        
    Returns:
        dict: Response with status code and processing results
    """
    logger.info('Received event: %s', json.dumps(event))
    
    # Extract S3 bucket and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    try:
        # Retrieve the object from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        
        # Validate file type and size
        content_type = response.get('ContentType', '')
        content_length = response.get('ContentLength', 0)
        
        # Skip non-text files
        if not content_type.startswith('text/') and not key.endswith('.txt'):
            logger.warning(f"Skipping file {key} with content type {content_type}")
            return {
                'statusCode': 200,
                'body': f"Skipped file {key} (not a text file)"
            }
        
        # Skip files larger than 1MB for performance reasons
        if content_length > 1024 * 1024:
            logger.warning(f"File {key} is too large ({content_length} bytes)")
            return {
                'statusCode': 200,
                'body': f"Skipped file {key} (too large)"
            }
        
        # Read the file content
        file_content = response['Body'].read().decode('utf-8')
        
        # Process the file based on content structure
        if file_content.count('\n') <= 1:
            # Single-line file processing
            logger.info(f"Processing single-line file: {key}")
            processed_content = process_line(file_content.strip())
            logger.info(f"Processed content: {processed_content}")
        else:
            # Multi-line file - process only first line
            logger.info(f"File {key} has multiple lines, only processing first line")
            first_line = file_content.split('\n')[0].strip()
            processed_content = process_line(first_line)
            logger.info(f"Processed first line: {processed_content}")
        
        # Return successful response with processing results
        return {
            'statusCode': 200,
            'body': json.dumps({
                'bucket': bucket,
                'key': key,
                'processedContent': processed_content
            })
        }
        
    except Exception as e:
        # Log and re-raise errors for troubleshooting
        logger.error(f"Error processing file {key} from bucket {bucket}: {e}")
        raise e

def process_line(line):
    """
    Process a single line of text from a file.
    
    Attempts to parse the line as JSON, or performs basic text analysis
    if it's not valid JSON.
    
    Args:
        line (str): The line of text to process
        
    Returns:
        dict: Information about the processed content
    """
    # Try to parse as JSON first
    try:
        data = json.loads(line)
        return {
            'type': 'json',
            'data': data,
            'wordCount': None,
            'charCount': len(line)
        }
    except json.JSONDecodeError:
        # Not JSON, perform basic text analysis
        words = line.split()
        return {
            'type': 'text',
            'data': line,
            'wordCount': len(words),
            'charCount': len(line)
        }