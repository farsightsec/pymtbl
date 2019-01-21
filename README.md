pymtbl: Python bindings for the mtbl sorted string table library
----------------------------------------------------------------

`pymtbl` provides a simple Pythonic wrapper for
[mtbl](https://github.com/farsightsec/mtbl)'s reader, writer, sorter, and
merger interfaces. The `examples/` directory contains scripts demonstrating
each of these interfaces. The following transcript shows the basic reader and
writer interfaces (nb. the traceback is expected behavior):

    >>> import mtbl
    >>> w = mtbl.writer('example.mtbl', compression=mtbl.COMPRESSION_SNAPPY)
    >>> w[b'key1'] = b'val1'
    >>> w[b'key17'] = b'val17'
    >>> w[b'key2'] = b'val2'
    >>> w[b'key23'] = b'val23'
    >>> w[b'key3'] = b'val3'
    >>> w[b'key4'] = b'val4'
    >>> w[b'key05'] = b'val05'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "mtbl.pyx", line 361, in mtbl.writer.__setitem__ (mtbl.c:4108)
    mtbl.KeyOrderError
    >>> w.close()
    >>> r = mtbl.reader('example.mtbl', verify_checksums=True)
    >>> for k,v in r.get_range(b'key19', b'key23'): print(k, v)
    ... 
    b'key2' b'val2'
    b'key23' b'val23'
    >>> for k,v in r.get_prefix(b'key2'): print(k, v)
    ... 
    b'key2' b'val2'
    b'key23' b'val23'
    >>> for k,v in r.iteritems(): print(k, v)
    ... 
    b'key1' b'val1'
    b'key17' b'val17'
    b'key2' b'val2'
    b'key23' b'val23'
    b'key3' b'val3'
    b'key4' b'val4'
    >>>


In Python 3.x bytes() is a distinct type, whereas in Python 2.6 and 2.7 
it is simply an alias for str(). We now take bytes as function parameters
instead of strings. This is done because, in Python 3, not all byte strings
can be encoded as printable strings and so accepting a str as a parameter was
not practical since mtbl is used, frequently, to store arbitrary byte data.

Scripts that used ord() to determine the value of a byte in a buffer returned
by this module under Python 2 will now need to test the data type. 

For example, in pymtbl<=0.4.0 you might have written:

```
x = mtbl.varint_encode(1234)
first_byte = ord(x[0])
```

Now you would write:

```
x = mtbl.varint_encode(1234)
if type(first_type) == str:  # py2
    first_byte = ord(x[0])
else:                        # py3
    first_byte = x[0]
```

Additionally, you must now pass in bytes to functions like
varint_encode and writer. Previously, you were able to write either
`w['key1'] = 'val1'` or `w[b'key1'] = b'val1'` because of Python 2's 
definition of bytes == str. Now you must write either

 `w[b'key1'] = b'val1'` 
 
 `w['key1'.encode()] = 'val1'.encode()`

While `w['key1'] = 'val1'` will continue to work when using Python 2, it will
*not* work when using Python 3 and so to maximize portability of your scripts, you 
should avoid that form.

If you intend to store strings, you should call encode() to ensure they
are stored with an encoding that you define.

References
----------

https://candide-guevara.github.io/article/python/2018/02/28/cython-memory-mgt.html
https://github.com/cython/cython/blob/master/tests/run/bytearray_coercion.pyx

