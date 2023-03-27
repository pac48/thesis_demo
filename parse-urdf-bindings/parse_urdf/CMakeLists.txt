find_package(pybind11 REQUIRED)

find_library(TINYXML2_LIB tinyxml2)
find_package(RL REQUIRED)


pybind11_add_module(_core _core/cpp_library.cpp)
target_include_directories(_core PRIVATE ${CMAKE_CURRENT_LIST_DIR}/_core)
include_directories(${Eigen3_INCLUDE_DIRS})

target_link_libraries(_core PUBLIC ${TINYXML2_LIB})
target_link_libraries(_core PUBLIC ${RL_LIBRARIES})


get_cmake_property(_variableNames VARIABLES)
list (SORT _variableNames)
foreach (_variableName ${_variableNames})
    message(STATUS "${_variableName}=${${_variableName}}")
endforeach()