#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <stdexcept>
#include <sstream>

#include "OBJ_Loader.h"

namespace py = pybind11;


template<typename T>
void free_vector(void* ptr) {
    std::cout << "freeing memory @ " << ptr << "\n";
    auto v = static_cast<std::vector<T>*>(ptr);
    delete v;
}

template<typename T>
py::capsule make_vector_capsule(std::vector<T>* ptr) {
    py::capsule free_when_done(ptr, free_vector<T>);
    return free_when_done;
}

template<typename T>
std::pair<std::vector<T>*, py::capsule> allocateVector(int size=0){
    auto data = new std::vector<T>();
    data->assign(size, 0);
    auto capsule = make_vector_capsule(data);
    return {data, capsule};
}

std::vector<std::tuple<py::array_t<float>, py::array_t<float>, py::array_t<float>, py::array_t<float>> > loadObj(std::string fileName) {

    objl::Loader Loader;
    bool loadout = Loader.LoadFile(fileName);
    if (!loadout) {
        std::stringstream ss;
        ss << "Failed to load object, ensure " << fileName << " is on the path.\n";
        throw std::runtime_error(ss.str());
        return {};
    }

    auto out = std::vector<std::tuple<py::array_t<float>,py::array_t<float>,py::array_t<float>,py::array_t<float> >>();
    int numMeshes = Loader.LoadedMeshes.size();

    for (int i = 0; i < numMeshes; i++) {
        objl::Mesh curMesh = Loader.LoadedMeshes[i];
        int numVerts = curMesh.Vertices.size();
        int numPoints = curMesh.Positions.size();
        int numInds = curMesh.Indices.size();
        std::string objName = curMesh.MeshName;

        auto pointsP = allocateVector<float>(3 * numPoints);
        auto verticesPositionsP = allocateVector<float>(3 * numVerts);
        auto verticesNormalsP = allocateVector<float>(3 * numVerts);
        auto verticesTextureCoordinatesP = allocateVector<float>(2 * numVerts);

        auto & points = *pointsP.first;
        auto & verticesPositions = *verticesPositionsP.first;
        auto & verticesNormals = *verticesNormalsP.first;
        auto & verticesTextureCoordinates = *verticesTextureCoordinatesP.first;

        // Copy one of the loaded meshes to be our current mesh

        for (int j = 0; j < numPoints; j++) {
            points[j] = curMesh.Positions[j].X;
            points[j + numPoints] = curMesh.Positions[j].Y;
            points[j + 2 * numPoints] = curMesh.Positions[j].Z;
        }

        for (int j = 0; j < numVerts; j++) {
            verticesPositions[j] = curMesh.Vertices[j].Position.X;
            verticesPositions[j + numVerts] = curMesh.Vertices[j].Position.Y;
            verticesPositions[j + 2 * numVerts] = curMesh.Vertices[j].Position.Z;

            verticesNormals[j] = curMesh.Vertices[j].Normal.X;
            verticesNormals[j + numVerts] = curMesh.Vertices[j].Normal.Y;
            verticesNormals[j + 2 * numVerts] = curMesh.Vertices[j].Normal.Z;

            verticesTextureCoordinates[j] = curMesh.Vertices[j].TextureCoordinate.X;
            verticesTextureCoordinates[j + numVerts] = curMesh.Vertices[j].TextureCoordinate.Y;
        }

        auto pointsArr = py::array_t<float>(pointsP.first->size(), pointsP.first->data(), pointsP.second);
        auto verticesPositionsArr = py::array_t<float>(verticesPositionsP.first->size(), verticesPositionsP.first->data(), verticesPositionsP.second);
        auto verticesNormalsArr = py::array_t<float>(verticesNormalsP.first->size(), verticesNormalsP.first->data(), verticesNormalsP.second);
        auto verticesTextureCoordinatesArr = py::array_t<float>(verticesTextureCoordinatesP.first->size(), verticesTextureCoordinatesP.first->data(), verticesTextureCoordinatesP.second);

        out.push_back({pointsArr, verticesPositionsArr, verticesNormalsArr, verticesTextureCoordinatesArr});
      }


    return out;
}

PYBIND11_MODULE(_core, m) {
    m.def("loadObj", &loadObj, "A function that loads a .obj file given name");
}
