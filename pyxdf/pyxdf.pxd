import cython

# native replacements for potentially slow functions

cdef class StreamData:
    cdef readonly double tdiff, last_timestamp, srate
    cdef readonly int nchns, samplebytes
    cdef readonly fmt
    cdef public double effective_srate
    cdef public time_stamps, time_series,clock_times,clock_values,dtype, fmts


@cython.locals(filesize=cython.int, StreamID=cython.int,v=cython.Py_ssize_t[:],idx=cython.Py_ssize_t[:])
cpdef load_xdf(filename, on_chunk=*,bint synchronize_clocks=*,
             bint handle_clock_resets=*,
             bint dejitter_timestamps=*,
             double jitter_break_threshold_seconds=*,
             int jitter_break_threshold_samples=*,
             double clock_reset_threshold_seconds=*,
             double clock_reset_threshold_stds=*,
             double clock_reset_threshold_offset_seconds=*,
             double clock_reset_threshold_offset_stds=*,
             double winsor_threshold=*)

@cython.locals(nbytes=cython.bytes)
cpdef int _read_varlen_int(f) except 0

@cython.locals(k=cython.Py_ssize_t, stamps=cython.double[:])
cdef _read_chunk3(f, StreamData s)

