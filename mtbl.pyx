#cython: embedsignature=True
#cython: language_level=2
# Copyright (c) 2024 DomainTools LLC
# Copyright (c) 2015-2019 by Farsight Security, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
include "mtbl.pxi"
import threading

DEFAULT_SORTER_TEMP_DIR = '/var/tmp'
DEFAULT_SORTER_MEMORY = 1073741824

COMPRESSION_NONE = MTBL_COMPRESSION_NONE
COMPRESSION_SNAPPY = MTBL_COMPRESSION_SNAPPY
COMPRESSION_ZLIB = MTBL_COMPRESSION_ZLIB
COMPRESSION_LZ4 = MTBL_COMPRESSION_LZ4
COMPRESSION_LZ4HC = MTBL_COMPRESSION_LZ4HC
COMPRESSION_ZSTD = MTBL_COMPRESSION_ZSTD

class KeyOrderError(Exception):
    pass

class TableClosedException(Exception):
    pass

class UnknownCompressionTypeException(Exception):
    pass

class UninitializedException(Exception):
    pass

class VarintDecodingError(Exception):
    pass

ImmutableError = TypeError('object does not support mutation')

def to_bytes(value):
    """
    to_bytes(v) -> return a bytes object from a bytes, str, and bytearray; raises a ValueError if the conversion fails
    """
    # bytes needs to be before str because in py2 str is already bytes
    if isinstance(value, bytes):
        b = value
    elif isinstance(value, str):
        b = value.encode()
    elif isinstance(value, bytearray):
        b = bytes(value)
    else:
        raise ValueError('Only str, bytes, and bytearrays are allowed.')
    return b

def from_bytes(bytes value, bool return_bytes=False):
    """
    from_bytes(v) -> given bytes returns str by UTF-8 decoding it. returns the bytes unchanged if decoding
    fails

    Keyword arguments:
    return_bytes -- whether to return data as bytes without attempting to convert it to str (default False)
    """
    if return_bytes:
        return value

    if isinstance(value, str): #py2
        v = value
    else: #py3
        try:
            v = value.decode('utf-8')
        except UnicodeDecodeError:
            v = value
    return v

def varint_length(uint64_t value):
    """varint_length(v) -> number of bytes the integer v would require in varint encoding."""
    return mtbl_varint_length(value)

def varint_length_packed(py_buf):
    """varint_length_packed(b) -> number of varint-packed bytes at the start of b."""
    cdef uint8_t *buf
    cdef Py_ssize_t len_buf
    cdef size_t sz
    len_buf = len(py_buf)
    py_buf = to_bytes(py_buf)
    buf = py_buf
    with nogil:
        sz = mtbl_varint_length_packed(buf, len_buf)
    if sz == 0:
        raise VarintDecodingError
    return sz

def varint_encode(long v):
    """varint_encode(v) -> encode integer v using packed variable-width encoding."""
    cdef uint8_t buf[10]
    cdef size_t sz
    with nogil:
        sz = mtbl_varint_encode64(buf, v)
    rv = buf[:sz]
    return <bytes> buf[:sz]

def varint_decode(py_buf):
    """varint_decode(b) -> decode variable-width packed integer from b"""
    cdef uint64_t val
    cdef const uint8_t *buf
    cdef Py_ssize_t len_buf
    cdef size_t bytes_read

    # This allows the function to accept strings like '\x01' to '\x7f' in py3
    py_buf = to_bytes(py_buf)

    buf = <uint8_t *> py_buf
    len_buf = len(py_buf)
    if mtbl_varint_length_packed(buf, len_buf) == 0:
        raise VarintDecodingError
    with nogil:
        mtbl_varint_decode64(buf, &val)
    return val

@cython.internal
cdef class iterkeys(object):
    cdef mtbl_iter *_instance
    cdef object _parent
    cdef bool return_bytes

    def __cinit__(self):
        self._instance = NULL

    def __init__(self, object _parent, bool return_bytes=False):
        self._parent = _parent
        self.return_bytes = return_bytes

    def __dealloc__(self):
        with nogil:
            mtbl_iter_destroy(&self._instance)

    def __iter__(self):
        return self

    def __next__(self):
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef const uint8_t *val
        cdef size_t len_key
        cdef size_t len_val

        if self._instance == NULL:
            raise StopIteration

        with nogil:
            res = mtbl_iter_next(self._instance, &key, &len_key, &val, &len_val)
        if res == mtbl_res_failure:
            raise StopIteration

        return from_bytes(key[:len_key], self.return_bytes)
@cython.internal
cdef class itervalues(object):
    cdef mtbl_iter *_instance
    cdef object _parent
    cdef bool return_bytes

    def __cinit__(self):
        self._instance = NULL

    def __init__(self, object _parent, bool return_bytes=False):
        self._parent = _parent
        self.return_bytes = return_bytes

    def __dealloc__(self):
        with nogil:
            mtbl_iter_destroy(&self._instance)

    def __iter__(self):
        return self

    def __next__(self):
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef const uint8_t *val
        cdef size_t len_key
        cdef size_t len_val

        if self._instance == NULL:
            raise StopIteration

        with nogil:
            res = mtbl_iter_next(self._instance, &key, &len_key, &val, &len_val)
        if res == mtbl_res_failure:
            raise StopIteration
        return from_bytes(val[:len_val], self.return_bytes)

@cython.internal
cdef class iteritems(object):
    cdef mtbl_iter *_instance
    cdef object _parent
    cdef bool return_bytes

    def __cinit__(self):
        self._instance = NULL

    def __init__(self, object _parent, bool return_bytes=False):
        self._parent = _parent
        self.return_bytes = return_bytes

    def __dealloc__(self):
        with nogil:
            mtbl_iter_destroy(&self._instance)

    def __iter__(self):
        return self

    def __next__(self):
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef const uint8_t *val
        cdef size_t len_key
        cdef size_t len_val

        if self._instance == NULL:
            raise StopIteration

        with nogil:
            res = mtbl_iter_next(self._instance, &key, &len_key, &val, &len_val)

        if res == mtbl_res_failure:
            raise StopIteration

        return (from_bytes(key[:len_key], self.return_bytes), from_bytes(val[:len_val], self.return_bytes))

cdef get_iterkeys(parent, mtbl_iter *instance, bool return_bytes=False):
    it = iterkeys(parent, return_bytes)
    it._instance = instance
    return it

cdef get_itervalues(parent, mtbl_iter *instance, bool return_bytes=False):
    it = itervalues(parent, return_bytes)
    it._instance = instance
    return it

cdef get_iteritems(parent, mtbl_iter *instance, bool return_bytes=False):
    it = iteritems(parent, return_bytes)
    it._instance = instance
    return it

@cython.internal
cdef class DictMixin(object):
    def __iter__(self):
        return self.iterkeys()

    def iter(self):
        return self.iterkeys()

    def items(self):
        """D.items() -> list of D's (key, value) pairs, as 2-tuples"""
        return [ (k, v) for k, v in self.iteritems() ]

    def keys(self):
        """D.keys() -> list of D's keys"""
        return [ k for k in self.iterkeys() ]

    def values(self):
        """D.values() -> list of D's values"""
        return [ v for v in self.itervalues() ]

    def __delitem__(self, key):
        """will raise ImmutableError"""
        raise ImmutableError

    def __setitem__(self, key, value):
        """will raise ImmutableError"""
        raise ImmutableError

    def pop(self, *a, **b):
        """will raise ImmutableError"""
        raise ImmutableError

    def popitem(self):
        """will raise ImmutableError"""
        raise ImmutableError

    def update(self, *a, **b):
        """will raise ImmutableError"""
        raise ImmutableError

cdef class reader(DictMixin):
    """
    reader(fname) -> new MTBL reader initialized from file fname

    Keyword arguments:
    verify_checksums -- whether to verify data block checksums (default False)
    return_bytes -- whether to return data as bytes without attempting to convert it to str (default False)
    """
    cdef mtbl_reader *_instance
    cdef bool return_bytes

    def __cinit__(self):
        self._instance = NULL

    def __dealloc__(self):
        with nogil:
            mtbl_reader_destroy(&self._instance)

    def __init__(self, str fname, bool verify_checksums=False, bool return_bytes=False):
        cdef mtbl_reader_options *opt
        cdef bytes tfn_bytes = fname.encode('utf-8')
        cdef char *tfn = tfn_bytes
        self.return_bytes = return_bytes

        with nogil:
            opt = mtbl_reader_options_init()
            mtbl_reader_options_set_verify_checksums(opt, verify_checksums)
            self._instance = mtbl_reader_init(tfn, opt)
            mtbl_reader_options_destroy(&opt)

        if (self._instance == NULL):
            raise IOError("unable to open file: '%s'" % fname)

    cdef check_initialized(self):
        if self._instance == NULL:
            raise UninitializedException

    def iterkeys(self):
        """R.iterkeys() -> an iterator over the keys of R."""
        self.check_initialized()
        return get_iterkeys(self, mtbl_source_iter(mtbl_reader_source(self._instance)), self.return_bytes)

    def itervalues(self):
        """R.itervalues() -> an iterator over the values of R."""
        self.check_initialized()
        return get_itervalues(self, mtbl_source_iter(mtbl_reader_source(self._instance)), self.return_bytes)

    def iteritems(self):
        """R.iteritems() -> an iterator over the (key, value) items of R."""
        self.check_initialized()
        return get_iteritems(self, mtbl_source_iter(mtbl_reader_source(self._instance)), self.return_bytes)

    def __contains__(self, py_key):
        """R.__contains__(k) -> True if R has a key k, else False"""
        try:
            self.__getitem__(py_key)
            return True
        except KeyError:
            pass
        return False

    def has_key(self, py_key):
        """R.has_key(k) -> True if R has a key k, else False."""
        return self.__contains__(py_key)

    def get(self, py_key, default=None):
        """R.get(k[,d]) -> R[k] if k in R, else d.  d defaults to None."""
        try:
            return self.__getitem__(py_key)
        except KeyError:
            pass
        return default

    def get_range(self, py_key0, py_key1):
        """
        R.get_range(key0, key1) -> an iterator over all (key, value) items in R where key is
        between key0 and key1 inclusive.
        """
        cdef mtbl_res res
        cdef const uint8_t *key0
        cdef const uint8_t *key1
        cdef size_t len_key0
        cdef size_t len_key1

        self.check_initialized()

        t = to_bytes(py_key0)
        key0 = <uint8_t *> t
        len_key0 = len(t)
        t = to_bytes(py_key1)
        key1 = <uint8_t *> t
        len_key1 = len(t)

        return get_iteritems(self, mtbl_source_get_range(
            mtbl_reader_source(self._instance), key0, len_key0, key1, len_key1), self.return_bytes)

    def get_prefix(self, py_key):
        """
        R.get_prefix(key_prefix) -> an iterator over all (key, value) items in R where key
        begins with key_prefix.
        """
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef size_t len_key

        self.check_initialized()

        t = to_bytes(py_key)
        key = <uint8_t *> t
        len_key = len(t)

        return get_iteritems(self, mtbl_source_get_prefix(
            mtbl_reader_source(self._instance), key, len_key), self.return_bytes)

    def __getitem__(self, py_key):
        cdef mtbl_iter *it
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef const uint8_t *val
        cdef size_t len_key
        cdef size_t len_val

        self.check_initialized()

        t = to_bytes(py_key)
        key = <uint8_t *> t
        len_key = len(t)

        items = []
        with nogil:
            it = mtbl_source_get(mtbl_reader_source(self._instance), key, len_key)
        if it == NULL:
            raise KeyError(py_key)
        while True:
            with nogil:
                res = mtbl_iter_next(it, &key, &len_key, &val, &len_val)
            if res == mtbl_res_failure:
                break
            items.append(from_bytes(val[:len_val], self.return_bytes))
        with nogil:
            mtbl_iter_destroy(&it)
        if not items:
            raise KeyError(py_key)
        return items

cdef class writer(object):
    """
    writer(fname) -> new MTBL writer, output to file fname

    Keyword arguments:
    compression -- compression type (default COMPRESSION_NONE)
    block_size -- maximum data block size in bytes (default 8192)
    block_restart_interval -- how frequently to restart key prefix compression (default 16)
    """
    cdef mtbl_writer *_instance
    cdef _lock

    def __cinit__(self):
        self._instance = NULL

    def __dealloc__(self):
        with nogil:
            mtbl_writer_destroy(&self._instance)

    def __init__(self,
            str fname,
            mtbl_compression_type compression=COMPRESSION_NONE,
            size_t block_size=8192,
            size_t block_restart_interval=16):
        if not (compression == COMPRESSION_NONE or
                compression == COMPRESSION_SNAPPY or
                compression == COMPRESSION_ZLIB or
                compression == COMPRESSION_LZ4 or
                compression == COMPRESSION_LZ4HC or
                compression == COMPRESSION_ZSTD):
            raise UnknownCompressionTypeException

        self._lock = threading.Semaphore()

        cdef bytes tfn_bytes = fname.encode('utf-8')
        cdef char *tfn = tfn_bytes
        cdef mtbl_writer_options *opt

        with nogil:
            opt = mtbl_writer_options_init()
            mtbl_writer_options_set_compression(opt, compression)
            mtbl_writer_options_set_block_size(opt, block_size)
            mtbl_writer_options_set_block_restart_interval(opt, block_restart_interval)
            self._instance = mtbl_writer_init(tfn, opt)
            mtbl_writer_options_destroy(&opt)
        if self._instance == NULL:
            raise IOError("unable to initialize file: '%s'" % fname)

    def close(self):
        """W.close() -- finalize and close the writer"""
        with self._lock:
            with nogil:
                mtbl_writer_destroy(&self._instance)

    def __setitem__(self, py_key, py_val):
        """
        W.__setitem__(key, value) <==> W[key] = value

        Adds a new (key, value) entry to the writer. key and value must be byte
        strings, and key must be lexicographically greater than any previously
        written key.
        """
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef const uint8_t *val
        cdef size_t len_key
        cdef size_t len_val

        if self._instance == NULL:
            raise TableClosedException

        py_key = to_bytes(py_key)
        py_val = to_bytes(py_val)

        key = <uint8_t *> py_key
        val = <uint8_t *> py_val
        len_key = len(py_key)
        len_val = len(py_val)

        with self._lock:
            with nogil:
                res = mtbl_writer_add(self._instance, key, len_key, val, len_val)

        if res == mtbl_res_failure:
            raise KeyOrderError

    def __delitem__(self, key):
        """will raise ImmutableError"""
        raise ImmutableError

cdef void merge_func_wrapper(void *clos,
        uint8_t *key, size_t len_key,
        uint8_t *val0, size_t len_val0,
        uint8_t *val1, size_t len_val1,
        uint8_t **merged_val, size_t *len_merged_val) with gil:
    cdef bytes py_key
    cdef bytes py_val0
    cdef bytes py_val1
    cdef bytes py_merged_val
    py_key = key[:len_key]
    py_val0 = val0[:len_val0]
    py_val1 = val1[:len_val1]

    py_merged_val = (<object> clos)(py_key, py_val0, py_val1)
    len_merged_val[0] = <size_t> len(py_merged_val)
    merged_val[0] = <uint8_t *> malloc(len_merged_val[0])
    t = py_merged_val
    memcpy(merged_val[0], <uint8_t *>py_merged_val, len_merged_val[0])

cdef class merger(object):
    """
    merger(merge_func) -> new MTBL merger

    merge_func is the user-supplied value merging function:

        merge_func(key, val0, val1) -> merged_val

    all parameters are byte strings, and the return value must be a byte string.
    """
    cdef mtbl_merger *_instance
    cdef set _references
    cdef _lock
    cdef object merge_func
    cdef bool return_bytes

    def __cinit__(self):
        self._instance = NULL

    def __dealloc__(self):
        with nogil:
            mtbl_merger_destroy(&self._instance)

    def __init__(self, object merge_func, bool return_bytes=False):
        cdef mtbl_merger_options *opt
        self.merge_func = merge_func
        opt = mtbl_merger_options_init()
        mtbl_merger_options_set_merge_func(opt,
                                           <mtbl_merge_func> merge_func_wrapper,
                                           <void *> merge_func)
        self._instance = mtbl_merger_init(opt)
        mtbl_merger_options_destroy(&opt)
        self._references = set()
        self._lock = threading.Semaphore()
        self.return_bytes = return_bytes

    def add_reader(self, reader r):
        """M.add_reader(mtbl.reader) -- add a reader object as a merge input"""
        with self._lock:
            with nogil:
                mtbl_merger_add_source(self._instance, mtbl_reader_source(r._instance))
        self._references.add(r)

    def write(self, writer w):
        """M.write(mtbl.writer) -- dump merged output to writer"""
        cdef mtbl_res res

        with w._lock:
            with nogil:
                res = mtbl_source_write(mtbl_merger_source(self._instance), w._instance)
        if res != mtbl_res_success:
            raise RuntimeError

    def __iter__(self):
        return self.iterkeys()

    def iterkeys(self):
        """M.iterkeys() -> an iterator over the merged keys of M."""
        return get_iterkeys(self, mtbl_source_iter(mtbl_merger_source(self._instance)), self.return_bytes)

    def itervalues(self):
        """M.itervalues() -> an iterator over the merged values of M."""
        return get_itervalues(self, mtbl_source_iter(mtbl_merger_source(self._instance)), self.return_bytes)

    def iteritems(self):
        """M.iteritems() -> an iterator over the merged (key, value) items of M."""
        return get_iteritems(self, mtbl_source_iter(mtbl_merger_source(self._instance)), self.return_bytes)

    def get(self, bytes py_key):
        """
        M.get(key) -> an iterator over all (key, value) items in M which match key.
        """
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef size_t len_key

        t = py_key
        key = <uint8_t *> t
        len_key = len(py_key)

        return get_iteritems(self,
                mtbl_source_get(mtbl_merger_source(self._instance), key, len_key), self.return_bytes)

    def get_range(self, bytes py_key0, bytes py_key1):
        """
        M.get_range(key0, key1) -> an iterator over all (key, value) items in M where key is
        between key0 and key1 inclusive.
        """
        cdef mtbl_res res
        cdef const uint8_t *key0
        cdef const uint8_t *key1
        cdef size_t len_key0
        cdef size_t len_key1

        t = py_key0
        key0 = <uint8_t *> t
        t = py_key1
        key1 = <uint8_t *> t
        len_key0 = len(py_key0)
        len_key1 = len(py_key1)

        return get_iteritems(self, mtbl_source_get_range(
            mtbl_merger_source(self._instance), key0, len_key0, key1, len_key1), self.return_bytes)

    def get_prefix(self, bytes py_key):
        """
        M.get_prefix(key_prefix) -> an iterator over all (key, value) items in M where key
        begins with key_prefix.
        """
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef size_t len_key

        t = py_key
        key = <uint8_t *> t
        len_key = len(py_key)

        return get_iteritems(self, mtbl_source_get_prefix(
            mtbl_merger_source(self._instance), key, len_key), self.return_bytes)

cdef class sorter(object):
    """
    sorter(merge_func) -> new MTBL sorter

    merge_func is the user-supplied value merging function:

        merge_func(key, val0, val1) -> merged_val

    all parameters are byte strings, and the return value must be a byte string.

    Keyword arguments:
    temp_dir -- temporary directory (default "/var/tmp")
    max_memory -- maxmimum amount of memory for in-memory sorting in bytes (default 1 GB)
    """
    cdef mtbl_sorter *_instance
    cdef _lock
    cdef bool return_bytes

    def __cinit__(self):
        self._instance = NULL

    def __dealloc__(self):
        with nogil:
            mtbl_sorter_destroy(&self._instance)

    def __init__(self,
                 object merge_func,
                 str temp_dir=DEFAULT_SORTER_TEMP_DIR,
                 size_t max_memory=DEFAULT_SORTER_MEMORY,
                 bool return_bytes=False):
        cdef mtbl_sorter_options *opt
        self._lock = threading.Semaphore()

        with nogil:
            opt = mtbl_sorter_options_init()

        mtbl_sorter_options_set_merge_func(opt,
                                           <mtbl_merge_func> merge_func_wrapper,
                                           <void *> merge_func)

        mtbl_sorter_options_set_temp_dir(opt, temp_dir.encode('utf-8'))
        mtbl_sorter_options_set_max_memory(opt, max_memory)
        with nogil:
            self._instance = mtbl_sorter_init(opt)
            mtbl_sorter_options_destroy(&opt)
        self.return_bytes = return_bytes

    def write(self, writer w):
        """S.write(mtbl.writer) -- dump sorted output to writer"""
        cdef mtbl_res res

        with w._lock:
            with nogil:
                res = mtbl_sorter_write(self._instance, w._instance)
        if res != mtbl_res_success:
            raise RuntimeError

    def __setitem__(self, py_key, py_val):
        """
        S.__setitem__(key, value) <==> S[key] = value

        Adds a new (key, value) item to the sorter. If the key already exists,
        the user-supplied merge function will be called to merge the
        conflicting values.
        """
        cdef mtbl_res res
        cdef const uint8_t *key
        cdef const uint8_t *val
        cdef size_t len_key
        cdef size_t len_val

        if self._instance == NULL:
            raise RuntimeError

        py_key = to_bytes(py_key)
        py_val = to_bytes(py_val)

        t = py_key
        key = <uint8_t *> t
        t = py_val
        val = <uint8_t *> t
        len_key = len(py_key)
        len_val = len(py_val)

        with self._lock:
            with nogil:
                res = mtbl_sorter_add(self._instance, key, len_key, val, len_val)
        if res == mtbl_res_failure:
            raise KeyOrderError

    def __delitem__(self, key):
        """will raise ImmutableError"""
        raise ImmutableError

    def __iter__(self):
        return self.iterkeys()

    def iterkeys(self):
        """S.iterkeys() -> an iterator over the sorted keys of R."""
        return get_iterkeys(self, mtbl_sorter_iter(self._instance), self.return_bytes)

    def itervalues(self):
        """S.itervalues() -> an iterator over the sorted values of R."""
        return get_itervalues(self, mtbl_sorter_iter(self._instance), self.return_bytes)

    def iteritems(self):
        """S.iteritems() -> an iterator over the sorted (key, value) items of R."""
        return get_iteritems(self, mtbl_sorter_iter(self._instance), self.return_bytes)
