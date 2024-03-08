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
cimport cython
from cpython cimport bool
from cpython.string cimport *
from libc.stddef cimport *
from libc.stdint cimport *
from libc.stdlib cimport *
from libc.string cimport *

cdef extern from "mtbl.h":
    ctypedef enum mtbl_res:
        mtbl_res_failure
        mtbl_res_success

    ctypedef enum mtbl_compression_type:
        MTBL_COMPRESSION_NONE
        MTBL_COMPRESSION_SNAPPY
        MTBL_COMPRESSION_ZLIB
        MTBL_COMPRESSION_LZ4
        MTBL_COMPRESSION_LZ4HC
        MTBL_COMPRESSION_ZSTD

    struct mtbl_iter:
        pass
    struct mtbl_source:
        pass
    struct mtbl_reader:
        pass
    struct mtbl_reader_options:
        pass
    struct mtbl_writer:
        pass
    struct mtbl_writer_options:
        pass
    struct mtbl_merger:
        pass
    struct mtbl_merger_options:
        pass
    struct mtbl_sorter:
        pass
    struct mtbl_sorter_options:
        pass

    ctypedef void (*mtbl_merge_func)(void *clos, uint8_t *, size_t, uint8_t *, size_t, uint8_t *, size_t, uint8_t **, size_t *)
    
    # iter
    void mtbl_iter_destroy(mtbl_iter **) nogil
    mtbl_res mtbl_iter_next(mtbl_iter *, uint8_t **, size_t *, uint8_t **, size_t *) nogil

    # source
    mtbl_iter *mtbl_source_iter(mtbl_source *) nogil
    mtbl_iter *mtbl_source_get(mtbl_source *, uint8_t *, size_t) nogil
    mtbl_iter *mtbl_source_get_range(mtbl_source *, uint8_t *, size_t, uint8_t *, size_t) nogil
    mtbl_iter *mtbl_source_get_prefix(mtbl_source *, uint8_t *, size_t) nogil
    mtbl_res mtbl_source_write(mtbl_source *, mtbl_writer *) nogil

    # reader
    mtbl_reader *mtbl_reader_init(char *, mtbl_reader_options *) nogil
    void mtbl_reader_destroy(mtbl_reader **) nogil
    mtbl_source *mtbl_reader_source(mtbl_reader *) nogil

    mtbl_reader_options *mtbl_reader_options_init() nogil
    void mtbl_reader_options_destroy(mtbl_reader_options **) nogil
    void mtbl_reader_options_set_verify_checksums(mtbl_reader_options *, bool) nogil

    # writer
    mtbl_writer *mtbl_writer_init(char *, mtbl_writer_options *) nogil
    void mtbl_writer_destroy(mtbl_writer **) nogil
    mtbl_res mtbl_writer_add(mtbl_writer *, uint8_t *, size_t, uint8_t *, size_t) nogil

    mtbl_writer_options *mtbl_writer_options_init() nogil
    void mtbl_writer_options_destroy(mtbl_writer_options **) nogil
    void mtbl_writer_options_set_compression(mtbl_writer_options *, mtbl_compression_type) nogil
    void mtbl_writer_options_set_block_size(mtbl_writer_options *, size_t) nogil
    void mtbl_writer_options_set_block_restart_interval(mtbl_writer_options *, size_t) nogil

    # merger
    mtbl_merger *mtbl_merger_init(mtbl_merger_options *) nogil
    void mtbl_merger_destroy(mtbl_merger **) nogil
    void mtbl_merger_add_source(mtbl_merger *, mtbl_source *) nogil
    mtbl_source *mtbl_merger_source(mtbl_merger *) nogil

    mtbl_merger_options *mtbl_merger_options_init() nogil
    void mtbl_merger_options_destroy(mtbl_merger_options **) nogil
    void mtbl_merger_options_set_merge_func(mtbl_merger_options *, mtbl_merge_func, void *) nogil

    # sorter
    mtbl_sorter *mtbl_sorter_init(mtbl_sorter_options *) nogil
    void mtbl_sorter_destroy(mtbl_sorter **) nogil
    mtbl_res mtbl_sorter_add(mtbl_sorter *, uint8_t *, size_t, uint8_t *, size_t) nogil
    mtbl_res mtbl_sorter_write(mtbl_sorter *, mtbl_writer *) nogil
    mtbl_iter *mtbl_sorter_iter(mtbl_sorter *) nogil

    mtbl_sorter_options *mtbl_sorter_options_init() nogil
    void mtbl_sorter_options_destroy(mtbl_sorter_options **) nogil
    void mtbl_sorter_options_set_merge_func(mtbl_sorter_options *, mtbl_merge_func, void *) nogil
    void mtbl_sorter_options_set_temp_dir(mtbl_sorter_options *, char *) nogil
    void mtbl_sorter_options_set_max_memory(mtbl_sorter_options *, size_t) nogil

    # varint
    unsigned mtbl_varint_length(uint64_t) nogil
    unsigned mtbl_varint_length_packed(uint8_t *, size_t) nogil
    size_t mtbl_varint_encode32(uint8_t *, uint32_t) nogil
    size_t mtbl_varint_encode64(uint8_t *, uint64_t) nogil
    size_t mtbl_varint_decode32(uint8_t *, uint32_t *) nogil
    size_t mtbl_varint_decode64(uint8_t *, uint64_t *) nogil
