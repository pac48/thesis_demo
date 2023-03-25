#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "OBJ_Loader.h"

namespace py = pybind11;


void free_vector(void* ptr) {
    std::cerr << "freeing memory @ " << ptr << "\n";
    auto v = static_cast<std::vector<double>*>(ptr);
    delete v;
}

py::capsule make_vector_capsule(std::vector<double>* ptr) {
    py::capsule free_when_done(ptr, free_vector);
    return free_when_done;
}

std::pair<std::vector<double>*, py::capsule> allocateVector(){
    auto data = new std::vector<double>();
    auto capsule = make_vector_capsule(data);
    return {data, capsule};
}

std::tuple<py::array_t<double>> loadObj(std::string name) {
    auto data_pair = allocateVector();



    // Create a NumPy array from the data
    auto result = py::array_t<double>(data_pair.first->size(), data_pair.first->data(), data_pair.second);

    // Associate the vector with the NumPy array using a capsule

    return {result};

}

PYBIND11_MODULE(_core, m) {
    m.def("loadObj", &loadObj, "A function that loads a .obj file given name");
}
