#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(mymodule, m) {
    m.doc() = "My Python module"; // Optional module docstring

    m.def("my_function", []() {
        return "Hello, world!";
    }, "Return a greeting string");
}
