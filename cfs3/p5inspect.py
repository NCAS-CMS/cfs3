from pyfive.inspect import p5ncdump
from cfs3.s3core import get_user_config, Capturing
import s3fs
import logging

def p5view(alias, bucket, path, object, special=False, log_level=logging.WARNING):
    """ 
    Approximate the use of ncdump -h on the object at path in bucket
    
    Args:
        alias: S3 location alias
        bucket: S3 bucket name
        path: Path within bucket
        object: Object/file name
        special: Display special attributes (not yet implemented)
        log_level: Logging level to use (default: WARNING to suppress INFO logs)
    """
    MB = 2**20
    credentials = get_user_config(alias)
    storage_options = {
                'key':credentials['accessKey'],
                'secret':credentials['secretKey'],  
                'endpoint_url':credentials['url'],
                'default_cache_type':'readahead',
                'default_block_size': 1 * MB 
    }
    if path == '' or path=='/':
        bits = [bucket,object]
    else:
        bits = [bucket,path,object]

    file_uri = '/'.join(bits)

    fs = s3fs.S3FileSystem(**storage_options)

    log_capture = []
    pyfive_logger_states = {}
    
    # Only configure pyfive logging when we want to capture it
    if log_level <= logging.INFO:
        # Find all pyfive loggers and save their state
        for name in list(logging.Logger.manager.loggerDict.keys()):
            if name.startswith('pyfive'):
                logger = logging.getLogger(name)
                if isinstance(logger, logging.Logger):
                    pyfive_logger_states[name] = {
                        'level': logger.level,
                        'handlers': logger.handlers.copy(),
                        'propagate': logger.propagate
                    }
        
        # Create a handler that captures log messages
        class ListHandler(logging.Handler):
            def emit(self, record):
                log_capture.append(self.format(record))
        
        log_handler = ListHandler()
        log_handler.setLevel(log_level)
        log_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        
        # Configure all pyfive loggers to capture to our handler
        for name in pyfive_logger_states.keys():
            logger = logging.getLogger(name)
            logger.setLevel(log_level)
            logger.propagate = False
            logger.handlers.clear()
            logger.addHandler(log_handler)

    try:
        with Capturing() as output:
            with fs.open(file_uri) as s3file:
                p5ncdump(s3file, special=special)
           
    finally:
        # Restore pyfive logger states if we changed them
        if pyfive_logger_states:
            for name, state in pyfive_logger_states.items():
                logger = logging.getLogger(name)
                logger.handlers.clear()
                for handler in state['handlers']:
                    logger.addHandler(handler)
                logger.setLevel(state['level'])
                logger.propagate = state['propagate']
    
    return output, log_capture
