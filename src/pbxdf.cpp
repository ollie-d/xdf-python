#include <cstdint>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

/*
 * The XDF format isn't very friendly towards interpreted languages
 * the data can't be read with vectorized functions (np.frombuffer et al)
 * This Python module provides compiled functions that provide a 3-12x speedup
 */

// Convenience class to extract variables from a char* array
struct binreader {
	char *ptr, *end;
	binreader(char* data, std::size_t length) : ptr(data), end(data + length) {}
	
	// istream-like extraction
	template <typename T> binreader& operator>>(T& val) {
		if ((ptr + sizeof(T)) > end) throw std::runtime_error("Reading past end of data!");
		memcpy(&val, ptr, sizeof(val));
		ptr += sizeof(val);
		return *this;
	}
	// get a value and advance the current position
	template <typename T> T get() {
		T val;
		*this >> val;
		return val;
	}
	template <char> char get() {
		if (ptr == end) throw std::runtime_error("Reading past end of data!");
		return *ptr++;
	}
};

template <typename T>
int read_tag3(char* data, size_t length, py::array_t<double> ts_, py::array_t<T> vals,
              double last_ts, double srate) {
	if (vals.ndim() != 2) throw std::runtime_error("vals needs to be a samples x channels array");
	const auto nsamples = vals.shape(0), nchans = vals.shape(1);
	if (ts_.shape(0) != nsamples)
		throw std::runtime_error(
		    "The timestamp array needs to have the same number of rows as the value array!");
	if(ts_.shape(0) + vals.shape(0)*vals.shape(1)*sizeof(T) > length)
		throw std::runtime_error("input data is too short for the requested values!");
	
	binreader in(data, length);

	auto ts = ts_.mutable_unchecked<1>();
	auto datavec = vals.mutable_unchecked();

	int samples_since_last_real_timestamp = 0;

	for (uint sample = 0; sample < nsamples; sample++) {
		// is there a timestamp for the sample?
		if (in.get<char>()) {
			samples_since_last_real_timestamp = 0;
			last_ts = ts(sample) = in.get<double>();
		} else {
			samples_since_last_real_timestamp++;
			ts(sample) = last_ts + samples_since_last_real_timestamp / srate;
		}
		for (uint chan = 0; chan < nchans; ++chan) datavec(sample, chan) = in.get<T>();
	}
	return in.ptr - in.end;
}

PYBIND11_MODULE(pbxdf, m) {
	m.doc() = "pyxdf helpers"; // optional module docstring
	m.def("read_tag3_b", read_tag3<int8_t>, "Read char tag 3 data");
	m.def("read_tag3_h", read_tag3<int16_t>, "Read short tag 3 data");
	m.def("read_tag3_i", read_tag3<int32_t>, "Read int tag 3 data");
	m.def("read_tag3_q", read_tag3<int64_t>, "Read int64 tag 3 data");
	m.def("read_tag3_f", read_tag3<float>, "Read float tag 3 data");
	m.def("read_tag3_d", read_tag3<double>, "Read double tag 3 data");
}
