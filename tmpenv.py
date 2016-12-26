"""
supported call formats
    tmpenv(k1, v1, k2, v2, k3, v3, ...)
    + tmpenv((k1, v1), (k2, v2), (k3, v3), ...)
    + tmpenv([(k1, v1), (k2, v2), (k3, v3), ...])
    tmpenv(k1=v1, k2=v2, k3=v3, ...)
"""
import contextlib
import os
import pdb

@contextlib.contextmanager
def tmpenv(*a, **kw):
    def tputenv(k, v):
        try:
            tmpenv._s[k] = os.getenv(k)
        except AttributeError:
            tmpenv._s = {}
            tmpenv._s[k] = os.getenv(k)
        if tmpenv._s[k] is not None:
            del os.environ[k]
        os.environ[k] = v

    try:
        if hasattr(tmpenv, '_s'):
            del tmpenv._s
        tmpenv._s = {}
        if a:
            if type(a[0]) == tuple and 2 == len(a[0]):
                # tmpenv((k1, v1), (k2, v2), ...)
                for t in a:
                    if 2 != len(t):
                        raise StandardError("tuple wrong length: '%s'" % str(t))
                    tputenv(t[0], t[1])
            elif type(a[0]) == list and type(a[0][0]) == tuple:
                # tmpenv([(k1, v1), (k2, v2), ...])
                if 1 < len(a):
                    raise StandardError("unknown extra arguments: '%s'" % a[1:])
                for k, v in a[0]:
                    tputenv(k, v)
            elif 0 != len(a) % 2:
                raise StandardError("tmpenv expects an even number of arguments")
            else:
                # tmpenv(k1, v1, k2, v2, ...)
                for i in range(0, len(a), 2):
                    tputenv(a[i], a[i+1])

        if kw:
            for k in kw:
                tputenv(k, kw[k])

        yield

    finally:
        for k in tmpenv._s:
            if tmpenv._s[k] is not None:
                os.environ[k] = tmpenv._s[k]
            elif k in os.environ:
                del os.environ[k]
        del tmpenv._s
