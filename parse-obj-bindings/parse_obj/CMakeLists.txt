find_package(pybind11 REQUIRED)

pybind11_add_module(_core _core/cpp_library.cpp)
target_include_directories(_core PRIVATE ${CMAKE_CURRENT_LIST_DIR}/_core)
