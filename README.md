pymtbl: Python bindings for the mtbl sorted string table library
----------------------------------------------------------------

`pymtbl` provides a simple Pythonic wrapper for
[mtbl](https://github.com/farsightsec/mtbl)'s reader, writer, sorter, and
merger interfaces. The `examples/` directory contains scripts demonstrating
each of these interfaces. The following transcript shows the basic reader and
writer interfaces (nb. the traceback is expected behavior):

    >>> import mtbl
    >>> w = mtbl.writer('example.mtbl', compression=mtbl.COMPRESSION_SNAPPY)
    >>> w['key1'] = 'val1'
    >>> w['key17'] = 'val17'
    >>> w['key2'] = 'val2'
    >>> w['key23'] = 'val23'
    >>> w['key3'] = 'val3'
    >>> w['key4'] = 'val4'
    >>> w['key05'] = 'val05'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "mtbl.pyx", line 361, in mtbl.writer.__setitem__ (mtbl.c:4108)
    mtbl.KeyOrderError
    >>> w.close()
    >>> r = mtbl.reader('example.mtbl', verify_checksums=True)
    >>> for k,v in r.get_range('key19', 'key23'): print(k, v)
    ...
    'key2' 'val2'
    'key23' 'val23'
    >>> for k,v in r.get_prefix('key2'): print(k, v)
    ...
    'key2' 'val2'
    'key23' 'val23'
    >>> for k,v in r.iteritems(): print(k, v)
    ...
    'key1' 'val1'
    'key17' 'val17'
    'key2' 'val2'
    'key23' 'val23'
    'key3' 'val3'
    'key4' 'val4'
    >>>


In Python 3.x bytes() is a distinct type, whereas in Python 2.6 and 2.7 it is
simply an alias for str(). We now take strings and bytes as function
parameters. Note that if you pass in a byte string that can be UTF-8 decoded it
will be read back from the mtbl as a str.

For example:

```
import mtbl
w = mtbl.writer('example.mtbl', compression=mtbl.COMPRESSION_SNAPPY)
w[b'key0'] = b'val0'
w[b'key1'] = b'\x01'
w[b'key2'] = b'\x7e'
w[b'key3'] = b'\x80\x01'
w.close()

r = mtbl.reader('example.mtbl', verify_checksums=True)

assert r.get(b'key0') == ['val0']
# all the keys in this mtbl are strings because they can all be UTF-8 decoded
assert [type(k) for k in list(r.iterkeys())] == [str, str, str, str]
assert r.get('key1') == ['\x01']
assert r.get('key2') == ['~']
assert r.get('key3') == [b'\x80\x01'] # not a printable string so the value read back is bytes
```

If you want to disable this behavior and read the contents of the mtbl as bytes
then initialize your reader with `return_bytes=True`.

```
r = mtbl.reader('example.mtbl', verify_checksums=True, return_bytes=True)
```

If you want to store integers in your mtbl use varint_encode() and
varint_decode() or
[struct.pack](https://docs.python.org/3.9/library/struct.html#struct.pack) and
[struct.unpack](https://docs.python.org/3.9/library/struct.html#struct.pack) to
do so:

```
import mtbl
import struct

w = mtbl.writer('example.mtbl', compression=mtbl.COMPRESSION_SNAPPY)
w['key0'] = mtbl.varint_encode(2)
w['key1'] = mtbl.varint_encode(128)
w['key2'] = mtbl.varint_encode(98765432100)
w['key3'] = struct.pack('I', 123)
w.close()

r = mtbl.reader('example.mtbl', verify_checksums=True, return_bytes=True)

assert mtbl.varint_decode(r.get('key0')[0]) == 2
assert mtbl.varint_decode(r.get('key1')[0]) == 128
assert mtbl.varint_decode(r.get('key2')[0]) == 98765432100
assert struct.unpack('I', r.get('key3')[0])[0] == 123
```

Finally, scripts that used ord() to determine the value of a byte in a buffer
returned by this module under Python 2 will now need to test the data type.

For example, in pymtbl<=0.4.0 you might have written:

```
x = mtbl.varint_encode(1234)
first_byte = ord(x[0])
```

Now you would write:

```
x = mtbl.varint_encode(1234)
if type(x) == str: # py2
    first_byte = ord(x[0])
else: # py3
    first_byte = x[0]
```
