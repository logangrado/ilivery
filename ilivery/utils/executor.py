#!/usr/bin/env python3

from concurrent import futures


class InlineExecutor:
    """Minimal executor that runs submit() inline and returns a Future."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def shutdown(self, wait=True):
        pass

    def submit(self, fn, *args, **kwargs):
        f = futures.Future()
        try:
            f.set_result(fn(*args, **kwargs))
        except BaseException as e:
            f.set_exception(e)
        return f


def make_executor(max_workers: int):
    # ThreadPoolExecutor requires >=1 workers; use Inline when <=1 or None
    if max_workers and max_workers > 1:
        return futures.ThreadPoolExecutor(max_workers=max_workers)
    return InlineExecutor()
