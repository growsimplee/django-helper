import traceback
import time
import logging
from .settings import ERROR_QUEUE, SERVICE_NAME, AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY, AWS_REGION, ERROR_CODES
import boto3
import json
import json
from functools import lru_cache,wraps

logger  = logging.getLogger("django")

def base_handler(func,error_handler,completion_handler):
        def execution(*args,**kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                end = time.time()
                completion_handler(end,start)
            except Exception as e :
                result = error_handler(traceback.format_exc(),e,args,kwargs)
            return result
        
        return execution

def gs_task(task_id):
    def error_handler(traceback, exception,args,kwargs):
        logger.error(f"error in {task_id} with input {args},{kwargs} -> {exception} | traceback {traceback}")
        sqs = boto3.resource('sqs', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY )
        queue2 = sqs.get_queue_by_name(QueueName=ERROR_QUEUE)
        data = {
            "service" : SERVICE_NAME,
            "task" : task_id,
            "time": str(time.time()),
            "exception" : str(exception),
            "traceback" : traceback, 
            "input": f"{args},{kwargs}"
        }
        response = queue2.send_message(MessageBody=json.dumps(data),MessageGroupId=SERVICE_NAME,  MessageAttributes={'errorType': {"StringValue":f"{SERVICE_NAME}","DataType":"String"}})
        return {"success":False,"exception" : str(exception), "code": ERROR_CODES.get(type(exception).__name__,50000)}

    def completion_handler(end,start):
        logger.info(f"{task_id} execution completed in {(end-start)*1000} ms")
    
    def base_wrapper(func):
        return base_handler(func,error_handler,completion_handler)

    return base_wrapper

def simple_gs_cache(maxsize):
    def hashable_lru(func):
        cache = lru_cache(maxsize=maxsize)

        def deserialise(value):
            try:
                return json.loads(value)
            except Exception:
                return value

        def func_with_serialized_params(*args, **kwargs):
            _args = tuple([deserialise(arg) for arg in args])
            _kwargs = {k: deserialise(v) for k, v in kwargs.items()}
            return func(*_args, **_kwargs)

        cached_function = cache(func_with_serialized_params)

        @wraps(func)
        def lru_decorator(*args, **kwargs):
            _args = tuple([json.dumps(arg, sort_keys=True) if type(arg) in (list, dict) else arg for arg in args])
            _kwargs = {k: json.dumps(v, sort_keys=True) if type(v) in (list, dict) else v for k, v in kwargs.items()}
            return cached_function(*_args, **_kwargs)
        lru_decorator.cache_info = cached_function.cache_info
        lru_decorator.cache_clear = cached_function.cache_clear
        return lru_decorator
    
    return hashable_lru

