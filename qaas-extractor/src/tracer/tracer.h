#ifndef TRACER_H_
#define TRACER_H_

#include "driver/common.h"
#include "rose.h"
#include <fstream>
#include <iostream>
#include <set>
#include <string>

#include "CallGraph.h"
#include "CallGraphTraverse.h"

class LoopFuncInfo {
  private:
    string func_name;
    SgFunctionDeclaration *func_decl;
    vector<string> func_args;
    vector<string> func_args_type;
    vector<string> global_vars;
    int instanceNum = 1;

  public:
    LoopFuncInfo() {}
    LoopFuncInfo(string func_name, vector<string> func_args,
                 vector<string> func_args_type, vector<string> global_vars) {
        this->func_name = func_name;
        this->func_args = func_args;
        this->func_args_type = func_args_type;
        this->global_vars = global_vars;
    }
    string getFuncName() { return func_name; }
    vector<string> getFuncArgs() { return func_args; }
    vector<string> getFuncArgsType() { return func_args_type; }
    vector<string> getGlobalVars() { return global_vars; }
    int getInstanceNum() { return instanceNum; }
    SgFunctionDeclaration *getFuncDecl() { return func_decl; }
    void setFuncName(string func_name) { this->func_name = func_name; }
    void setFuncArgs(vector<string> func_args) { this->func_args = func_args; }
    void setFuncArgsType(vector<string> func_args_type) {
        this->func_args_type = func_args_type;
    }
    void setGlobalVars(vector<string> global_vars) {
        this->global_vars = global_vars;
    }
    void setInstanceNum(int instanceNum) { this->instanceNum = instanceNum; }
    void setFuncDecl(SgFunctionDeclaration *func_decl) {
        this->func_decl = func_decl;
    }
};

class Tracer : public AstSimpleProcessing {
  private:
    // This data is generated in initTracing()
    SgProject *project;
    string baseFileName;

    vector<string> loopFileNames;

    SgScopeStatement *loopScope; // useless??
    SgNode *loopNode;            // useless??

    SgStatement *insertBefore;
    SgScopeStatement *loopFuncScope;
    SgGlobal *globalscope;
    string loopExtrIncludeFlag;

    vector<string> globalVariableNames;
    vector<SgInitializedName*> global_vars_initName_vec ;
    vector<string> localVariableNames;

    vector<string> filenameVec;

    string currentLoopFileName;
    ofstream restoreOutfile;
    vector<string> headerLines;
    SgStatement *loopFuncNode;
    set<SgType *> declaredTypes;
    stringstream variableDeclarations;
    stringstream classDeclarations;
    vector<string> globalNames;

    vector<LoopFuncInfo *> LFI;
    LoopFuncInfo *current_lfi = nullptr;

    set<SgName> visitedFuncCalls;
    void traverseCG(
        SgGraphNode *CGNode, SgIncidenceDirectedGraph *CG,
        boost::unordered_map<SgFunctionDeclaration *, SgGraphNode *> &mapCG);
    void exportFuncCalls();

  public:
    virtual void visit(SgNode *n);
    Tracer() {}
    void initTracing();
    void buildHeaders();
    void insertSaveInfo();
    void insertTraceInfo();
    void setBaseFileName(std::string fileName);
    void addLoopFileName(std::string fileName);
    void addHeaderLine(std::string line);
    string getCurrentLoopFileName();

    void setLoopExtrIncludeFlag(std::string loopExtrIncludeFlag);
    void setFilenameVec(std::vector<std::string> filenameVec);
    void setLoopScope(SgScopeStatement *loopScope);
    void setLoopFuncScope(SgScopeStatement *loopFuncScope);
    void setLoopNode(SgNode *loopNode);
    void setInsertStatement(SgStatement *insertBefore);
    void setLocalVars(std::vector<std::string> localVariableNames);
    void setGlobalVars(std::vector<std::string> globalVariableNames);
    void setGlobalVarsInitNameVec(vector<SgInitializedName *> global_vars_initName_vec);

    void addLoopFuncInfo(LoopFuncInfo *LFI);

    SgStatement *buildVarDecl(string varName, string varType);
    vector<SgStatement *> buildSegmentPtrs();
    SgStatement *buildPrintFunc(string printStr, string variableName);
    SgStatement *buildPrintImitFunc(string printStr);
    SgStatement *buildWriteStack(string datafileName);
    SgStatement *buildWriteHeap(string datafileName);
    vector<SgStatement *> buildBrkStmt();
    vector<SgStatement *> saveGlobalVars();
    vector<SgStatement *> saveLoopFuncParamAddresses();
    SgStatement *buildAddrPrinting();
    SgStatement *buildDataSavingLines();
    void buildInstanceCheck(int instanceNum, SgStatement *body);
    void buildInstanceIncrement();

    void insertRestoreHeaders();
    void insertLoopFuncDecl();
    void insertClassDeclarations();
    void insertGlobalVarDeclarations();
    void insertMainFunction();
    void typeDeclaration(SgType *tp);
    void variableDeclaration(SgVariableSymbol *smbl);
    void insertGlobalVariablesRead();
    void insertLoopFuncCall();

    void moveCodeletSourcefile(string prefixStr, string funcName,
                               string baseFileName, bool isRestore);
    void moveDriverFile(string prefixStr, string funcName, string baseFileName);
    void moveFile(string fileName, string dirName);

    std::pair<unsigned, unsigned> lineNumbers;
};

class ParseLoopFiles : public AstSimpleProcessing {

  public:
    vector<string> *fileNames;
    virtual void visit(SgNode *node);
    Tracer *tr;
    ParseLoopFiles(vector<string> *fileNames) { this->fileNames = fileNames; }
};

#endif