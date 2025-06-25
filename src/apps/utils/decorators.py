import asyncio
import functools
from time import time


def rate_limited(max_requests_per_minute: int):
	request_delay = 60 / max_requests_per_minute
	last_request_time = 0

	def decorator(func):
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			nonlocal last_request_time
			current_time = time()
			time_since_last_request = current_time - last_request_time

			if time_since_last_request < request_delay:
				await asyncio.sleep(request_delay - time_since_last_request)
			
			last_request_time = time()
			return await func(*args, **kwargs)
		
		return wrapper
	return decorator