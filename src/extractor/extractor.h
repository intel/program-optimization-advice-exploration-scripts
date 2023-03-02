#ifndef EXTRACTOR_H_
#define EXTRACTOR_H_

#include "driver/common.h"
#include "tracer/tracer.h"
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <boost/tokenizer.hpp>
#include <cstdio>
#include <iostream>

using namespace std;

class InheritedAttribute {
  public:
    int loop_nest_depth_;
    int scope_depth_;

    InheritedAttribute() : loop_nest_depth_(0), scope_depth_(0) {}

    InheritedAttribute(const InheritedAttribute &other) {
        loop_nest_depth_ = other.loop_nest_depth_;
        scope_depth_ = other.scope_depth_;
    }
};

class SynthesizedAttribute {
  public:
    SynthesizedAttribute() {}
};

class Extractor : public SgTopDownBottomUpProcessing<InheritedAttribute, int> {
    string LoopExtractor_file_path;
    string LoopExtractor_original_file_name;
    string LoopExtractor_file_name;
    string LoopExtractor_file_extn;
    SgScopeStatement *main_scope = NULL;
    bool nonVoidMain = false;
    int uniqueCounter = 0; // for loops at same line number bcoz of macros
    string relpathcode =
        ""; // for files with same name but in different folders
    SgStatement *lastIncludeStmt = NULL;
    SgGlobal *global_node;           // Needed to add the extern calls
    set<SgNode *> astNodesCollector; // Required to not add loop functions on
                                     // Ast Post Processing
    vector<SgStatement *> externLoopFuncDefinitionsAdd;
    /* header_vec needs to be vector so that the order of IFDEF,ENDIF,etc.
     * remain same */
    vector<string> header_vec;
    /* Global vars and associated OMP threadprivate directives */
    vector<string> global_vars;
    vector<string> static_funcs_vec;
    /* If typedef struct is with defination then line number of struct def is
     * same, hence exclude */
    vector<int> typedef_struct_lineno_vec;
    src_lang src_type;

    //Tracer *tr;
    vector<string> global_var_names;
    vector<string> short_loop_names;
    SgSourceFile* src_file_loop;
    SgSourceFile* src_file_trace_save;
    SgSourceFile* src_file_restore;
    std::pair<unsigned, unsigned> lineNumbers;
    vector<string> filenameVec;

  public:
    string ignorePrettyFunctionCall1 = "__PRETTY_FUNCTION__";
    string ignorePrettyFunctionCall2 = "__func__";
    string ignorePrettyFunctionCall3 = "__FUNCTION__";
    bool mainFuncPresent = false;
    bool copysourcefiles = false;
    int if_else_macro_count;
    vector<string> *loop_funcName_vec = new vector<string>;
    map<SgFunctionDeclaration *, string> inline_func_map;
    string loopOMPpragma = "";
    string loopSkipPragma = "";
    vector<string> func_var_str_vec;
    SgScopeStatement *loopParentFuncScope = NULL;
    map<SgStatement *, SgScopeStatement *> externFuncDef;
    vector<SgForStatement *>
        consecutiveLoops; // Collection of consecutive loop nests

  public:
    Extractor(){};
    //Extractor(const vector<string> &argv, Tracer *tr);
    Extractor(const vector<string> &argv);

    src_lang getSrcType() { return src_type; }
    SgGlobal *getGlobalNode() { return global_node; }
    SgStatement *getLastIncludeStatement() { return lastIncludeStmt; }
    string getDataFolderPath() { return LoopExtractor_data_folder_path; };
    string getOMPpragma() { return loopOMPpragma; };
    void setLineNumbers(unsigned first, unsigned second) 
    { lineNumbers.first = first; lineNumbers.second = second; }

    string getFilePath() { return LoopExtractor_file_path; };
    string getFileName() { return LoopExtractor_file_name; };
    string getOrigFileName() { return LoopExtractor_original_file_name; };
    string getFileExtn() { return LoopExtractor_file_extn; };
    string getFilePath(const string &fileNameWithPath);
    string getFileName(const string &fileNameWithPath);
    string getOrigFileName(const string &fileNameWithPath);
    string getFileExtn(const string &fileNameWithPath);
    int getAstNodeLineNum(SgNode *const &astNode);
    string getExtractionFileName(SgNode *astNode);
    void updateUniqueCounter(SgNode *astNode);
    string getLoopName(SgNode *astNode);
    void set_src_file_loop(SgSourceFile* file) { src_file_loop = file; }
    void set_src_file_trace_save(SgSourceFile* file) { src_file_trace_save = file; }
    void set_src_file_restore(SgSourceFile* file) { src_file_restore = file; }
    SgSourceFile* get_src_file() { return src_file_loop; }
    void printHeaders(ofstream &loop_file_buf);
    void printGlobalsAsExtern(ofstream &loop_file_buf);
    void addExternDefs(SgFunctionDeclaration *func);
    void addPostTraversalDefs();
    void modifyExtractedFileText(const string &base_file);
    void collectAdjoiningLoops(SgStatement *loop);
    //  void getVarsInFunction();

    bool skipLoop(SgNode *astNode);
    void extractLoops(SgNode *astNode);
    void extractFunctions(SgNode *astNode);
    virtual InheritedAttribute
    evaluateInheritedAttribute(SgNode *astNode, InheritedAttribute inh_attr);
    virtual int
    evaluateSynthesizedAttribute(SgNode *astNode, InheritedAttribute inh_attr,
                                 SubTreeSynthesizedAttributes syn_attr_list);
    void inlineFunctions(const vector<string> &argv);

    void do_extraction();
};

/* Must contain all info regarding the current loop */
class LoopInfo {
    Extractor &extr;
    SgNode *astNode;
    SgForStatement *loop;
    SgStatement *loop_func_call;
    string func_name;
    SgScopeStatement *loop_scope;
    vector<string> scope_vars_str_vec;
    vector<SgVariableSymbol *> scope_vars_symbol_vec;
    vector<SgInitializedName *> scope_vars_initName_vec;
    vector<SgInitializedName *> global_vars_initName_vec;
    set<SgFunctionDeclaration *> scope_funcCall_vec;
    vector<string> scope_globals_vec;
    vector<string> privateOMP_array_vec;
    vector<string> OMPscope_symbol_vec;
    map<string, string> OMParray_type_map;

  public:
    vector<string> scope_struct_str_vec;

  public:
    LoopInfo(SgNode *astNode, SgForStatement *loop, string func_name,
             Extractor &e)
        : extr(e), astNode(astNode), loop(loop), func_name(func_name) {}
    string getFuncName() { return func_name; }
    bool isDeclaredInInnerScope(SgScopeStatement *var_scope);
    void getVarsInScope();
    bool hasFuncCallInScope();
    void addScopeFuncAsExtern(string &externFuncStr);
    void addScopeGlobalsAsExtern(string &externGlobalsStr);

    void printLoopFunc(ofstream &loop_file_buf);
    void printLoopFunc1(string loop_file_name);
    void pushPointersToLocalVars(ofstream &loop_file_buf);
    void popLocalVarsToPointers(ofstream &loop_file_buf);
    void analyzeOMPprivateArrays(const string &pragmaStr);
    string printOMPprivateArrays();
    string sanitizeOMPpragma(const string &pragmaStr);
    void addLoopFuncAsExtern(); // In Base file
    void addLoopFuncCall();     // In Base file
    SgFunctionDeclaration* makeLoopFunc(bool defining, SgGlobal* glb) ;
    SgFunctionDeclaration* addLoopFuncDefnDecl(SgGlobal* glb); // In Base file
    void addGlobalVarDecls(SgGlobal* glb, bool as_extern); // In Base file

    SgScopeStatement *getLoopScope() { return loop_scope; }
    SgNode *getLoopNode() {
        std::cout << "funcName:" << func_name << std::endl;
        return astNode;
    }
    vector<string> getLoopFuncArgsName(); //{ return scope_vars_str_vec; }
    vector<string> getLoopFuncArgsType();
    vector<string> getGlobalVars() { return scope_globals_vec; }
    vector<SgInitializedName*> getGlobalVarsInitNameVec() { return global_vars_initName_vec; }
    SgForStatement *getLoopStatement() { return loop; }
    SgStatement *getLoopFuncCall() { return loop_func_call; }
    void restoreGlobalVars();
    void saveGlobalVars();
    void saveRestoreGlobalVars(bool is_save);
    std::vector<SgStatement *> buildDataSavingLines() ;
    SgStatement *buildPrintFunc(std::string printStr, std::string variableName) ;
    SgStatement *buildPrintAddrOfFunc(std::string printStr, std::string variableName) ;
    SgStatement *buildPrintFunc(std::string printStr,  SgExpression* exp) ;
    vector<SgStatement *> buildSegmentPtrs() ;
    SgStatement *buildWriteStack(string datafileName);
    SgStatement *buildWriteHeap(string datafileName);
    SgExprListExp* getSaveCurrentFuncParamAddrArgs(SgExpression* lhs, SgInitializedName* func_arg_decl, SgExpression* funcArgument);
    vector<SgStatement *> saveLoopFuncParamAddresses(SgExprStatement* call_expr_stmt) ;
    SgBasicBlock* saveLoopFuncParamAddressesInBB(SgExprStatement* call_expr_stmt) ;
    SgBasicBlock* saveGlobalVarsInBB() ;
    vector<SgStatement *> buildBrkStmt() ;
    SgBasicBlock* addrPrintingInBB();
    SgVariableDeclaration* buildExternVarDecl(string varName, SgType* type) ;
    SgVariableDeclaration* buildExternCharStarStarVarDecl(string varName) ; 
    SgVariableDeclaration* buildExternIntVarDecl(string varName) ;
};

#endif
