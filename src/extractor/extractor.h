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
    //int scope_depth_;

    //InheritedAttribute() : loop_nest_depth_(0), scope_depth_(0) {}
    InheritedAttribute() : loop_nest_depth_(0)  {}

    InheritedAttribute(const InheritedAttribute &other) {
        loop_nest_depth_ = other.loop_nest_depth_;
        //scope_depth_ = other.scope_depth_;
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

class LoopLocations {
  // list of file name and line number pairs
  std::set<std::pair<string, unsigned>> locs;
  int loop_nest_depth_;
  public:
  LoopLocations() : loop_nest_depth_(0) {}
  LoopLocations(const LoopLocations &other) : locs(other.locs), 
    loop_nest_depth_(other.loop_nest_depth_) { }
  void addLoc(string filename, unsigned lineNo) { locs.insert(std::make_pair(filename, lineNo)); }
  bool matches(SgNode* ast);
  void incLevel() { loop_nest_depth_++; }
  int getLoopLevel() {return loop_nest_depth_; }
};
class CollectedLoops {
  std::set<SgForStatement*> collected;
  int deepest_nest;
  public:
  CollectedLoops(): deepest_nest(0) {}
  CollectedLoops(const CollectedLoops &other) : collected(other.collected), 
    deepest_nest(other.deepest_nest) {}
  void set(SgForStatement* loop, int nest_level);
  void addAll(const CollectedLoops& loops) ;
  bool isEmpty() { return collected.empty(); }
  bool matches(SgForStatement* ast) { return collected.count(ast) > 0; }
  int getLoopDepth() {return deepest_nest; }
  void incLoopDepth() {deepest_nest++;}
};

class LoopCollector : public SgTopDownBottomUpProcessing<LoopLocations, CollectedLoops> {
    virtual LoopLocations
    evaluateInheritedAttribute(SgNode *astNode, LoopLocations inh_attr);
    virtual CollectedLoops
    evaluateSynthesizedAttribute(SgNode *astNode, LoopLocations inh_attr,
                                 SubTreeSynthesizedAttributes syn_attr_list);
};

class LoopInfo;

class Extractor : public SgTopDownBottomUpProcessing<InheritedAttribute, int> {
    string LoopExtractor_file_path;
    string LoopExtractor_original_file_name;
    string LoopExtractor_file_name;
    string LoopExtractor_file_extn;
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
    //SgSourceFile* src_file_loop;
    vector<SgSourceFile*> src_file_loops;
    //SgSourceFile* src_file_trace_save;
    //SgSourceFile* src_file_restore;
    vector<SgSourceFile*> src_file_restores;
    string targetfilename;
    std::pair<unsigned, unsigned> lineNumbers;
    // string main_file_name;
    // std::pair<unsigned, unsigned> mainLineNumbers;
    // std::set<std::pair<unsigned, unsigned>> extracted;
    LoopLocations loop_locs;
    CollectedLoops collected_loops;
    vector<string> filenameVec;
  protected:
    SgScopeStatement *main_scope = NULL;

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
    //SgScopeStatement *loopParentFuncScope = NULL;
    map<SgStatement *, SgScopeStatement *> externFuncDef;
    #if 0
    // disable for now
    vector<SgForStatement *>
        consecutiveLoops; // Collection of consecutive loop nests
    #endif

  public:
    Extractor(){};
    //Extractor(const vector<string> &argv, Tracer *tr);
    Extractor(const vector<string> &argv);

    src_lang getSrcType() { return src_type; }
    SgGlobal *getGlobalNode() { return global_node; }
    SgStatement *getLastIncludeStatement() { return lastIncludeStmt; }
    string getDataFolderPath() { return LoopExtractor_data_folder_path; };
    string getOMPpragma() { return loopOMPpragma; };
    void addTargetLineNumbers(const string& filename, unsigned first, unsigned second) 
    //{ targetfilename = filename; lineNumbers.first = first; lineNumbers.second = second; }
    { loop_locs.addLoc(filename, first); }
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
    void add_src_file_loop(SgSourceFile* file) { src_file_loops.push_back(file); }
    //void set_src_file_trace_save(SgSourceFile* file) { src_file_trace_save = file; }
    void add_src_file_restore(SgSourceFile* file) { src_file_restores.push_back(file); }
    //SgSourceFile* get_src_file() { return src_file_loop; }
    void printHeaders(ofstream &loop_file_buf);
    void printGlobalsAsExtern(ofstream &loop_file_buf);
    void addExternDefs(SgFunctionDeclaration *func, SgFunctionDefinition* encl_fn);
    void addPostTraversalDefs();
    void modifyExtractedFileText(const string &base_file);
    // void collectAdjoiningLoops(SgStatement *loop);
    //  void getVarsInFunction();

    bool skipLoop(SgForStatement *astNode);
    void extractLoops(SgForStatement *astNode);
    virtual void extractLoop(SgForStatement* curr_loop) = 0;
    void extractFunctions(SgNode *astNode);
    virtual InheritedAttribute
    evaluateInheritedAttribute(SgNode *astNode, InheritedAttribute inh_attr);
    virtual int
    evaluateSynthesizedAttribute(SgNode *astNode, InheritedAttribute inh_attr,
                                 SubTreeSynthesizedAttributes syn_attr_list);
    void inlineFunctions(const vector<string> &argv);

    void do_extraction();
    void final_pushback_fileList(SgProject* ast);
    static SgExprStatement* buildSimpleFnCallStmt(string fnName, SgScopeStatement* scope);
    void reportOutputFiles();
    void reportOutputFiles(ofstream& info_file, const vector<SgSourceFile*>& src_file_loop, const string& type);
    void reportOutputFiles(ofstream& info_file, SgSourceFile* src_file_loop, const string& type);
    void reportOutputFile(ofstream& info_file, const string& loop_file_name, const string& type);
    static Extractor* createExtractor(LoopExtractorMode mode, const vector<string>& argv);
    virtual void instrumentMain() = 0;
    virtual void generateBaseHeaders(SgGlobal* glb_scope) = 0;
    virtual void generateBasePreLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt, 
      LoopInfo* loop_info, vector<SgInitializedName *> scope_vars_initName_vec) = 0;
    virtual void generateBasePostLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt) = 0;
};

class OutliningExtractor : public Extractor {
  public:
    OutliningExtractor(const vector<string> &argv):Extractor(argv) {}
    void extractLoop(SgForStatement* curr_loop);
    virtual void extractLoop(SgForStatement* loop, LoopInfo& curr_loop);
};

class InvitroExtractor : public OutliningExtractor {
  public:
    InvitroExtractor(const vector<string> &argv):OutliningExtractor(argv) {}
    void generateBaseHeaders(SgGlobal* glb_scope);
    void generateBasePreLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt, 
      LoopInfo* loop_info, vector<SgInitializedName *> scope_vars_initName_vec);
    void generateBasePostLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt);
    void instrumentMain();
    void extractLoop(SgForStatement* loop, LoopInfo& curr_loop);
};

class InsituExtractor : public OutliningExtractor {
  public:
    InsituExtractor(const vector<string> &argv):OutliningExtractor(argv) {}
    void generateBaseHeaders(SgGlobal* glb_scope) {}
    void generateBasePreLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt, 
      LoopInfo* loop_info, vector<SgInitializedName *> scope_vars_initName_vec) {}
    void generateBasePostLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt) {}
    void instrumentMain() {}
};

class InvivoExtractor : public Extractor {
  public:
    InvivoExtractor(const vector<string> &argv):Extractor(argv) {}
    void generateBaseHeaders(SgGlobal* glb_scope) {}
    void generateBasePreLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt, 
      LoopInfo* loop_info, vector<SgInitializedName *> scope_vars_initName_vec) {}
    void generateBasePostLoop(SgScopeStatement* loop_scope, SgExprStatement* call_expr_stmt) {}
    void instrumentMain() {}
    void extractLoop(SgForStatement* curr_loop);
};

class TypeDeclTraversal : public AstSimpleProcessing {
  //vector<SgDeclarationStatement*> type_decl_v;
  //set<SgDeclarationStatement*> type_decl_s;
  InsertOrderSet<SgDeclarationStatement*> type_decl_ios;
  InsertOrderSet<SgDeclarationStatement*> type_decl_ios_pending;
  set<SgDeclarationStatement*> type_decl_visited;
  SgGlobal* global_scope;
  public:
  TypeDeclTraversal(SgGlobal* glb):AstSimpleProcessing(), global_scope(glb) { }
  TypeDeclTraversal(const TypeDeclTraversal& t):AstSimpleProcessing(),
  type_decl_ios(t.type_decl_ios), 
  type_decl_ios_pending(t.type_decl_ios_pending), 
  type_decl_visited(t.type_decl_visited),
  global_scope(t.global_scope) { }
  void operator= (const TypeDeclTraversal& ios) 
   { type_decl_ios = ios.type_decl_ios; 
    type_decl_ios_pending = ios.type_decl_ios_pending; 
    type_decl_visited = ios.type_decl_visited; 
    global_scope = ios.global_scope;
    }
  virtual void visit (SgNode* n);
  void add_decl(SgDeclarationStatement* type_decl) { assert (type_decl != NULL); type_decl_ios.insert(type_decl); }
  void add_decl_pending(SgDeclarationStatement* type_decl) { assert (type_decl != NULL); type_decl_ios_pending.insert(type_decl); }
  void mark_decl_visited(SgDeclarationStatement* decl) { 
    if(isSgTypedefDeclaration(decl) && (isSgTypedefDeclaration(decl)->get_name().getString() == "x264_t") ) {
      cout << "x264_t visisted" << endl;
    }
    type_decl_visited.insert(decl); 
    }
  void visit_if_namedtype(SgType* decl_type);
  void visit_defining_decl(SgDeclarationStatement* decl_type);
  const vector<SgDeclarationStatement*> get_type_decl_v() { 
    const vector<SgDeclarationStatement*>& pre_decls = type_decl_ios.get_vec();
    const vector<SgDeclarationStatement*>& pending_decls = type_decl_ios_pending.get_vec();
    vector<SgDeclarationStatement*> ans;
    ans.reserve(pre_decls.size() + pending_decls.size());
    //ans.reserve(pending_decls.size());
    ans.insert(ans.end(), pre_decls.begin(), pre_decls.end());
    ans.insert(ans.end(), pending_decls.begin(), pending_decls.end());
    return ans;
    }
};
class CallTraversal : public AstSimpleProcessing {
  InsertOrderSet<SgFunctionDeclaration*> fn_defn_ios;
  set<SgFunctionDeclaration*> fn_defn_visited;
  set<SgFunctionDeclaration*> fn_decl_s;
  InsertOrderSet<SgVariableDeclaration*> globals;
  InsertOrderSet<SgType*> types;
  public:
  CallTraversal():AstSimpleProcessing() { }
  CallTraversal(const CallTraversal& t) : AstSimpleProcessing(), 
    fn_defn_ios(t.fn_defn_ios), fn_defn_visited(t.fn_defn_visited),
    fn_decl_s(t.fn_decl_s), globals(t.globals), types(t.types) {}
  void operator= (const CallTraversal& ios) {
    fn_defn_ios = ios.fn_defn_ios;
    fn_defn_visited = ios.fn_defn_visited;
    fn_decl_s = ios.fn_decl_s;
    globals = ios.globals;
    types = ios.types;
  }
  virtual void visit (SgNode* n);
  void sub_visit(SgNode* n);
  const vector<SgFunctionDeclaration*>& get_fn_defn_v() { return fn_defn_ios.get_vec(); }
  const set<SgFunctionDeclaration*>& get_fn_decl_s() { return fn_decl_s; }
  const vector<SgVariableDeclaration*> get_global_decl_v() { return globals.get_vec(); }
  const vector<SgType*> get_type_v() { return types.get_vec(); }
};
/* Must contain all info regarding the current loop */
class LoopInfo {
    const string RESTORE_GUARD_NAME = "__RESTORE_CODELET__";
    Extractor *extr;
    // SgNode *astNode;
    SgForStatement *loop;
    // SgStatement *loop_func_call;
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

    // some type decl needed for standalone loop and replay file
    vector<SgDeclarationStatement*> type_decls_needed ;

  public:
    vector<string> scope_struct_str_vec;

  public:
    LoopInfo(SgForStatement *loop, string func_name,
             Extractor *e)
        : extr(e), loop(loop), func_name(func_name) {}
    string getFuncName() const { return func_name; }
    bool isDeclaredInInnerScope(SgScopeStatement *var_scope);
    void getVarsInScope();
    bool hasFuncCallInScope();
    void addScopeFuncAsExtern(string &externFuncStr);
    void addScopeGlobalsAsExtern(string &externGlobalsStr);

    //void printLoopFunc(ofstream &loop_file_buf);
    void printLoopFunc(string loop_file_name) ;
    void printLoopReplay(string replay_loop_filename);
    void pushPointersToLocalVars(ofstream &loop_file_buf);
    void popLocalVarsToPointers(ofstream &loop_file_buf);
    void analyzeOMPprivateArrays(const string &pragmaStr);
    string printOMPprivateArrays();
    string sanitizeOMPpragma(const string &pragmaStr);
    void addLoopFuncAsExtern(); // In Base file
    void addLoopFuncCall() ;     // In Base file
    SgFunctionDeclaration* makeLoopFunc(bool defining, SgGlobal* glb) ;
    SgFunctionDeclaration* addLoopFuncDefnDecl(SgGlobal* glb); // In Base file
    void dumpGlobalVarNames(const string& data_folder, const string& loop_file_name);
    void addGlobalVarDecls(SgGlobal* glb, bool as_extern); // In Base file
    void addGlobalVarDecl(SgGlobal* glb, bool as_extern, SgDeclarationStatement* var_decl); // In Base file

    SgScopeStatement *getLoopScope() { return loop_scope; }
    // SgNode *getLoopNode() {
    //     std::cout << "funcName:" << func_name << std::endl;
    //     return astNode;
    // }
    vector<string> getLoopFuncArgsName(); //{ return scope_vars_str_vec; }
    vector<string> getLoopFuncArgsType();
    vector<string> getGlobalVars() { return scope_globals_vec; }
    vector<SgInitializedName*> getGlobalVarsInitNameVec() { return global_vars_initName_vec; }
    SgForStatement *getLoopStatement() { return loop; }
    //SgStatement *getLoopFuncCall() { return loop_func_call; }
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
