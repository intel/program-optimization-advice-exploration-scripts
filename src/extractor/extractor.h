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

#define PIN_METHOD 0

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

template<class T>
class InsertOrderSet {
  set<T> s;
  vector<T> v;
  public:
  void insert(T e);
  const vector<T>& get_vec() { return v; }
  public:
  InsertOrderSet() {}
  InsertOrderSet(const InsertOrderSet& ios) : s(ios.s) , v(ios.v) {  }
  void operator= (const InsertOrderSet& ios) { s = ios.s; v = ios.v; }
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
    string targetfilename;
    std::pair<unsigned, unsigned> lineNumbers;
    // string main_file_name;
    // std::pair<unsigned, unsigned> mainLineNumbers;
    std::set<std::pair<unsigned, unsigned>> extracted;
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
    void setTargetLineNumbers(const string& filename, unsigned first, unsigned second) 
    { targetfilename = filename; lineNumbers.first = first; lineNumbers.second = second; }
    /*
    void setMainInfo(const string& filename, unsigned first, unsigned second) 
    { main_file_name = filename;
      mainLineNumbers.first = first; mainLineNumbers.second = second; }
    */

    void cleanupName(string& name, bool remove_dots);
    string getFilePath() { return LoopExtractor_file_path; };
    string getFileName() { return LoopExtractor_file_name; };
    string getOrigFileName() { return LoopExtractor_original_file_name; };
    string getFileExtn() { return LoopExtractor_file_extn; };
    string getFilePath(const string &fileNameWithPath);
    string getFileName(const string &fileNameWithPath);
    string getOrigFileName(const string &fileNameWithPath);
    string getFileExtn(const string &fileNameWithPath);
    string getBaseFileName() {
      return getOrigFileName() + base_str + "_" + relpathcode + "." + getFileExtn();
    }
    int getAstNodeLineNum(SgNode *const &astNode);
    string getExtractionFileName(SgNode *astNode);
    string getReplayFileName(SgNode *astNode);
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
    void instrumentMain();
    virtual InheritedAttribute
    evaluateInheritedAttribute(SgNode *astNode, InheritedAttribute inh_attr);
    virtual int
    evaluateSynthesizedAttribute(SgNode *astNode, InheritedAttribute inh_attr,
                                 SubTreeSynthesizedAttributes syn_attr_list);
    void inlineFunctions(const vector<string> &argv);

    void do_extraction();
    static SgExprStatement* buildSimpleFnCallStmt(string fnName, SgScopeStatement* scope);
    void reportOutputFiles();
};

class TypeDeclTraversal : public AstSimpleProcessing {
  //vector<SgDeclarationStatement*> type_decl_v;
  //set<SgDeclarationStatement*> type_decl_s;
  InsertOrderSet<SgDeclarationStatement*> type_decl_ios;
  set<SgDeclarationStatement*> type_decl_visited;
  public:
  TypeDeclTraversal():AstSimpleProcessing() { }
  TypeDeclTraversal(const TypeDeclTraversal& t):AstSimpleProcessing() { 
    type_decl_ios = t.type_decl_ios; type_decl_visited = t.type_decl_visited; }
  virtual void visit (SgNode* n);
  void visit_if_namedtype(SgType* decl_type);
  void visit_defining_decl(SgDeclarationStatement* decl_type);
  const vector<SgDeclarationStatement*>& get_type_decl_v() { return type_decl_ios.get_vec(); }
};
class CallTraversal : public AstSimpleProcessing {
  InsertOrderSet<SgFunctionDeclaration*> fn_defn_ios;
  set<SgFunctionDeclaration*> fn_defn_visited;
  set<SgFunctionDeclaration*> fn_decl_s;
  public:
  virtual void visit (SgNode* n);
  const vector<SgFunctionDeclaration*>& get_fn_defn_v() { return fn_defn_ios.get_vec(); }
  const set<SgFunctionDeclaration*>& get_fn_decl_s() { return fn_decl_s; }
};
/* Must contain all info regarding the current loop */
class LoopInfo {
    const string RESTORE_GUARD_NAME = "__RESTORE_CODELET__";
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
    void printLoopFunc1(string loop_file_name, string replay_loop_filename);
    void pushPointersToLocalVars(ofstream &loop_file_buf);
    void popLocalVarsToPointers(ofstream &loop_file_buf);
    void analyzeOMPprivateArrays(const string &pragmaStr);
    string printOMPprivateArrays();
    string sanitizeOMPpragma(const string &pragmaStr);
    void addLoopFuncAsExtern(); // In Base file
    void addLoopFuncCall();     // In Base file
    SgFunctionDeclaration* makeLoopFunc(bool defining, SgGlobal* glb) ;
    SgFunctionDeclaration* addLoopFuncDefnDecl(SgGlobal* glb); // In Base file
    void dumpGlobalVarNames(string data_folder);
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
    SgExpression* getFuncParamAddr(SgInitializedName* func_arg_decl, SgExpression* funcArgument);
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
