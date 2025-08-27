from concurrent import futures
from dataclasses import dataclass
from typing import Any, Callable, List, Sequence, Optional


def _submit_merge_when_ready(pool, left_fut, right_fut, merge_items):
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
    lvl: int


def reduce_submit_in_order(
    items: Sequence[Any],
    build_item: Callable[[Any], Any],
    merge_items: Callable[[Any, Any], Any],
    *,
    pool: futures.Executor,
    pbar: Optional["tqdm.tqdm"] = None,
    update_on: str = "always",  # "always" or "success"
) -> futures.Future:
    if not items:
        raise ValueError("items is empty")

    def _attach_progress(fut: futures.Future):
        if pbar is None:
            return

        def _inc(done: futures.Future):
            if update_on == "success":
                if done.exception() is None:
                    pbar.update(1)
            else:
                pbar.update(1)

        fut.add_done_callback(_inc)

    stack: List[_Node] = []
    it = iter(items)

    # submit first two leaves (if present), their merge, then continue
    for itm in it:
        leaf = pool.submit(lambda params: build_item(**params), itm)
        _attach_progress(leaf)
        stack.append(_Node(leaf, 0))
        # whenever top two share level, submit their merge
        while len(stack) >= 2 and stack[-1].lvl == stack[-2].lvl:
            r = stack.pop()
            l = stack.pop()
            m = _submit_merge_when_ready(pool, l.fut, r.fut, merge_items)
            stack.append(_Node(m, l.lvl + 1))

    # drain remaining nodes (handles odd counts)
    while len(stack) > 1:
        r = stack.pop()
        l = stack.pop()
        m = _submit_merge_when_ready(pool, l.fut, r.fut, merge_items)
        stack.append(_Node(m, max(l.lvl, r.lvl) + 1))

    return stack[0].fut
