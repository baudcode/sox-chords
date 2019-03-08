from threading import Thread
import multiprocessing
import tqdm


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)

    def join(self):
        Thread.join(self)
        return self._return


def parallize_v2(f, args):
    threads = multiprocessing.cpu_count()
    return parallize(f, args, threads=threads)


def parallize(f, args, threads=None):
    """
        Args:
            - f: function
            - args: list or list(tuple), list when threads not None
    """
    if threads is not None:

        def parse_arg(arg):
            if type(arg) == list or type(arg) == set or type(arg) == tuple:
                return tuple(arg)
            else:
                return (arg, )

        results = []
        for i in tqdm.trange(0, len(args), threads):
            func_args = [parse_arg(arg) for arg in args[i:i + threads]]
            active_threads = [ThreadWithReturnValue(target=f, args=arg) for arg in func_args]
            [thread.start() for thread in active_threads]
            results += [thread.join() for thread in active_threads]
        return results
    else:
        active_threads = [ThreadWithReturnValue(target=f, args=arg) for arg in args]
        [thread.start() for thread in active_threads]
        return [thread.join() for thread in active_threads]
