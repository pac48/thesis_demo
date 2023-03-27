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



class URDFModel {
public:
    URDFModel(const std::string & urdf_file_name) {
  model = new mdl::Model();
  rl::mdl::UrdfFactory urdf;
  urdf.load(urdf_file_name, model);
  mdl::Dynamic* dynamics = (mdl::Dynamic*) model;
  dynamics->forwardPosition();

  robot = new MatlabRobot(dynamics, urdf_file_name);

  auto robot = new MatlabRobot(dynamics, urdf_file_name);
  auto numJoint = model->getJoints();

  auto numBodies = dynamics->getBodies();

   std::vector<std::string> jointNames;
  for (int i = 0; i < model->getJoints(); i++){
    jointNames.push_back((model->getJoint(i)->getName()));
  }

   std::vector<std::string> bodyNames;
  for (int i = 0; i < model->getJoints(); i++){
    bodyNames.push_back((dynamics->getBody(i)->getName()));
  }

  auto numEE = dynamics->getOperationalDof();

  std::vector<double> minJoints;
  for (int i = 0; i < model->getJoints(); i++){
    minJoints.push_back(model->getJoint(i)->getMinimum()[0]);
  }


  std::vector<double> maxJoints;
  for (int i = 0; i < model->getJoints(); i++){
    maxJoints.push_back(model->getJoint(i)->getMaximum()[0]);
  }

}

void setJoints(std::vector<double> jointAngles){
  auto curJoint = dynamics->getPosition();
  for (int i =0; i < curJoint.size(); i++){
    curJoint[i] = jointAngles[i];
  }
  dynamics->setPosition(curJoint);
  dynamics->forwardPosition();

}

void getJoints(){
  auto curJoint = dynamics->getPosition();

  std::vector<double> joints;
  joints.assign(0, curJoint.size());

  for (int i =0; i < curJoint.size(); i++){
    joints[i] = curJoint[i];
  }

}

//void getOperationalPosition(int nlhs, mxArray *plhs[],
//                            int nrhs, const mxArray *prhs[]){
//
//  mdl::Dynamic* model = getPairPtr(prhs[1]);
//
//  int index = mxGetScalar(prhs[2])-1;
//  rl::math::Transform T = model->getOperationalPosition(index);
//
////  setMatrixOutput(plhs[0], T);
//
//}

//void getJacobian(int nlhs, mxArray *plhs[],
//                 int nrhs, const mxArray *prhs[]){
//  mdl::Dynamic* model = getPairPtr(prhs[1]);
//  int numEE = model->getOperationalDof();
//  int numDof = model->getDof();
//  math::Matrix J = math::Matrix(6*numEE, numDof);
//  model->calculateJacobian(J);
//
////  setMatrixOutput(plhs[0], J);
//}

mdl::Body* getBody(int index){
    mdl::Body* body;
    body = dynamics->getBody(index);

     return body;
}

mdl::Body* getBody(const std::string& bodyName){
  mdl::Body* body;

    Node* node = robot->body2NodeMap[bodyName];
    body = node->body;

  return body;
}

void getBodyTransform(const std::string& bodyName) {
  auto body = getBody(bodyName);
//  setMatrixOutput(plhs[0], body->t);
}

void getJointTransform(const std::string& jointName){
  string bodyName = robot->joint2BodyMap[jointName];
  mdl::Body* body = getBody(bodyName);
//  setMatrixOutput(plhs[0], body->t);
}



private:
    MatlabRobot* robot;
    mdl::Model* model;
    mdl::Dynamic* dynamics;
    int value;
};

int loadModel(std::string fileName) {

}

//PYBIND11_MODULE(_core, m) {
//    m.def("loadModel", &loadModel, "A function that loads a .urdf file given name");
//}

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    py::class_<URDFModel>(m, "URDFModel")
        .def(py::init<std::string>())
        .def("getBodyTransform", &URDFModel::getBodyTransform)
        .def("setJoints", &URDFModel::setJoints)
        .def("getJoints", &URDFModel::getJoints);
}
