#!/usr/bin/env python3
from __future__ import annotations
from concurrent import futures
from dataclasses import dataclass
from typing import Any, Callable, List, Sequence, Tuple


# --- helper: schedule a merge only after both inputs finish ---
def _submit_merge_when_ready(
    pool: futures.Executor,
    left_fut: futures.Future,
    right_fut: futures.Future,
    merge_items: Callable[[Any, Any], Any],
) -> futures.Future:
    out = futures.Future()
    scheduled = {"flag": False}

    def try_schedule(_=None):
        if scheduled["flag"] or out.done():
            return
        if left_fut.cancelled() or right_fut.cancelled():
            out.cancel()
            scheduled["flag"] = True
            return
        if left_fut.done() and right_fut.done():
            e = left_fut.exception() or right_fut.exception()
            if e is not None:
                out.set_exception(e)
                scheduled["flag"] = True
                return

            def run():
                try:
                    out.set_result(merge_items(left_fut.result(), right_fut.result()))
                except BaseException as ex:
                    out.set_exception(ex)

            scheduled["flag"] = True
            pool.submit(run)

    left_fut.add_done_callback(try_schedule)
    right_fut.add_done_callback(try_schedule)
    try_schedule()
    return out


@dataclass
class _Node:
    fut: futures.Future
    lvl: int  # 0 for leaves; +1 per merge


def reduce_submit_in_order(
    items: Sequence[Any],
    build_item: Callable[[Any], Any],  # takes a single item (params) -> obj
    merge_items: Callable[[Any, Any], Any],  # merges two objs -> obj
    *,
    pool: futures.Executor,
) -> futures.Future:
    """
    Submit jobs in strict binary-tree order:
      build 0, build 1, merge(0,1),
      build 2, build 3, merge(2,3),
      merge((0,1),(2,3)), ...
    Returns a Future for the final result. No worker ever blocks on another Future.
    """
    if not items:
        raise ValueError("items is empty")

    stack: List[_Node] = []

    # submit leaves one by one; whenever the top two have the same level, submit their merge
    for itm in items:
        leaf = pool.submit(lambda params: build_item(**params), itm)
        stack.append(_Node(leaf, 0))
        while len(stack) >= 2 and stack[-1].lvl == stack[-2].lvl:
            right = stack.pop()
            left = stack.pop()
            merged = _submit_merge_when_ready(pool, left.fut, right.fut, merge_items)
            stack.append(_Node(merged, left.lvl + 1))

    # drain remaining nodes to a single result (handles odd counts)
    while len(stack) > 1:
        right = stack.pop()
        left = stack.pop()
        merged = _submit_merge_when_ready(pool, left.fut, right.fut, merge_items)
        # level here is max+1 to keep it monotonic even if levels differ
        stack.append(_Node(merged, max(left.lvl, right.lvl) + 1))

    return stack[0].fut
