import functools
import inspect


class param_groups:
    def __init__(self, *, exclusive=None):
        if not isinstance(exclusive, (list, tuple)):
            raise TypeError("")
        # Check that it's a list of lists
        exclusive = [[x] if isinstance(x, str) else x for x in exclusive]

        self._exclusive = exclusive

    @staticmethod
    def _collect_args_kargs(func, args, kwargs):
        signature = inspect.signature(func)
        param_names = list(signature.parameters.keys())
        pos_args = {param_names[i]: arg for i, arg in enumerate(args)}

        # argspec = inspect.getargspec(func)
        # pos_args = {argspec.args[i]: arg for i, arg in enumerate(args)}
        return {**pos_args, **kwargs}

    def _check_param_groups(self, func, args, kwargs):
        all_args = self._collect_args_kargs(func, args, kwargs)
        all_args = [k for k, v in all_args.items() if v is not None]

        exclusives_present = [set(group).intersection(set(all_args)) for group in self._exclusive]

        # Ensure only one set of exclusives is present
        n_exclusive_groups = sum([len(x) > 0 for x in exclusives_present])
        if n_exclusive_groups == 0:
            raise TypeError(f"{func.__name__}() missing required groups: {self._exclusive}")

        if n_exclusive_groups > 1:
            raise TypeError(f"{func.__name__}() received mutually exclusive arguments: {exclusives_present}")

        # Ensure the present set is complete
        group_idx = [i for i, x in enumerate(exclusives_present) if len(x) > 0][0]
        group_args = exclusives_present[group_idx]
        group_expected = set(self._exclusive[group_idx])

        missing = group_expected - group_args
        if len(missing) > 0:
            raise TypeError(f"{func.__name__}() missing arguments {missing} from group {group_expected}")

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._check_param_groups(func, args, kwargs)

            return func(*args, **kwargs)

        return wrapper
