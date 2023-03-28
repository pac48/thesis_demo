#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <stdexcept>

#define _USE_MATH_DEFINES
#include <cmath>
#include "vector"
#include "rl/math/Transform.h"
#include "rl/math/Unit.h"
#include "rl/mdl/Dynamic.h"
#include "rl/mdl/Body.h"
#include "rl/mdl/UrdfFactory.h"
#include "rl/mdl/Joint.h"

#include "tinyxml2.h"
#include "string"

using namespace rl;
using namespace std;
using namespace tinyxml2;

const int REVOLUTE = 9;
const int PRISMATIC = 10;
const int FIXED = 11;


struct Node {
  string bodyName;
  string jointName;
  Node* parent;
  mdl::Body* body;
  int jointType;

  Node(string bodyNameIn="", string jointNameIn="", Node* parentIn=nullptr, mdl::Body* bodyIn=nullptr, int jointTypeIn=FIXED){
    bodyName = bodyNameIn;
    jointName = jointNameIn;
    parent = parentIn;
    body = bodyIn;
    jointType = jointTypeIn;
  }
};

class MatlabRobot {
public:
  const mdl::Dynamic* robotPtr;
  unordered_map<string, Node*> body2NodeMap;
  unordered_map<string, string> joint2BodyMap;
  unordered_map<string, int> joint2IndMap;

  MatlabRobot(const mdl::Dynamic* robotPtrIn, string urdf_file_name){
    this->robotPtr = robotPtrIn;
    parseURDF(urdf_file_name);
  }

  ~MatlabRobot(){
    for (auto keyPair : this->body2NodeMap){
      delete keyPair.second;
    }
  }

  void parseURDF(const string& fileName) {
    XMLDocument doc;
    doc.LoadFile(fileName.c_str());

    XMLNode *root = (XMLNode *) doc.RootElement();

    unordered_map <string, string> parentLinkMap;
    //        unordered_set<string> linkNames;

    for (const XMLNode *xmlNode = root->FirstChild(); xmlNode; xmlNode = xmlNode->NextSibling()) {
      if( auto comment = dynamic_cast<const XMLComment*>(xmlNode) ) continue;
      const XMLElement* child = xmlNode->ToElement();

      if (strcmp(child->Value(), "joint") == 0) {
        string jointName = child->Attribute("name");
        string parentLinkName = child->FirstChildElement("parent")->Attribute("link");
        string childLinkName = child->FirstChildElement("child")->Attribute("link");
        //                linkNames.insert(parentLinkName);
        //                linkNames.insert(childLinkName);
        joint2BodyMap[jointName] = childLinkName;
        parentLinkMap[childLinkName] = parentLinkName;

        int jointType = FIXED;
        if (strcmp(child->Attribute("type"), "revolute") == 0){
          jointType = REVOLUTE;
        } else if (strcmp(child->Attribute("type"), "prismatic") == 0){
          jointType = PRISMATIC;
        }

        if (body2NodeMap.find(childLinkName) == body2NodeMap.end()){
          body2NodeMap[childLinkName] = new Node(childLinkName);
        }
        if (body2NodeMap.find(parentLinkName) == body2NodeMap.end()){
          body2NodeMap[parentLinkName] = new Node(parentLinkName);
        }

        body2NodeMap[childLinkName]->jointType = jointType;
        body2NodeMap[childLinkName]->jointName = jointName;
      }
    }

    for (auto keyPair : body2NodeMap){
      string linkName = keyPair.first;
      Node* parentNode = nullptr;

      if (parentLinkMap.find(linkName) != parentLinkMap.end()){
        string parentName = parentLinkMap[linkName];
        parentNode = body2NodeMap[parentName];
      }
      body2NodeMap[linkName]->parent = parentNode;
    }

    for (int i = 0; i < robotPtr->getBodies(); i++){
      body2NodeMap[robotPtr->getBody(i)->getName()]->body = robotPtr->getBody(i);
    }

    for (int i = 0; i < robotPtr->getJoints(); i++) {
      joint2IndMap[robotPtr->getJoint(i)->getName()] = i;
    }
  }

};



namespace py = pybind11;

template<typename T>
void free_vector(void* ptr) {
//    std::cout << "freeing memory @ " << ptr << "\n";
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

class URDFModel {
public:
    URDFModel(const std::string & urdf_file_name) {
  model = new mdl::Model();
  rl::mdl::UrdfFactory urdf;
  urdf.load(urdf_file_name, model);
  dynamics = (mdl::Dynamic*) model;
  dynamics->forwardPosition();

  robot = new MatlabRobot(dynamics, urdf_file_name);

  auto robot = new MatlabRobot(dynamics, urdf_file_name);
  auto numJoint = model->getJoints();

  auto numBodies = dynamics->getBodies();


  for (int i = 0; i < model->getJoints(); i++){
    jointNames.push_back((model->getJoint(i)->getName()));
  }


  for (int i = 0; i < model->getJoints(); i++){
    bodyNames.push_back((dynamics->getBody(i)->getName()));
  }

  numEE = dynamics->getOperationalDof();


  for (int i = 0; i < model->getJoints(); i++){
    minJoints.push_back(model->getJoint(i)->getMinimum()[0]);
  }



  for (int i = 0; i < model->getJoints(); i++){
    maxJoints.push_back(model->getJoint(i)->getMaximum()[0]);
  }

}

void setJoints(std::vector<double> jointAngles){
  auto curJoint = dynamics->getPosition();

    if (jointAngles.size() != curJoint.size()){
        std::stringstream ss;
        ss << "Wrong number of joint. Make sure input is length " << curJoint.size() << "\n";
        throw std::runtime_error(ss.str());
        }

  for (int i =0; i < curJoint.size(); i++){
    curJoint[i] = jointAngles[i];
  }
  dynamics->setPosition(curJoint);
  dynamics->forwardPosition();

}

py::array_t<float> getJoints(){
  auto curJoint = dynamics->getPosition();

  auto [joints_ptr, capsule] = allocateVector<float>(curJoint.size());
  auto & joints = *joints_ptr;
  for (int i = 0; i < curJoint.size(); i++){
    joints[i] = curJoint[i];
  }
    auto arr = py::array_t<float>(joints_ptr->size(), joints_ptr->data(), capsule);
  return arr;
}

py::array_t<float> getOperationalPosition(int index){

    if (index >= model->getOperationalDof()){
     std::stringstream ss;
        ss << "index "<< index <<" must be positive and less than the number of end effectors: " << model->getOperationalDof() << "\n";
        throw std::runtime_error(ss.str());
    }

  rl::math::Transform tEE = model->getOperationalPosition(index);
  auto [T_ptr, capsule] = allocateVector<float>(16);
  auto& T = *T_ptr;
    for (int r = 0; r < 4; r++){
    for (int c = 0; c < 4; c++){
        T[r*4 + c] = tEE.data()[c*4 + r];
    }
    }

   auto arr = py::array_t<float>(T_ptr->size(), T_ptr->data(), capsule);
  arr = arr.reshape({4, 4});  // Set the shape to 4x4
    return arr;

}

py::array_t<float> getJacobian(){
  int numDof = dynamics->getDof();
  math::Matrix Jac = math::Matrix(6*numEE, numDof);
  dynamics->calculateJacobian(Jac);

  auto [J_ptr, capsule] = allocateVector<float>(6*numEE*numDof);
  auto& J = *J_ptr;

    for (int r = 0; r < 6*numEE; r++){
    for (int c = 0; c < numDof; c++){
        J[r*numDof + c] = Jac.data()[c*4 + r];
    }
    }


 auto arr = py::array_t<float>(J_ptr->size(), J_ptr->data(), capsule);
  arr = arr.reshape({6*numEE, numDof});  // Set the shape to 4x4
    return arr;

//  setMatrixOutput(plhs[0], J);
}

mdl::Body* getBody(int index){
    mdl::Body* body;
    body = dynamics->getBody(index);

     return body;
}

mdl::Body* getBody(const std::string& bodyName){
  mdl::Body* body;
  if (robot->body2NodeMap.find(bodyName) == robot->body2NodeMap.end()){
        std::stringstream ss;
        ss << "Body name not found: " << bodyName << "\n";
        throw std::runtime_error(ss.str());
  }

    Node* node = robot->body2NodeMap[bodyName];
    body = node->body;

  return body;
}

py::array_t<float> getBodyTransform(const std::string& bodyName) {
  auto body = getBody(bodyName);

  auto [T_ptr, capsule] = allocateVector<float>(16);
  auto& T = *T_ptr;
    for (int r = 0; r < 4; r++){
    for (int c = 0; c < 4; c++){
        T[r*4 + c] = body->t.data()[c*4 + r];
    }
    }

   auto arr = py::array_t<float>(T_ptr->size(), T_ptr->data(), capsule);
  arr = arr.reshape({4, 4});  // Set the shape to 4x4
    return arr;
}

py::array_t<float> getJointTransform(const std::string& jointName){
  if (robot->joint2BodyMap.find(jointName) == robot->joint2BodyMap.end()){
        std::stringstream ss;
        ss << "Joint name not found: " << jointName << "\n";
        throw std::runtime_error(ss.str());
  }

  string bodyName = robot->joint2BodyMap[jointName];
  mdl::Body* body = getBody(bodyName);

  auto [T_ptr, capsule] = allocateVector<float>(16);
  auto& T = *T_ptr;
    for (int r = 0; r < 4; r++){
    for (int c = 0; c < 4; c++){
        T[r*4 + c] = body->t.data()[c*4 + r];
    }
    }

   auto arr = py::array_t<float>(T_ptr->size(), T_ptr->data(), capsule);
  arr = arr.reshape({4, 4});  // Set the shape to 4x4
    return arr;
//  setMatrixOutput(plhs[0], body->t);
}


    std::vector<std::string> jointNames;
    std::vector<std::string> bodyNames;
    int numEE;
    std::vector<double> minJoints;
    std::vector<double> maxJoints;

private:
    MatlabRobot* robot;
    mdl::Model* model;
    mdl::Dynamic* dynamics;
    int value;
};

PYBIND11_MODULE(_core, m) {
    py::class_<URDFModel>(m, "URDFModel")
        .def(py::init<std::string>())
        .def("getBodyTransform", &URDFModel::getBodyTransform)
        .def("getJointTransform", &URDFModel::getJointTransform)
        .def("getOperationalPosition", &URDFModel::getOperationalPosition)
        .def("getJacobian", &URDFModel::getJacobian)
        .def("setJoints", &URDFModel::setJoints)
        .def("getJoints", &URDFModel::getJoints)
        .def_readwrite("jointNames", &URDFModel::jointNames)
        .def_readwrite("bodyNames", &URDFModel::bodyNames)
        .def_readwrite("numEE", &URDFModel::numEE)
        .def_readwrite("minJoints", &URDFModel::minJoints)
        .def_readwrite("maxJoints", &URDFModel::maxJoints);
}
