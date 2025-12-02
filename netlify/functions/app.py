import sys
import os
from io import BytesIO
import json

# Add parent directory to path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Initialize app before importing
os.environ.setdefault('FLASK_ENV', 'production')

try:
    from app import app, db, orchestrate_initial_setup
    
    # Initialize database on cold start
    with app.app_context():
        db.create_all()
        try:
            orchestrate_initial_setup()
        except Exception as e:
            print(f"Setup initialization error: {e}", file=sys.stderr)
except ImportError as e:
    print(f"Error importing app: {e}", file=sys.stderr)
    raise

def handler(event, context):
    """
    Netlify Functions handler for Flask app.
    Converts HTTP events to Flask WSGI requests.
    """
    try:
        # Extract request details from the event
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        query_string = event.get('queryStringParameters', {})
        body = event.get('body', '')
        
        # Handle base64 encoded body
        is_base64 = event.get('isBase64Encoded', False)
        if is_base64 and body:
            import base64
            body = base64.b64decode(body)
        elif isinstance(body, str):
            body = body.encode('utf-8')
        
        # Build query string
        if query_string and isinstance(query_string, dict):
            query_parts = [f"{k}={v}" for k, v in query_string.items()]
            query_string = "&".join(query_parts)
        elif not query_string:
            query_string = ""
        
        # Construct WSGI environ
        environ = {
            'REQUEST_METHOD': http_method,
            'SCRIPT_NAME': '',
            'PATH_INFO': path,
            'QUERY_STRING': query_string or '',
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': headers.get('content-length', str(len(body)) if body else '0'),
            'SERVER_NAME': headers.get('host', 'netlify.com').split(':')[0],
            'SERVER_PORT': '443',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Add headers to environ
        for header_name, header_value in headers.items():
            header_name = header_name.upper().replace('-', '_')
            if header_name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{header_name}'] = header_value
        
        # Capture response
        response_status = None
        response_headers = {}
        
        def start_response(status, headers_list, exc_info=None):
            nonlocal response_status, response_headers
            if exc_info:
                try:
                    if response_headers:
                        raise exc_info[1].with_traceback(exc_info[2])
                finally:
                    exc_info = None
            response_status = status
            response_headers = dict(headers_list)
            return lambda x: None  # write() function for legacy apps
        
        # Call Flask app
        try:
            response_data = app(environ, start_response)
            response_body = b''.join(response_data)
            
            # Close response if it has a close method
            if hasattr(response_data, 'close'):
                response_data.close()
        except Exception as e:
            print(f"Flask app error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'text/plain'},
                'body': f'Internal Server Error: {str(e)}'
            }
        
        # Extract status code
        status_code = int(response_status.split()[0]) if response_status else 500
        
        # Prepare response headers
        headers_dict = {}
        for k, v in response_headers.items():
            headers_dict[k] = v
        
        # Determine if response should be base64 encoded
        is_binary = False
        content_type = headers_dict.get('Content-Type', '')
        if any(x in content_type for x in ['image', 'audio', 'video', 'application/octet-stream']):
            is_binary = True
        
        # Format response
        response_body_str = response_body.decode('utf-8', errors='ignore') if response_body else ''
        
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': response_body_str,
            'isBase64Encoded': False
        }
        
    except Exception as e:
        print(f"Handler error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Internal Server Error: {str(e)}'
        }

