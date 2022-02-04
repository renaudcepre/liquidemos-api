import functools
import time

from django.db import connection, reset_queries


def query_info(show_sql=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            reset_queries()

            start_queries_count = len(connection.queries)
            start = time.perf_counter()

            result = func(*args, **kwargs)

            end = time.perf_counter()

            end_queries = connection.queries
            end_queries_count = len(end_queries)

            print(f"for function \"{func.__name__}\":")
            queries_count = end_queries_count - start_queries_count
            print(
                f"{queries_count} {'queries' if queries_count > 1 else 'query'} performed.")
            if show_sql:
                for q in end_queries:
                    print(f"{q['time']}s - {q['sql']}")
            print(f"Total: {(end - start):.4f}s")
            return result

        return wrapper

    return decorator
