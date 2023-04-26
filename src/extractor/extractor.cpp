/*
 * Written by: Aniket Shivam
 * Loop Extractor and Function Extractor too (in future)
 * Move loops into new file as function with calls to that
 * function in the base file.
 */
#include "extractor.h"

string Extractor::getFilePath(const string &fileNameWithPath) {
    int lastSlashPos = fileNameWithPath.find_last_of('/');
    return (fileNameWithPath.substr(0, lastSlashPos + 1));
}

void Extractor::cleanupName(string& name, bool remove_dots) {
    /* Since you cannot start Function name with a digit */
    if (isdigit(name[0]))
        name.insert(0, 1, '_');
    /* Since you cannot have '-' in Function name */
    while (name.find('-') != string::npos)
        name.replace(name.find('-'), 1, string("X_X"));
    if (remove_dots) {
        while (name.find('.') != string::npos)
         name.replace(name.find('.'), 1, string("Y_Y"));
    }
}
string Extractor::getFileName(const string &fileNameWithPath) {
    int lastSlashPos = fileNameWithPath.find_last_of('/');
    int lastDotPos = fileNameWithPath.find_last_of('.');
    string fileStr = (fileNameWithPath.substr(lastSlashPos + 1,
                                              lastDotPos - lastSlashPos - 1));
    cleanupName(fileStr, false);
    return fileStr;
}

string Extractor::getOrigFileName(const string &fileNameWithPath) {
    int lastSlashPos = fileNameWithPath.find_last_of('/');
    int lastDotPos = fileNameWithPath.find_last_of('.');
    return (fileNameWithPath.substr(lastSlashPos + 1,
                                    lastDotPos - lastSlashPos - 1));
}

string Extractor::getFileExtn(const string &fileNameWithPath) {
    int lastDotPos = fileNameWithPath.find_last_of('.');
    string extn = fileNameWithPath.substr(lastDotPos + 1);
    transform(extn.begin(), extn.end(), extn.begin(), ::tolower);
    regex fortran_extn("f*");
    if (extn.compare("c") == 0)
        src_type = src_lang_C;
    else if (extn.compare("cc") == 0 || extn.compare("cpp") == 0)
        src_type = src_lang_CPP;
    else if (regex_match(extn, fortran_extn))
        src_type = src_lang_FORTRAN;
    else
        ROSE_ASSERT(false);

    return extn;
}

int Extractor::getAstNodeLineNum(SgNode *const &astNode) {
    ROSE_ASSERT(astNode != NULL);
    SgLocatedNode *locatedNode = isSgLocatedNode(astNode);
    // Deprecated: return rose::getLineNumber(locatedNode);
    return astNode->get_file_info()->get_line();
}

string Extractor::getReplayFileName(SgNode *astNode) {
    return "replay_"+getExtractionFileName(astNode);
}
string Extractor::getExtractionFileName(SgNode *astNode) {
    string fileNameWithPath = (astNode->get_file_info())->get_filenameString();
    LoopExtractor_file_path = getFilePath(fileNameWithPath);
    LoopExtractor_file_name = getFileName(fileNameWithPath);
    LoopExtractor_original_file_name = getOrigFileName(fileNameWithPath);
    LoopExtractor_file_extn = getFileExtn(fileNameWithPath);
    int lineNumber = getAstNodeLineNum(astNode);

    string file_name = LoopExtractor_original_file_name;
    string file_extn = LoopExtractor_file_extn;

    string enclosingFuncName =
        (SageInterface::getEnclosingFunctionDeclaration(astNode)
             ->get_qualified_name())
            .getString();
    boost::erase_all(enclosingFuncName, "::");

    file_name += "_" + enclosingFuncName;
    file_name += "_line" + to_string(lineNumber);

    if (uniqueCounter != 0)
        file_name += "_" + to_string(uniqueCounter);
    if (!relpathcode.empty())
        file_name += "_" + relpathcode;

    file_name += "." + LoopExtractor_file_extn;

    //string output_path = getDataFolderPath();
    //return output_path + file_name;
    return file_name;
}

void Extractor::updateUniqueCounter(SgNode *astNode) {
    uniqueCounter = 0;
    string file_name = getExtractionFileName(astNode);
    //boost::erase_all(file_name, getDataFolderPath());
    boost::erase_all(file_name, "." + LoopExtractor_file_extn);
    boost::erase_all(file_name, relpathcode);

    /* check for loops at same line number bcoz of macros and add suffix*/
    for (auto const &funcstr : files_to_compile) {
        if (funcstr.find(file_name) != string::npos)
            uniqueCounter++;
    }
}

string Extractor::getLoopName(SgNode *astNode) {
    string loopName = getExtractionFileName(astNode);
    /* Since you cannot have '-' in Function name */
    cleanupName(loopName, true);
    //boost::erase_all(loopName, getDataFolderPath());
    boost::erase_all(loopName, "." + LoopExtractor_file_extn);
    return loopName;
}

bool LoopInfo::isDeclaredInInnerScope(SgScopeStatement *var_scope) {
    vector<SgNode *> nested_scopes =
        NodeQuery::querySubTree(loop_scope, V_SgScopeStatement);
    if (var_scope == NULL || nested_scopes.empty())
        return false;
    vector<SgNode *>::const_iterator scopeItr = nested_scopes.begin();
    for (; scopeItr != nested_scopes.end(); scopeItr++) {
        if (isSgNode(var_scope) == isSgNode(*scopeItr))
            return true;
    }
    return false;
}

void LoopInfo::getVarsInScope() {
    /* collectVarRefs will collect all variables used in the loop body */
    vector<SgVarRefExp *> sym_table;
    set<SgInitializedName *> global_vars_initName_set;
    SageInterface::collectVarRefs(dynamic_cast<SgLocatedNode *>(loop),
                                  sym_table);

    vector<SgVarRefExp *>::iterator iter;
    for (iter = sym_table.begin(); iter != sym_table.end(); iter++) {
        SgVariableSymbol *var = (*iter)->get_symbol();
        SgScopeStatement *var_scope = (var->get_declaration())->get_scope();

        if (!(isSgGlobal(var_scope) || isDeclaredInInnerScope(var_scope) ||
              var_scope->get_qualified_name() != "") &&
            find(scope_vars_symbol_vec.begin(), scope_vars_symbol_vec.end(),
                 var) == scope_vars_symbol_vec.end()) {
            scope_vars_symbol_vec.push_back(var); // Needed for function call
            scope_vars_initName_vec.push_back(
                var->get_declaration()); // Needed for function extern defn
        } else if (isSgGlobal(var_scope) &&
                   var_scope->get_qualified_name() != "") {
            SgInitializedName* var_decl = var->get_declaration();
            if (! global_vars_initName_set.count(var_decl)) {
                // Needed for extracted function extern defn
                global_vars_initName_set.insert(var_decl); 
                global_vars_initName_vec.push_back(var_decl);
            }
        }
    }
}

// Assuming parent scope already pushed by SageBuilder::pushScopeStack()
SgBasicBlock* LoopInfo::saveGlobalVarsInBB() {
    SgBasicBlock* bb = SageBuilder::buildBasicBlock_nfi(SageBuilder::topScopeStack());
    SageBuilder::pushScopeStack(bb);
    this->saveGlobalVars();
    SageBuilder::popScopeStack();
    return bb;
}

void LoopInfo::saveGlobalVars() {
    this->saveRestoreGlobalVars(true);
}

void LoopInfo::restoreGlobalVars() {
    this->saveRestoreGlobalVars(false);
}

/**
 * @brief Function that generates code lines that saves and restores global variable
 *        addresses in a datafile
 * @return SgStatement* will be appended to current scope
 */
void LoopInfo::saveRestoreGlobalVars(bool is_save) {
    string rw_mode = is_save ? "w" : "r";
    string rw_call = is_save ? "fwrite" : "fread";
    /* 'FILE* fp;' line of a function pointer declaration */
    auto file_type = SageBuilder::buildPointerType(
        SageBuilder::buildOpaqueType("FILE", SageBuilder::topScopeStack()));
    std::string uniqueFileName = SageInterface::generateUniqueVariableName(
        SageBuilder::topScopeStack(), "fp");
    auto fileNameDecl = SageBuilder::buildVariableDeclaration(
        uniqueFileName, file_type, NULL, SageBuilder::topScopeStack());
    //ret.push_back(fileNameDecl);
    SageInterface::appendStatement(fileNameDecl);
    /* 'fp = fopen("datafile", "w");' line of a function call */
    SgExpression *fp = SageBuilder::buildVarRefExp(fileNameDecl);
    SgExprListExp *fopen_arg_list = SageBuilder::buildExprListExp();
    SgStringVal *file_name = SageBuilder::buildStringVal("myDataFile/test.nhd");
    SgStringVal *file_modifier = SageBuilder::buildStringVal(rw_mode);
    SageInterface::appendExpression(fopen_arg_list, file_name);
    SageInterface::appendExpression(fopen_arg_list, file_modifier);
    SgFunctionCallExp *rhs = SageBuilder::buildFunctionCallExp(
        "fopen", file_type, fopen_arg_list, SageBuilder::topScopeStack());
    SgStatement *fopenStmt = SageBuilder::buildAssignStatement(fp, rhs);
    //ret.push_back(fopenStmt);
    SageInterface::appendStatement(fopenStmt);
    /* 'fwrite(&var, sizeof(var), 1, fp);' line of a function call for each
     * global variable */
    //SgSymbolTable *global_tbl = globalscope->get_symbol_table();
    SgType *return_void_type = SageBuilder::buildVoidType();

    for (auto v: global_vars_initName_vec ) {
        SgInitializedName* inv = isSgInitializedName(v);
        std::cout << "GLOBAL:" << inv->unparseToString() << std::endl;
        ParamPassingStyle style = getPassingStyle(inv->get_type(), src_lang_C);
        SgExpression* arg_exp = SageBuilder::buildVarRefExp(inv);
        if (style == ParamPassingStyle::POINTER)
            arg_exp = (SageBuilder::buildAddressOfOp(arg_exp));
        std::cout << "GLOBAL1:" << arg_exp->unparseToString() << std::endl;

        SgExprListExp *fwrt_arg_list = SageBuilder::buildExprListExp();
        SageInterface::appendExpression(fwrt_arg_list, arg_exp);
        SgExprListExp *sizeArg = SageBuilder::buildExprListExp();
        SageInterface::appendExpression(sizeArg, SageBuilder::buildVarRefExp(inv));
        SgFunctionCallExp *sizeFunc = SageBuilder::buildFunctionCallExp("sizeof", SageBuilder::buildUnsignedIntType(), sizeArg);
        SageInterface::appendExpression(fwrt_arg_list, sizeFunc);
        SgIntVal *oneVal = SageBuilder::buildIntVal(1);
        SageInterface::appendExpression(fwrt_arg_list, oneVal);
        SageInterface::appendExpression(fwrt_arg_list, fp); // inserting fp to the list of arguments
        SgExprStatement *fwrt = SageBuilder::buildFunctionCallStmt(rw_call, return_void_type, fwrt_arg_list);
        //ret.push_back(fwrt);
        SageInterface::appendStatement(fwrt);
    }
    /* 'fclose(fp);' line of a function call */
    SgExprListExp *fclose_arg_list = SageBuilder::buildExprListExp();
    SgExpression *filePointer = SageBuilder::buildVarRefExp(fileNameDecl);
    SageInterface::appendExpression(fclose_arg_list, filePointer);
    SgExprStatement *fcloseStmt = SageBuilder::buildFunctionCallStmt(
        SgName("fclose"), return_void_type, fclose_arg_list);
    //ret.push_back(fcloseStmt);
    SageInterface::appendStatement(fcloseStmt);
}


// Assuming parent scope already pushed by SageBuilder::pushScopeStack()
SgBasicBlock* LoopInfo::saveLoopFuncParamAddressesInBB(SgExprStatement *call_expr_stmt) {
    SgBasicBlock* bb = SageBuilder::buildBasicBlock_nfi(SageBuilder::topScopeStack());
    SageBuilder::pushScopeStack(bb);

    for (auto const &stmt : this->saveLoopFuncParamAddresses(call_expr_stmt)) {
        bb->append_statement(stmt);
    }
    SageBuilder::popScopeStack();
    return bb;
}

SgExpression* LoopInfo::getFuncParamAddr(SgInitializedName* func_arg_decl, SgExpression* funcArgument) {
    ParamPassingStyle style = getPassingStyle(func_arg_decl->get_type(), extr.getSrcType());
    /*
     * Three cases:
     * Reference: save address of variable
     * Direct: save the value of the variable (should already be address)
     * Pointer: save address of variable 
     * */
    SgExpression* paramAddress = NULL;
    switch(style) {
        case ParamPassingStyle::REFERENCE:
            paramAddress = (SageBuilder::buildAddressOfOp(funcArgument));
            break;
        case ParamPassingStyle::POINTER:
        case ParamPassingStyle::DIRECT:
            paramAddress = funcArgument;
            break;
    }
    return paramAddress;
}
SgExprListExp* LoopInfo::getSaveCurrentFuncParamAddrArgs(SgExpression* lhs, SgInitializedName* func_arg_decl, SgExpression* funcArgument) {
    SgVarRefExp *varArg = isSgVarRefExp(funcArgument);
    // do we really need this check?
    if (!varArg && !isSgAddressOfOp(funcArgument)) {
        std::cout << "Argument is not a variable expression! \n"
                    << "funcArgument: "
                    << funcArgument->unparseToString()
                    << std::endl;
        return NULL;
    }
    SgExprListExp *fprintf_line_args = SageBuilder::buildExprListExp();
    SageInterface::appendExpression(fprintf_line_args, lhs);
    SgExpression* paramAddress = this->getFuncParamAddr(func_arg_decl, funcArgument);

    SgUnparse_Info unparse_info ;
    unparse_info.set_SkipDefinition();
    SgName arg_name = func_arg_decl->get_name();
    SgPointerType* param_address_type = isSgPointerType(paramAddress->get_type());
    ROSE_ASSERT(param_address_type != NULL);
    std::string fpline1 = "#define SAVED_"+arg_name+" ("+param_address_type->unparseToString(&unparse_info)+ ") 0x%lx \\n"; 
    SgStringVal *lineVal1 = SageBuilder::buildStringVal(fpline1);
    SageInterface::appendExpression(fprintf_line_args, lineVal1);

    SageInterface::appendExpression(fprintf_line_args, paramAddress);
    return fprintf_line_args;
}
/**
 * @brief Function that generates code lines that saves loop function
 *        parameter addresses in a header file
 * @return vector of SgStatement* that contains the generated code lines
 */
vector<SgStatement *> LoopInfo::saveLoopFuncParamAddresses(
    SgExprStatement *call_expr_stmt) {

    vector<SgStatement *> ret;
    SgExprStatement *exprStmt = isSgExprStatement(call_expr_stmt);
    if (exprStmt) {
        SgExpression *expr = exprStmt->get_expression();
        SgFunctionCallExp *funcExpr = isSgFunctionCallExp(expr);
        if (funcExpr) {
            std::string funcName = funcExpr->get_function()->unparseToString();
            auto funcArgs = funcExpr->get_args()->get_expressions();
            int numOfArgs = funcArgs.size();
            if (numOfArgs > 0) {
                /* 'FILE* fp;' line of a function pointer declaration */
                SgType *return_void_type = SageBuilder::buildVoidType();
                auto file_type =
                    SageBuilder::buildPointerType(SageBuilder::buildOpaqueType(
                        "FILE", SageBuilder::topScopeStack()));
                std::string uniqueFileName =
                    SageInterface::generateUniqueVariableName(
                        SageBuilder::topScopeStack(), "fp");
                auto fileNameDecl = SageBuilder::buildVariableDeclaration(
                    uniqueFileName, file_type, NULL,
                    SageBuilder::topScopeStack());
                ret.push_back(fileNameDecl);
                // david fix 
                /* 'fp = fopen("datafile", "w");' line of a function call */
                SgExpression *lhs = SageBuilder::buildVarRefExp(fileNameDecl);
                SgExprListExp *fopen_arg_list = SageBuilder::buildExprListExp();
                SgStringVal *file_name =
                    SageBuilder::buildStringVal("saved_pointers.h");
                SgStringVal *file_modifier = SageBuilder::buildStringVal("w");
                SageInterface::appendExpression(fopen_arg_list, file_name);
                SageInterface::appendExpression(fopen_arg_list, file_modifier);
                SgFunctionCallExp *rhs = SageBuilder::buildFunctionCallExp(
                    "fopen", file_type, fopen_arg_list,
                    SageBuilder::topScopeStack());
                SgStatement *fopenStmt =
                    SageBuilder::buildAssignStatement(lhs, rhs);
                ret.push_back(fopenStmt);
                /* 'fprintf(fp, "#define SAVED_funcArgName (funcArgType*)%lld",
                 * &funcArg);' line of a function call for each loop function
                 * parameter
                 */
                /* Basically two cases
                * For C program, save the parameters passed to function, which should be argument addresses already
                * For C++ program, save the address of the parameters because we pass by reference
                * On replay
                * For C program, pass the saved address as is
                * For C++ program, pass the dereference (*x) as arguments are passed by reference.
                */
                for (int i = 0; i < numOfArgs; i++) {
                    auto funcArgument = funcArgs[i]; 
                    SgInitializedName * func_arg_decl = scope_vars_initName_vec[i];
                    SgExprListExp* fprintf_line_args = this->getSaveCurrentFuncParamAddrArgs(lhs, func_arg_decl, funcArgument);
                    if (fprintf_line_args) {
                        SgExprStatement *fprintf_funccall = SageBuilder::buildFunctionCallStmt( "fprintf", return_void_type, fprintf_line_args);
                        ret.push_back(fprintf_funccall);
                    }
                }
                /* 'fclose(fp);' line of a function call */
                SgExprListExp *fclose_arg_list =
                    SageBuilder::buildExprListExp();
                SgExpression *filePointer =
                    SageBuilder::buildVarRefExp(fileNameDecl);
                SageInterface::appendExpression(fclose_arg_list, filePointer);
                SgExprStatement *fcloseStmt =
                    SageBuilder::buildFunctionCallStmt(
                        SgName("fclose"), return_void_type, fclose_arg_list);
                ret.push_back(fcloseStmt);
            }
        } else
            std::cout << "Something went wrong with funcExpr " << std::endl;
    } else
        std::cout << "SOMETHING WENT WRONG with exprStmt!" << std::endl;
    return ret;
}

/**
 * @brief Function that generates heap saving lines of code
 */
SgStatement *LoopInfo::buildWriteHeap(string datafileName) {
    SgType *return_void_type = SageBuilder::buildVoidType();
    SgStringVal *addDataFile = SageBuilder::buildStringVal(datafileName);
    SgExprListExp *heap_arg_list = SageBuilder::buildExprListExp();
    SgVarRefExp *heap_arg1 =
        SageBuilder::buildVarRefExp(SgName("min_heap_address"));
    SgVarRefExp *heap_arg2 =
        SageBuilder::buildVarRefExp(SgName("max_heap_address"));
    SgVarRefExp *heap_arg3 =
        SageBuilder::buildVarRefExp(SgName("heapPointerData"));
    SageInterface::appendExpression(heap_arg_list, addDataFile);
    SageInterface::appendExpression(heap_arg_list, heap_arg1);
    SageInterface::appendExpression(heap_arg_list, heap_arg2);
    SageInterface::appendExpression(heap_arg_list, heap_arg3);
    SgExprStatement *callStmt = SageBuilder::buildFunctionCallStmt(
        SgName("writeDataRangeToFile"), return_void_type, heap_arg_list);
    return callStmt;
}

/**
 * @brief Function that generates stack saving lines of code
 */
SgStatement *LoopInfo::buildWriteStack(string datafileName) {
    SgType *return_void_type = SageBuilder::buildVoidType();
    SgStringVal *addDataFile = SageBuilder::buildStringVal(datafileName);
    SgExprListExp *stack_arg_list = SageBuilder::buildExprListExp();
    SgVarRefExp *stack_arg1 =
        SageBuilder::buildVarRefExp(SgName("min_stack_address"));
    SgVarRefExp *stack_arg2 =
        SageBuilder::buildVarRefExp(SgName("max_stack_address"));
    SgVarRefExp *stack_arg3 =
        SageBuilder::buildVarRefExp(SgName("stackPointerData"));
    SageInterface::appendExpression(stack_arg_list, addDataFile);
    SageInterface::appendExpression(stack_arg_list, stack_arg1);
    SageInterface::appendExpression(stack_arg_list, stack_arg2);
    SageInterface::appendExpression(stack_arg_list, stack_arg3);
    SgExprStatement *callStmt = SageBuilder::buildFunctionCallStmt(
        SgName("writeDataRangeToFile"), return_void_type, stack_arg_list);
    return callStmt;
}
/**
 * @brief Function that generates code lines that traces segment boundaries
 *        by receiving the addresses of base frame (rbp) and stack frame (rsp)
 * @return vector of SgStatement* that contains the generated code lines
 */
vector<SgStatement *> LoopInfo::buildSegmentPtrs() {
    vector<SgStatement *> segmentPtrs;
    /* Declare 'basepointer' and 'stackpointer' variables */
    SgType *voidType = SageBuilder::buildVoidType();
    SgType *voidPtrType = SageBuilder::buildPointerType(voidType);
    SgVariableDeclaration *basePtrStmt = SageBuilder::buildVariableDeclaration(
        "basepointer", voidPtrType, NULL, SageBuilder::topScopeStack());
    SgVariableDeclaration *stackPtrStmt = SageBuilder::buildVariableDeclaration(
        "stackpointer", voidPtrType, NULL, SageBuilder::topScopeStack());
    segmentPtrs.push_back(basePtrStmt);
    segmentPtrs.push_back(stackPtrStmt);
    /* Get the address of the base pointer by calling
     * '__builtin_frame_address(0)' Get the address of the stack pointer by
     * calling 'alloca(0)'
     */
    SgExprListExp *heap_arg_list = SageBuilder::buildExprListExp();
    auto heap_arg1 = SageBuilder::buildIntVal(0);
    SageInterface::appendExpression(heap_arg_list, heap_arg1);
    SgFunctionCallExp *basePtrCall = SageBuilder::buildFunctionCallExp(
        SgName("__builtin_frame_address"), voidPtrType, heap_arg_list);
    SgFunctionCallExp *stackPtrCall = SageBuilder::buildFunctionCallExp(
        SgName("alloca"), voidPtrType, heap_arg_list);
    /* Assign the result of the function call to the variable */
    SgVarRefExp *basePtrRef = SageBuilder::buildVarRefExp("basepointer");
    SgVarRefExp *stackPtrRef = SageBuilder::buildVarRefExp("stackpointer");
    SgStatement *basePtrAsgn =
        SageBuilder::buildAssignStatement(basePtrRef, basePtrCall);
    SgStatement *stackPtrAsgn =
        SageBuilder::buildAssignStatement(stackPtrRef, stackPtrCall);
    segmentPtrs.push_back(basePtrAsgn);
    segmentPtrs.push_back(stackPtrAsgn);
    return segmentPtrs;
}


/**
 * @brief Function that generates code lines that print some variable
 * @param printStr - first parameter of printf function call (format string)
 * @param variableName - name of the variable to be printed
 * @return generated printf call statement
 */
SgStatement *LoopInfo::buildPrintFunc(std::string printStr, std::string variableName) {

    return this->buildPrintFunc(printStr, SageBuilder::buildVarRefExp(SgName(variableName)));
}
SgStatement *LoopInfo::buildPrintAddrOfFunc(std::string printStr, std::string variableName) {

    return this->buildPrintFunc(printStr, SageBuilder::buildAddressOfOp
        (SageBuilder::buildVarRefExp(SgName(variableName))));
}

SgStatement *LoopInfo::buildPrintFunc(std::string printStr, SgExpression* exp) {
    SgType *return_type = SageBuilder::buildIntType();
    SgExprListExp *arg_list = SageBuilder::buildExprListExp();
    SgStringVal *arg = SageBuilder::buildStringVal(printStr);
    SageInterface::appendExpression(arg_list, arg);
    SageInterface::appendExpression(arg_list, exp);
    SgExprStatement *callStmt1 = SageBuilder::buildFunctionCallStmt(
        SgName("printf"), return_type, arg_list);
    return callStmt1;
}

void TypeDeclTraversal::visit(SgNode * n) {
    if (SgTypedefDeclaration* type_def_decl = isSgTypedefDeclaration(n)) {
        this->visit_if_namedtype(type_def_decl->get_base_type());
        // add this typedef after the base types are added
        type_decl_ios.insert(type_def_decl);
    } else if (SgClassDeclaration* class_decl = isSgClassDeclaration(n)) {
        visit_defining_decl(class_decl);
    } else if (SgInitializedName* in = isSgInitializedName(n)) {
        // std::cout << "initedname:" <<n->unparseToString() << std::endl;
        // std::cout << "typedecl type:" <<decl_type->unparseToString() << std::endl;
        this->visit_if_namedtype(in->get_type());
    } 
}

void TypeDeclTraversal::visit_if_namedtype(SgType * decl_type) {
    SgNamedType* named_exp_type = isSgNamedType(decl_type);
    if (named_exp_type) {
        SgDeclarationStatement* type_decl = named_exp_type->get_declaration();
        //this->visit_defining_decl(type_decl);
        this->visit(type_decl);
    }
}

void TypeDeclTraversal::visit_defining_decl (SgDeclarationStatement* type_decl) {
    type_decl = type_decl->get_definingDeclaration(); // ensure full decl
    if (type_decl_visited.count(type_decl) == 0) {
        type_decl_visited.insert(type_decl);
        // be careful.  Need to create new traversal after inserting visited
        TypeDeclTraversal decl_traversal(*this);
        decl_traversal.traverse(type_decl, postorder);
        // copy out the list and set before end of search
        type_decl_ios = decl_traversal.type_decl_ios;
        type_decl_visited = decl_traversal.type_decl_visited;
        // after traversing all needed declaration, then record this decl
        type_decl_ios.insert(type_decl);
    }
}


void CallTraversal::visit(SgNode * n) {
    SgFunctionCallExp* fn_call = isSgFunctionCallExp(n);
    if (fn_call) {
        SgFunctionRefExp* fn_ref = isSgFunctionRefExp(fn_call->get_function());
        SgFunctionDeclaration* fn_decl = fn_ref->getAssociatedFunctionDeclaration();
        SgFunctionDeclaration* fn_decl_def = isSgFunctionDeclaration(fn_decl->get_definingDeclaration()); // ensure full decl
        fn_decl_s.insert(fn_decl);
        if (fn_decl_def != NULL && fn_defn_visited.count(fn_decl_def) == 0) {
            fn_defn_visited.insert(fn_decl_def); 
            SgBasicBlock* fn_body = fn_decl_def->get_definition()->get_body(); 
            CallTraversal call_traversal(*this); 
            call_traversal.traverse(fn_body, postorder);
            fn_defn_ios = call_traversal.fn_defn_ios;
            fn_defn_visited = call_traversal.fn_defn_visited;
            fn_decl_s = call_traversal.fn_decl_s;
            fn_defn_ios.insert(fn_decl_def);
        }

    }
}

template<class T>
void InsertOrderSet<T>::insert(T e) {
    if (! s.count(e)) {
        // Needed for extracted function extern defn
        s.insert(e); 
        v.push_back(e);
    }
}
/*
 * Take cares of print complete loop function and adding func calls
 * and extern loop func to the base file.
 * Manages SCoP pragmas.
 * Add OMP Timer around the loop. (Not sure)
 * Manages variables that are needed for extracting the loop.
 */
void LoopInfo::printLoopFunc1(string outfile_name, string replay_file_name) {

    /* Scope of loop body contains the variables needed for this loop to compile
     */
    for (vector<SgForStatement *>::iterator iter =
             extr.consecutiveLoops.begin();
         iter != extr.consecutiveLoops.end(); iter++) {
        loop = *iter;
        loop_scope = (loop->get_loop_body())->get_scope();

	/*
        if (hasFuncCallInScope()) {
            string externFuncStr;
            addScopeFuncAsExtern(externFuncStr);
        }
    */

        // getParamatersInFunc - Dont need same analysis twice
        getVarsInScope();
    }
    loop = *(extr.consecutiveLoops.begin());
    loop_scope = (loop->get_loop_body())->get_scope();
    // Function definition


    std::remove(replay_file_name.c_str());
    SgSourceFile* my_restore_src_file = isSgSourceFile(SageBuilder::buildFile(replay_file_name, replay_file_name));
    SgGlobal * glb_restore_src = my_restore_src_file->get_globalScope();
    extr.set_src_file_restore(my_restore_src_file);

    const char* outfile = outfile_name.c_str();
    std::remove(outfile);
    SgProject* project = TransformationSupport::getProject(loop);
    SgSourceFile* src_file_loop = isSgSourceFile(SageBuilder::buildFile(outfile, outfile));
    extr.set_src_file_loop(src_file_loop);

    Sg_File_Info* file_info = src_file_loop->get_file_info();
    SgGlobal * glb_loop_src = src_file_loop->get_globalScope();


    // Check whether calls are called
    CallTraversal call_traversal;
    call_traversal.traverse(loop, postorder);
    TypeDeclTraversal decl_traversal;

    Rose_STL_Container<SgNode *> expList = NodeQuery::querySubTree(loop, V_SgExpression);
    vector<SgDeclarationStatement*>::iterator type_decls_iter;
    for (Rose_STL_Container<SgNode*>::iterator iter = expList.begin(); iter !=expList.end(); iter ++) {
        SgExpression* exp = isSgExpression(*iter);
        SgType* exp_type = exp->get_type();

        // get rid of pointer decls
        while(true) {
            SgPointerType* ptr_type = isSgPointerType(exp_type);
            if (ptr_type) {
                exp_type = ptr_type->get_base_type();
                continue;
            }
            SgArrayType* arr_type = isSgArrayType(exp_type);
            if (arr_type) {
                exp_type = arr_type->get_base_type();
                continue;
            }
            break;  // done getting rid array and pointer types modifiers
        }

        decl_traversal.visit_if_namedtype(exp_type); 
    }
    //for(type_decls_iter=type_decls_v.begin(); type_decls_iter != type_decls_v.end(); type_decls_iter++) {
    vector<SgDeclarationStatement*> type_decls_v1 = decl_traversal.get_type_decl_v();
    for(type_decls_iter=type_decls_v1.begin(); type_decls_iter != type_decls_v1.end(); type_decls_iter++) {
        SgDeclarationStatement* type_decl = isSgDeclarationStatement(SageInterface::deepCopy((*type_decls_iter)));
        SageInterface::appendStatement(type_decl, glb_loop_src);
    }
    this->addGlobalVarDecls(glb_loop_src, true);

    for (auto const& fn_decl : call_traversal.get_fn_decl_s()) {
        auto fn_decl_copy = SageInterface::deepCopy(fn_decl);
        SageInterface::appendStatement(fn_decl_copy, glb_loop_src);
    }
    for (auto const& fn_defn : call_traversal.get_fn_defn_v()) {
        // std::cout << fn_defn->unparseToString() << std::endl;
        auto fn_defn_copy = SageInterface::deepCopy(fn_defn);
        SageInterface::guardNode(fn_defn_copy, RESTORE_GUARD_NAME);
        SageInterface::appendStatement(fn_defn_copy, glb_loop_src);
    }
    SgFunctionDeclaration *fn_decl = this->addLoopFuncDefnDecl(glb_loop_src);


    SgBasicBlock* fn_bb = fn_decl->get_definition()->get_body();

    SageBuilder::pushScopeStack(fn_bb);
    SgPragmaDeclaration* scop_pragma = SageBuilder::buildPragmaDeclaration("scop", SageBuilder::topScopeStack());
    SageInterface::appendStatement(scop_pragma, SageBuilder::topScopeStack());
    SgForStatement* extracted_loop = isSgForStatement(SageInterface::deepCopy(loop));
    // fix loop variable if they were passed by pointer
    vector<SgVariableSymbol *>::iterator iter;
    set<SgVariableSymbol *> fix_vars;
    SgVariableSymbol* last_sym = NULL;
    for (iter = scope_vars_symbol_vec.begin(); iter != scope_vars_symbol_vec.end(); iter++) { 
        SgVariableSymbol* arg_v = (*iter);
        SgType *arg_type = arg_v->get_type();
        ParamPassingStyle style = getPassingStyle(arg_type, extr.getSrcType());
        if (style == ParamPassingStyle::POINTER) {
            // variable passed as pointer of original variable so need to fix them
            fix_vars.insert(arg_v);
            last_sym = arg_v;
        }
    }
    Rose_STL_Container<SgNode *> var_ref_list = NodeQuery::querySubTree(extracted_loop, V_SgVarRefExp);
    for (Rose_STL_Container<SgNode*>::iterator iter = var_ref_list.begin(); 
        iter != var_ref_list.end(); iter ++) {
        SgVarRefExp* v_ref = isSgVarRefExp((*iter));
        SgVariableSymbol* v_sym = v_ref->get_symbol();
        if (fix_vars.count(v_sym) != 0) {
            //fix this by adding a dereference
            SgExpression* new_exp = SageBuilder::buildPointerDerefExp(
                SageBuilder::buildVarRefExp(v_sym));
            SageInterface::replaceExpression(v_ref, new_exp);
        }
    }

    SageInterface::appendStatement(extracted_loop, SageBuilder::topScopeStack());
    SgPragmaDeclaration* end_scop_pragma = SageBuilder::buildPragmaDeclaration("endscop", SageBuilder::topScopeStack());
    SageInterface::appendStatement(end_scop_pragma, SageBuilder::topScopeStack());
    SageBuilder::popScopeStack();

    SageInterface::appendStatement(fn_decl, glb_loop_src);
    
    for(type_decls_iter=type_decls_v1.begin(); type_decls_iter != type_decls_v1.end(); type_decls_iter++) {
        SgDeclarationStatement* type_decl = isSgDeclarationStatement(SageInterface::deepCopy((*type_decls_iter)));
        SageInterface::appendStatement(type_decl, glb_restore_src);
    }
    this->addGlobalVarDecls(glb_restore_src, false);
    SgFunctionDeclaration* func_decl_restore = this->makeLoopFunc(false, glb_restore_src);
    SageInterface::setExtern(func_decl_restore);
    SageInterface::appendStatement(func_decl_restore, glb_restore_src);

    // ROSE "hack" or "feature".  header files including can only be inserted after some declaration was done in a src file.
    SageInterface::insertHeader("unistd.h", PreprocessingInfo::after, true, glb_restore_src);
    SageInterface::insertHeader("replay.h", PreprocessingInfo::after, false, glb_restore_src);
    //SageInterface::insertHeader("saved_pointers.h", PreprocessingInfo::after, false, glb_restore_src);

    /*
    // Create a function declaration for run_loop
    SgFunctionDeclaration *run_loop_decl = SageBuilder::buildNondefiningFunctionDeclaration(
        "run_loop", SageBuilder::buildIntType(), 
        SageBuilder::buildFunctionParameterList(
            SageBuilder::buildInitializedName("call_count", SageBuilder::buildIntType()),
            SageBuilder::buildInitializedName("max_seconds", SageBuilder::buildIntType())), glb_restore_src);

    run_loop_decl->set_linkage("C");
    SageInterface::setExtern(run_loop_decl);
    // Insert the function declaration into the AST
    SageInterface::appendStatement(run_loop_decl, glb_restore_src);
    */


    SgFunctionDeclaration *main_decl = SageBuilder::buildDefiningFunctionDeclaration
        ("run_loop", SageBuilder::buildVoidType(), 
        SageBuilder::buildFunctionParameterList(
            SageBuilder::buildInitializedName("call_count", SageBuilder::buildIntType()),
            SageBuilder::buildInitializedName("max_seconds", SageBuilder::buildIntType())), glb_restore_src);

    //main_decl->set_linkage("C");

    SgBasicBlock* main_fn_bb = main_decl->get_definition()->get_body();
    SgType* void_type = SageBuilder::buildVoidType();
    SgType* void_ptr_type = SageBuilder::buildPointerType(void_type);
    SageBuilder::pushScopeStack(main_fn_bb);

    //auto preRSP_init_name = preRSP_var_decl->get_vardefn();
    //preRSP_init_name->set_register_name_code(SgInitializedName::e_register_sp);
    SgBasicBlock* rep_loop_body = SageBuilder::buildBasicBlock_nfi(main_fn_bb);

    // SgForStatement* rep_loop = SageBuilder::buildForStatement_nfi(
    //     SageBuilder::buildForInitStatement(SageBuilder::buildAssignInitializer_nfi(
    //         SageBuilder::buildAssignOp(SageBuilder::buildVarRefExp("i"), SageBuilder::buildIntVal(0)), SageBuilder::buildIntType())), 
    //     SageBuilder::buildLessThanOp(SageBuilder::buildVarRefExp("i"), SageBuilder::buildVarRefExp("call_count")),
    //     SageBuilder::buildPlusPlusOp(SageBuilder::buildVarRefExp("i")), rep_loop_body);

    SgForStatement* rep_loop = SageBuilder::buildForStatement_nfi(
        SageBuilder::buildForInitStatement(
            SageBuilder::buildVariableDeclaration("i", SageBuilder::buildIntType(), SageBuilder::buildAssignInitializer_nfi(SageBuilder::buildIntVal(0), SageBuilder::buildIntType()), main_fn_bb)), 
        SageBuilder::buildExprStatement(SageBuilder::buildLessThanOp(SageBuilder::buildVarRefExp("i"), SageBuilder::buildVarRefExp("call_count"))),
        SageBuilder::buildPlusPlusOp(SageBuilder::buildVarRefExp("i"), SgUnaryOp::postfix), rep_loop_body);

    SageInterface::appendStatement(rep_loop);

    SageBuilder::pushScopeStack(rep_loop_body);
    auto alarm_call = SageBuilder::buildFunctionCallStmt("alarm", void_type, SageBuilder::buildExprListExp(SageBuilder::buildVarRefExp("max_seconds")));
    SageInterface::appendStatement(alarm_call);
    SageInterface::attachComment(alarm_call, "Set timeout for run");
    int numOfArgs = scope_vars_symbol_vec.size();
    auto void_star_args_decl = SageBuilder::buildVariableDeclaration("args", SageBuilder::buildArrayType(
        SageBuilder::buildPointerType(void_type), SageBuilder::buildIntVal(numOfArgs)));
    SageInterface::appendStatement(void_star_args_decl);
    SageInterface::attachComment(void_star_args_decl, "This array will contain the loop arguments' addresses.");


    int instance_num = 1;
    auto load_call = SageBuilder::buildFunctionCallStmt(
        "load", 
        void_type,
        SageBuilder::buildExprListExp(
            SageBuilder::buildStringVal(getFuncName()),
            SageBuilder::buildIntVal(instance_num),
            SageBuilder::buildIntVal(numOfArgs),
            SageBuilder::buildVarRefExp("args")) 
    );
    SageInterface::appendStatement(load_call);
    SageInterface::attachComment(load_call, "Calling the load function before each call to restore memory to its original state. We are copying the content of the memdump files into our custom ELF sections, and optionally doing some warmup.");


    vector<SgExpression *> expr_list;
    vector<SgVariableSymbol *> saved_scope_vars_symbol_vec;
    for (int i=0 ; i <numOfArgs; i++) {
    //for (iter = scope_vars_symbol_vec.begin(); iter != scope_vars_symbol_vec.end(); iter++) { 
        SgExpression *arg_exp = NULL;
        //SgVariableSymbol* arg_v = (*iter);
        SgVariableSymbol* arg_v = scope_vars_symbol_vec[i];
        // SgVariableSymbol* saved_arg_v = new SgVariableSymbol(
        //     SageBuilder::buildInitializedName(
        //         "SAVED_"+arg_v->get_name(), SageBuilder::buildPointerType(arg_v->get_type())));

        SgType *arg_type = arg_v->get_type();
        ParamPassingStyle style = getPassingStyle(arg_type, extr.getSrcType());

        SgType* saved_v_type = arg_type;
        switch(style) { 
            case ParamPassingStyle::REFERENCE: 
            case ParamPassingStyle::POINTER: 
                saved_v_type = SageBuilder::buildPointerType(saved_v_type);
                break;
            case ParamPassingStyle::DIRECT: 
                // do nothing
                break;
        }

        //arg_exp = SageBuilder::buildPointerDerefExp(SageBuilder::buildVarRefExp(saved_arg_v));
        // For reference types, saved address, so need to dereference
        // For pointer and direct, saved values directly so no need to dereference
        string saved_v_name = "SAVED_"+arg_v->get_name();

        // add variable assignment declaration here
        auto saved_v_decl = SageBuilder::buildVariableDeclaration(
            saved_v_name, saved_v_type, 
            SageBuilder::buildAssignInitializer_nfi(
                SageBuilder::buildCastExp(SageBuilder::buildPntrArrRefExp(SageBuilder::buildVarRefExp("args"), SageBuilder::buildIntVal(i)),
                saved_v_type)));
        SageInterface::appendStatement(saved_v_decl);

        arg_exp = SageBuilder::buildVarRefExp(saved_v_name);
        switch(style) { 
            case ParamPassingStyle::REFERENCE: 
                arg_exp = SageBuilder::buildPointerDerefExp(arg_exp);
                break;
            case ParamPassingStyle::POINTER: 
            case ParamPassingStyle::DIRECT: 
                // do nothing
                break;
        }

        // no extra work for direct and reference type

        ROSE_ASSERT(arg_exp != NULL);
        expr_list.push_back(arg_exp); 
    }

    SgFunctionCallExp *call_expr = SageBuilder::buildFunctionCallExp(
        getFuncName(), SageBuilder::buildVoidType(),
        SageBuilder::buildExprListExp(expr_list), SageBuilder::topScopeStack());
    SageInterface::appendStatement(SageBuilder::buildExprStatement(call_expr));

    SageBuilder::popScopeStack();

    SageBuilder::popScopeStack();
    SageInterface::appendStatement(main_decl, glb_restore_src);
}
/**
 * @brief Function that generates an extern variable declaration of given type 
 * @param varName - name of the variable
 * @param type - type of the variable
 * @return SgVariableDeclaration* that contains the generated variable declaration
 */
SgVariableDeclaration* LoopInfo::buildExternVarDecl(string varName, SgType* type) {
    SgVariableDeclaration* var_decl = SageBuilder::buildVariableDeclaration(varName, type);
    SageInterface::setExtern(var_decl);
    return var_decl;
}
/**
 * @brief Function that generates an extern variable declaration of type char**
 * @param varName - name of the variable
 * @return SgVariableDeclaration* that contains the generated variable declaration
 */
SgVariableDeclaration* LoopInfo::buildExternCharStarStarVarDecl(string varName) {
    return this->buildExternVarDecl(varName, 
        SageBuilder::buildPointerType(SageBuilder::buildPointerType(SageBuilder::buildCharType())));
}
/**
 * @brief Function that generates an extern variable declaration of type int
 * @param varName - name of the variable
 * @return SgVariableDeclaration* that contains the generated variable declaration
 */
SgVariableDeclaration* LoopInfo::buildExternIntVarDecl(string varName) {
    return this->buildExternVarDecl(varName, SageBuilder::buildIntType());
}
/**
 * @brief Function that generates code lines that calls brk function
 *        to get heap address
 * @return vector of SgStatement* that contains the generated code lines
 */
std::vector<SgStatement *> LoopInfo::buildBrkStmt() {
    std::vector<SgStatement *> ret;
    //SgStatement *brkDecl = buildVarDecl("brk", "char*");
    SgVariableDeclaration *brkDecl =
        SageBuilder::buildVariableDeclaration("brk", 
        SageBuilder::buildPointerType(SageBuilder::buildCharType()));
    ret.push_back(brkDecl);
    SgExpression *lhs = SageBuilder::buildVarRefExp("brk");
    SgExprListExp *sbrkArgList = SageBuilder::buildExprListExp();
    SgIntVal *zeroVal = SageBuilder::buildIntVal(0);
    SageInterface::appendExpression(sbrkArgList, zeroVal);
    auto brkType =
        SageBuilder::buildOpaqueType("char*", SageBuilder::topScopeStack());
    SgFunctionCallExp *rhs =
        SageBuilder::buildFunctionCallExp("sbrk", brkType, sbrkArgList);
    SgCastExp *voidToChar = SageBuilder::buildCastExp(rhs, brkType);
    SgStatement *brkAsgn = SageBuilder::buildAssignStatement(lhs, voidToChar);
    ret.push_back(brkAsgn);
    return ret;
}

/**
 * @brief Function that generates code lines to print segment boundary addresses
 *        and imitates the behavior of the SAVE code (to avoid different memory
 * allocation)
 * @return SgStatement* that contains the generated basic block
 */
SgBasicBlock* LoopInfo::addrPrintingInBB() {
    /* Most of code lines will be in a single basic block */
    std::vector<SgStatement *> basicBlockStmts;
    /* Environment variables */
    basicBlockStmts.push_back(buildExternIntVarDecl("_end"));
    basicBlockStmts.push_back(buildExternIntVarDecl("_etext"));
    basicBlockStmts.push_back(buildExternIntVarDecl("_start"));
    basicBlockStmts.push_back(buildExternIntVarDecl("_edata"));
    basicBlockStmts.push_back(buildExternIntVarDecl("__bss_start"));
    basicBlockStmts.push_back(buildExternIntVarDecl("__data_start"));
    basicBlockStmts.push_back(buildExternCharStarStarVarDecl("environ"));
    /* Printing segment boundary addresses */
    vector<SgStatement *> segmentPtrs = buildSegmentPtrs();
    for (int i = 0; i < segmentPtrs.size(); i++) {
        basicBlockStmts.push_back(segmentPtrs[i]);
    }
    std::vector<SgStatement *> brkVec = buildBrkStmt();
    for (int i = 0; i < brkVec.size(); i++) {
        basicBlockStmts.push_back(brkVec[i]);
    }
    basicBlockStmts.push_back(
        buildPrintFunc("BP(INSTANCE): %d\\n", "extr_instance"));
    /*
    basicBlockStmts.push_back(
        buildPrintFunc("BP(OMP_NUM_TH): %d\\n", "omp_get_thread_num()"));
    */
    basicBlockStmts.push_back(
        buildPrintFunc("BP(STACK END): %09lx\\n", "basepointer"));
    basicBlockStmts.push_back(
        buildPrintFunc("SP(STACK BEGIN): %09lx\\n", "((char*)stackpointer)-1"));
    basicBlockStmts.push_back(
        buildPrintAddrOfFunc("DS START: %09lx\\n", "__data_start"));
    basicBlockStmts.push_back(
        buildPrintFunc("DS END: %09lx\\n", "((char*)&_end)-1"));
    basicBlockStmts.push_back(buildPrintAddrOfFunc("HEAP START: %09lx\\n", "_end"));
    basicBlockStmts.push_back(buildPrintFunc("HEAP END: %09lx\\n", "brk"));
    /* Imitation of SAVE code */
    //basicBlockStmts.push_back(buildPrintImitFunc("myDataFile/test"));
    //basicBlockStmts.push_back(buildPrintImitFunc("myDataFile/test"));
    basicBlockStmts.push_back(buildWriteHeap("myDataFile/test"));
    basicBlockStmts.push_back(buildWriteStack("myDataFile/test"));

    SgBasicBlock *result = SageBuilder::buildBasicBlock_nfi(basicBlockStmts);
    return result;
}

void Extractor::addExternDefs(SgFunctionDeclaration *func) {
    externFuncDef.insert(pair<SgStatement *, SgScopeStatement *>(
        dynamic_cast<SgStatement *>(func), loopParentFuncScope));
    // externFuncDef.insert(pair<SgStatement*,SgStatement*>(
    // dynamic_cast<SgStatement *>(func),
    // SageInterface::getFirstStatement(loopParentFuncScope) ));
}

/* Add loop function call as extern in the base source file */
void LoopInfo::addGlobalVarDecls(SgGlobal* glb, bool as_extern) {
    vector<SgInitializedName *>::iterator iter;
    for (iter = global_vars_initName_vec.begin();
            iter != global_vars_initName_vec.end(); iter++) {
        // Create parameter list
        SgName arg_name = (*iter)->get_name();
        //SgInitializedName *arg_init_name;
        SgVariableDeclaration *var_decl;
        var_decl = SageBuilder::buildVariableDeclaration( arg_name, (*iter)->get_type());
        //SageInterface::appendArg(paramList, arg_init_name);
        if (as_extern)
            SageInterface::setExtern(var_decl);
        SageInterface::appendStatement(var_decl , glb);
        //std::cout << "David deArg type unparse 2:" << paramList->unparseToString() << std::endl;
    }
}
/* Add loop function call as extern in the base source file */
SgFunctionDeclaration* LoopInfo::addLoopFuncDefnDecl(SgGlobal* glb) {
    return this->makeLoopFunc(true, glb);
}

SgFunctionDeclaration* LoopInfo::makeLoopFunc(bool defining, SgGlobal* glb) {
    vector<SgInitializedName *>::iterator iter;
    SgFunctionParameterList *paramList =
        SageBuilder::buildFunctionParameterList();
    for (iter = scope_vars_initName_vec.begin();
            iter != scope_vars_initName_vec.end(); iter++) {
        // Create parameter list
        SgName arg_name = (*iter)->get_name();
        SgType *arg_type = (*iter)->get_type();
        SgInitializedName *arg_init_name;

        ParamPassingStyle style = getPassingStyle(arg_type, extr.getSrcType());

        //if (need_addressof_type)
        if (style == ParamPassingStyle::POINTER)
            arg_type = SageBuilder::buildPointerType(arg_type);
        else if (style == ParamPassingStyle::REFERENCE)
            arg_type = SageBuilder::buildReferenceType(arg_type);
        arg_init_name = SageBuilder::buildInitializedName(arg_name, arg_type);

        SageInterface::appendArg(paramList, arg_init_name);
    }
    // Create function declaration
    SgName func_name = getFuncName();
    if (defining)
        return SageBuilder::buildDefiningFunctionDeclaration(func_name, SageBuilder::buildVoidType(), paramList, glb);
    else
        return SageBuilder::buildNondefiningFunctionDeclaration(func_name, SageBuilder::buildVoidType(), paramList, glb);  
}
/* Add loop function call as extern in the base source file */
void LoopInfo::addLoopFuncAsExtern() {
    if (extr.getGlobalNode() != NULL) {
        SgFunctionDeclaration* func = this->makeLoopFunc(false, extr.getGlobalNode());
        SageInterface::setExtern(func);
        // Insert Function into Global scope
        // SageInterface::prependStatement( func, extr.getGlobalNode() );
        extr.addExternDefs(func);
    } else {
        ROSE_ASSERT(extr.getGlobalNode() != NULL);
    }
}

/* Replaces the loop subtree with a function call to corresponding loop function
 */
void LoopInfo::addLoopFuncCall() {
    vector<SgVariableSymbol *>::iterator iter;
    vector<SgExpression *> expr_list;
    for (iter = scope_vars_symbol_vec.begin();
         iter != scope_vars_symbol_vec.end(); iter++) {
        SgExpression *arg_exp = NULL;
        SgType *arg_type = (*iter)->get_type();

        ParamPassingStyle style = getPassingStyle(arg_type, extr.getSrcType());

        arg_exp = (SageBuilder::buildVarRefExp((*iter)));
        if (style == ParamPassingStyle::POINTER)
            arg_exp = (SageBuilder::buildAddressOfOp(arg_exp));
        // no extra work for direct and reference type

        ROSE_ASSERT(arg_exp != NULL);
        expr_list.push_back(arg_exp);
    }
    SgName func_name = getFuncName();
    SgFunctionCallExp *call_expr = SageBuilder::buildFunctionCallExp(
        func_name, SageBuilder::buildVoidType(),
        SageBuilder::buildExprListExp(expr_list), loop_scope);

    /* Check if previous statement is OMP pragma, then remove it */
    SgStatement *prevStmt = SageInterface::getPreviousStatement(loop, false);
    if (prevStmt != NULL && prevStmt->variantT() == V_SgPragmaDeclaration) {
        SgPragmaDeclaration *pragmaDecl =
            dynamic_cast<SgPragmaDeclaration *>(prevStmt);
        if (SageInterface::extractPragmaKeyword(pragmaDecl) == "omp") {
            SageInterface::replaceStatement(
                prevStmt, SageBuilder::buildNullStatement(), true);
        }
    }

    /* Replace for loop with function call - Keep preprocessing info */
    SgExprStatement *call_expr_stmt =
        SageBuilder::buildExprStatement(call_expr);


    // BEGIN Add save stuff here
    SgGlobal* glb_scope = SageInterface::getGlobalScope(loop);
    #if PIN_METHOD
    SageInterface::replaceStatement(loop, call_expr_stmt, true);

    //SgBasicBlock = 
    SageInterface::insertHeader("util.h", PreprocessingInfo::after, false, glb_scope);
    SageInterface::insertHeader("addresses.h", PreprocessingInfo::after, false, glb_scope);
    SageInterface::insertHeader("unistd.h", PreprocessingInfo::after, true, glb_scope);
    SageInterface::insertHeader("omp.h", PreprocessingInfo::after, true, glb_scope);
    string extr_instance_varname = "extr_instance";
    //SgVariableDeclaration* extr_instance_var_decl = SageBuilder::buildVariableDeclaration(
    //    extr_instance_varname, SageBuilder::buildIntType(), NULL, glb_scope);
    SgVariableDeclaration* extr_instance_var_decl = SageBuilder::buildVariableDeclaration_nfi(
        extr_instance_varname, SageBuilder::buildIntType(), 
        SageBuilder::buildAssignInitializer(SageBuilder::buildIntVal(0)), glb_scope);
    SageInterface::prependStatement(extr_instance_var_decl, glb_scope);


    //SgVarRefExp *instVar = SageBuilder::buildVarRefExp(extr_instance_varname, glb_scope);
    SgVarRefExp *instVar = SageBuilder::buildVarRefExp(extr_instance_varname, loop_scope);
    // TODO: should be instanceNum instead of 1
    SgIntVal *oneVal = SageBuilder::buildIntVal(1);
    SgIntVal *zeroVal = SageBuilder::buildIntVal(0);
    //SgIntVal *oneVal1 = SageBuilder::buildIntVal(1);
    SgEqualityOp *instr_cmp = SageBuilder::buildEqualityOp(instVar, oneVal);
    //SgEqualityOp *cmp = SageBuilder::buildEqualityOp(oneVal1, oneVal);
    int mpi_target_rank = 0;
    int omp_target_thread = 0;
    SgFunctionCallExp *chk_omp_mpi = SageBuilder::buildFunctionCallExp(
        "check_omp_mpi_id", SageBuilder::buildIntType(), 
        SageBuilder::buildExprListExp(
            SageBuilder::buildIntVal(omp_target_thread), 
            SageBuilder::buildIntVal(mpi_target_rank)), loop_scope);
    SgStatement *omp_mpi_cond = SageBuilder::buildExprStatement(chk_omp_mpi);
    //SgAndOp* and_op = SageBuilder::buildAndOp(instr_cmp, chk_omp_mpi);
    SgStatement *cond = SageBuilder::buildExprStatement(instr_cmp);

    //vector<SgStatement *> bb_stmts
    SgBasicBlock* if_omp_bb = SageBuilder::buildBasicBlock_nfi(loop_scope);
    SageBuilder::pushScopeStack(if_omp_bb);

    SgBasicBlock* if_bb = SageBuilder::buildBasicBlock_nfi(loop_scope);
    SageBuilder::pushScopeStack(if_bb);
    /* Replace for loop with function call - Keep preprocessing info */

    if_bb->append_statement(this->saveLoopFuncParamAddressesInBB(call_expr_stmt));
    if_bb->append_statement(this->saveGlobalVarsInBB());
    if_bb->append_statement(this->addrPrintingInBB());
    SageBuilder::popScopeStack(); // if_bb

    //SgBasicBlock* if_bb = SageBuilder::buildBasicBlock_nfi(bb_stmts);



    SgIfStmt *instCheck = SageBuilder::buildIfStmt(cond, if_bb, nullptr);
    //SageInterface::replaceStatement(loop, instCheck, true);

    SgVarRefExp *instVar1 = SageBuilder::buildVarRefExp(extr_instance_varname, loop_scope);
    SgPlusPlusOp *incOp = SageBuilder::buildPlusPlusOp(instVar);
    SgStatement *incStmt = SageBuilder::buildExprStatement(incOp);

    //SageInterface::insertStatementAfter(instCheck, incStmt);
    if_omp_bb->append_statement(instCheck);
    if_omp_bb->append_statement(incStmt);
    SageBuilder::popScopeStack(); // if_omp_bb

    SgIfStmt *ompMpiCheck = SageBuilder::buildIfStmt(omp_mpi_cond, if_omp_bb, nullptr);

    SageInterface::insertStatementBefore(call_expr_stmt, ompMpiCheck);



    #else // CERE approach
    // TODO make it parameter
    int instance_num = 1;

    SageInterface::insertHeader("tracee.h", PreprocessingInfo::before, false, glb_scope);

    // END Add save stuff here
    SageInterface::replaceStatement(loop, call_expr_stmt, true);

    int numOfArgs = expr_list.size();
    SgExprListExp* dump_args = SageBuilder::buildExprListExp(
        SageBuilder::buildStringVal(func_name.str()), SageBuilder::buildIntVal(instance_num),
        SageBuilder::buildIntVal(numOfArgs));

    auto funcArgs = call_expr->get_args()->get_expressions();
    for (int i = 0; i < funcArgs.size(); i++) {
        SgExpression* funcArgument = funcArgs[i]; 
        SgInitializedName * func_arg_decl = scope_vars_initName_vec[i];
        SgExpression* dump_arg = this->getFuncParamAddr(func_arg_decl, funcArgument);
        dump_args->append_expression(dump_arg);
    }
    SgExprStatement *dump_call = SageBuilder::buildExprStatement(SageBuilder::buildFunctionCallExp(
        "dump", SageBuilder::buildVoidType(), dump_args, loop_scope));

    SgExprStatement *after_dump_call = SageBuilder::buildExprStatement(SageBuilder::buildFunctionCallExp(
        "after_dump", SageBuilder::buildVoidType(), SageBuilder::buildExprListExp(), loop_scope));
    SageInterface::insertStatementBefore(call_expr_stmt, dump_call);
    SageInterface::insertStatementAfter(call_expr_stmt, after_dump_call);
    #endif

    loop_func_call = call_expr_stmt;
}

/**
 * @brief For each local variable in the loop scope, get the corresponding type
 * @return vector of types of variables in the loop scope
 */
vector<string> LoopInfo::getLoopFuncArgsType() {
    vector<string> args_type;
    vector<SgVariableSymbol *>::iterator iter;
    for (iter = scope_vars_symbol_vec.begin();
         iter != scope_vars_symbol_vec.end(); iter++) {
        args_type.push_back((*iter)->get_type()->unparseToString());
    }
    return args_type;
}

/**
 * @brief For each local variable in the loop scope, get its name
 * @return vector of variable names in the loop scope
 */
vector<string> LoopInfo::getLoopFuncArgsName() {
    vector<string> args_name;
    vector<SgVariableSymbol *>::iterator iter;
    for (iter = scope_vars_symbol_vec.begin();
         iter != scope_vars_symbol_vec.end(); iter++) {
        // cout << "Loop func arg: " << (*iter)->get_name().str() << endl;
        args_name.push_back((*iter)->get_name().str());
    }
    return args_name;
}

bool Extractor::skipLoop(SgNode *astNode) {
    // TODO: may need to include filename
    if (extracted.count(lineNumbers) > 0)
        return true;
    if (!loopSkipPragma.empty() &&
        loopSkipPragma.find(LoopExtractor_skiplooppragma_str) != string::npos) {
        loopSkipPragma = "";
        return true;
    }
    SgForStatement *loop = dynamic_cast<SgForStatement *>(astNode);
    SgScopeStatement *scope = (loop->get_loop_body())->get_scope();
    Rose_STL_Container<SgNode *> returnStmt =
        NodeQuery::querySubTree(scope, V_SgReturnStmt);
    if (returnStmt.begin() != returnStmt.end())
        return true;

    /* Skip loop with macro def in the body, Rose will extract the first
     * instance of complete loop */
    string loop_body_orig = loop->unparseToString();
    string loop_body =
        loop_body_orig.substr(loop_body_orig.find_first_of("for"));
    if (loop_body.find("#if") != string::npos ||
        loop_body.find("#else") != string::npos ||
        loop_body.find("#endif") != string::npos) {
        int count_if = 0;
        string sub = "#if";
        for (size_t offset = loop_body.find(sub); offset != string::npos;
             offset = loop_body.find(sub, offset + sub.length()))
            ++count_if;
        int count_endif = 0;
        sub = "#endif";
        for (size_t offset = loop_body.find(sub); offset != string::npos;
             offset = loop_body.find(sub, offset + sub.length()))
            ++count_endif;
        if (count_if != count_endif)
            return true;
    }

    Rose_STL_Container<SgNode *> gotoStmt =
        NodeQuery::querySubTree(scope, V_SgGotoStatement);
    if (gotoStmt.begin() != gotoStmt.end())
        return true;

    /* If calls a static function */
    Rose_STL_Container<SgNode *> funcCallList =
        NodeQuery::querySubTree(scope, V_SgFunctionCallExp);
    Rose_STL_Container<SgNode *>::iterator funcCallIter = funcCallList.begin();
    for (; funcCallIter != funcCallList.end(); funcCallIter++) {
        SgFunctionCallExp *funcCallExp = isSgFunctionCallExp(*funcCallIter);
        SgFunctionDeclaration *funcDecl =
            funcCallExp->getAssociatedFunctionDeclaration();
        if (funcDecl != NULL && SageInterface::isStatic(funcDecl))
            return true;
        if (funcDecl != NULL &&
            find(static_funcs_vec.begin(), static_funcs_vec.end(),
                 string(funcDecl->get_name())) != static_funcs_vec.end())
            return true;
    }

    /* If uses a static variable */
    vector<SgVarRefExp *> sym_table;
    SageInterface::collectVarRefs(dynamic_cast<SgLocatedNode *>(astNode),
                                  sym_table);
    vector<SgVarRefExp *>::iterator iter;
    for (iter = sym_table.begin(); iter != sym_table.end(); iter++) {
        SgVariableSymbol *var = (*iter)->get_symbol();
        SgDeclarationStatement *var_decl =
            (var->get_declaration())->get_declaration();
        if (var_decl != NULL && SageInterface::isStatic(var_decl))
            return true;
    }

    return false;
}
void Extractor::reportOutputFiles() {
    // parse loop_file_name and do fprintf to tmp/loopFileNames.txt
    string loop_file_name, base_file_name, restore_file_name;
    if (src_file_loop) {
        loop_file_name = src_file_loop->get_file_info()->get_filenameString();
    }
    if (src_file_restore) {
        restore_file_name = src_file_restore->get_file_info()->get_filenameString();
    }

    base_file_name = getDataFolderPath() + getBaseFileName();

    cout << "LOOP_FILE_NAME: " << loop_file_name << endl;
    cout << "BASE_FILE_NAME: " << base_file_name << endl;
    cout << "RESTORE_FILE_NAME: " << restore_file_name << endl;
    loop_file_name = parseFileName(&loop_file_name);
    base_file_name = parseFileName(&base_file_name);
    restore_file_name = parseFileName(&restore_file_name);
    cout << "PARSED loop_file_name: " << loop_file_name << endl;
    cout << "PARSED base_file_name: " << base_file_name << endl;
    cout << "PARSED restore_file_name: " << restore_file_name << endl;
    string report_file = getDataFolderPath() + "loopFileNames.txt";
    /*
    FILE *tmp_fp = fopen(report_file, "w"); //"./loopFileNames.txt", "w");
    fprintf(tmp_fp, "%s\n%s\n%s\n", base_file_name.c_str(), loop_file_name.c_str(), restore_file_name.c_str());
    fclose(tmp_fp);
    */
    ofstream info_file(report_file);
    info_file << base_file_name << endl << loop_file_name << endl << restore_file_name << endl;
    info_file.close();
    cout << "Output file info: " << report_file << endl;

}

/**
 * @brief Most important function in the extractor, it will extract the loop
 *        body and create a new function
 * @param astNode The loop to be extracted
 */
void Extractor::extractLoops(SgNode *astNode) {
    Sg_File_Info* file_info = astNode->get_file_info();
    string file_name = file_info->get_filenameString();
    int lineNum = file_info->get_line();
    /*
    cout << "line number of ast node: " << astNode->unparseToString() << endl;
    cout << "is " << lineNum << endl;
    */

    /* Here we check if loop file number is the one we need */
    if (file_name == targetfilename && lineNum >= lineNumbers.first && lineNum <= lineNumbers.second) {
        // cout << "PASSED the lineNum check" << endl;
        SgForStatement *loop = dynamic_cast<SgForStatement *>(astNode);
        updateUniqueCounter(astNode);
        string output_path = getDataFolderPath();
        string loop_file_name = output_path + getExtractionFileName(astNode);
        string replay_loop_file_name = output_path + getReplayFileName(astNode);

        //ofstream loop_file_buf;
        //loop_file_buf.open(loop_file_name.c_str(), ofstream::out);

        files_to_compile.insert(loop_file_name);


        // Create loop object
        LoopInfo curr_loop(astNode, loop, getLoopName(astNode), *this);

        /*
         * Take cares of print complete loop function and adding func calls
         * and extern loop func to the base file.
         */
        curr_loop.printLoopFunc1(loop_file_name, replay_loop_file_name);
        curr_loop.addLoopFuncCall();
        curr_loop.addLoopFuncAsExtern();

        // to replace remaining consecutive loops with null statements */
        if (consecutiveLoops.size() > 1) {
            vector<SgForStatement *>::iterator iter = consecutiveLoops.begin();
            iter++; // First loop is already removed by addLoopFuncCall()
            for (; iter != consecutiveLoops.end(); iter++) {
                SageInterface::replaceStatement(
                    (*iter), SageBuilder::buildNullStatement(), false);
            }
        }
        // set it done after extraction
        extracted.insert(lineNumbers);
    }

}

void Extractor::collectAdjoiningLoops(SgStatement *loop) {
    if (loop == NULL)
        return;
    // cout << "Loop: " << loop->class_name() << endl <<
    // loop->unparseToCompleteString() << endl;
    consecutiveLoops.push_back(dynamic_cast<SgForStatement *>(loop));
    SgStatement *nextStmt = SageInterface::getNextStatement(loop);
    if (nextStmt && nextStmt->variantT() &&
        nextStmt->variantT() == V_SgForStatement) {
        collectAdjoiningLoops(nextStmt);
    } else {
        return;
    }
    return;
}

void Extractor::extractFunctions(SgNode *astNode) {}

/* Required for Top Down parsing
 *  This function is called for each node in the AST inside of
 * traverseInputFiles function.
 */
InheritedAttribute
Extractor::evaluateInheritedAttribute(SgNode *astNode,
                                      InheritedAttribute inh_attr) {
    /* If condition so that Post traversal doesn't mess up extractor changes to
     * the graph */
    if (astNodesCollector.find(astNode) == astNodesCollector.end()) {
        astNodesCollector.insert(astNode);
        switch (astNode->variantT()) {
        case V_SgForStatement: {
            SgForStatement *loop = dynamic_cast<SgForStatement *>(astNode);
            if (loop == NULL) {
                // cerr << "Error: incorrect loop node type" << endl;
                break;
            }
            ++inh_attr.loop_nest_depth_;
            // cerr << "Found node: " << loop->class_name() << " with depth: "
            // << inh_attr.loop_nest_depth_ << endl;
            // TODO: Upto what loop depth to extract as tool option
            //if (inh_attr.loop_nest_depth_ < 2) {
            if (inh_attr.loop_nest_depth_ < 20) {
                // cerr << "Extracting loop now" << endl;
                // if( SageInterface::getNextStatement(loop)->variantT() != NULL
                // && SageInterface::getNextStatement(loop)->variantT() ==
                // V_SgForStatement
                // )
                if (!skipLoop(astNode)) {
                    if (LoopExtractor_enabled_options[EXTRACTKERNEL])
                        collectAdjoiningLoops(
                            dynamic_cast<SgStatement *>(astNode));
                    else
                        consecutiveLoops.push_back(
                            dynamic_cast<SgForStatement *>(astNode));
                    extractLoops(astNode);
                }
                consecutiveLoops.clear(); // Clear vector for next kernel
                loopOMPpragma = "";
            }
            break;
        }
        case V_SgFunctionDeclaration: {
            /* Collect all extern functions in this file */
            SgFunctionDeclaration *declFunc =
                dynamic_cast<SgFunctionDeclaration *>(astNode);
            SgFunctionModifier declModf = declFunc->get_functionModifier();

            /* Inline function are copied to be put in loops files where
               neccesary Function body is present only here through function
               declaration. */
            if (declModf.isInline()) {
                string inline_func_str = declFunc->unparseToString() + '\n';
                inline_func_map.insert(pair<SgFunctionDeclaration *, string>(
                    declFunc, inline_func_str));
            }

            if (SageInterface::isExtern(declFunc)) {
                header_vec.push_back(declFunc->unparseToString() + '\n');
            }

            if (SageInterface::isMain(astNode)) {
                mainFuncPresent = true;
                main_scope = dynamic_cast<SgScopeStatement *>(
                    (declFunc->get_definition())->get_body());
            }
            // getVarsInFunction(astNode);

            break;
        }
        case V_SgFunctionDefinition: {
            loopParentFuncScope = dynamic_cast<SgScopeStatement *>(astNode);
            SgFunctionDefinition *funcDef =
                dynamic_cast<SgFunctionDefinition *>(astNode);
            if (funcDef != NULL &&
                ((funcDef->unparseToString()).find("static") <
                 (funcDef->unparseToString())
                     .find(funcDef->get_declaration()->get_name())))
                static_funcs_vec.push_back(
                    funcDef->get_declaration()->get_name());
            break;
        }
        case V_SgGlobal: {
            global_node = isSgGlobal(astNode);
            break;
        }
        case V_SgPragmaDeclaration: {
            SgPragmaDeclaration *pragmaDecl =
                dynamic_cast<SgPragmaDeclaration *>(astNode);
            if (SageInterface::extractPragmaKeyword(pragmaDecl) == "omp") {
                SgPragma *pragmaNode = pragmaDecl->get_pragma();
                string pragmaString = pragmaNode->get_pragma();
                if (pragmaString.find("parallel") == string::npos &&
                    pragmaString.find("threadprivate") != string::npos) {
                    global_vars.push_back("#pragma " + pragmaString);
                    global_var_names.push_back(pragmaString);
                    //          } else if( pragmaString.find("parallel") !=
                    //          string::npos
                    //          &&
                    //                     pragmaString.find("for") ==
                    //                     string::npos ){
                    //            /* Do nothing since it should be covered in a
                    //            base file or inside the body of loop */
                } else if (pragmaString.find("for") != string::npos) {
                    /* Should only be concerned with 'for' directive,
                     * every other directive remains where they are.
                     * i.e. either in base file or inside the loop */
                    loopOMPpragma = "#pragma " + pragmaString;
                }
            }
            if (SageInterface::extractPragmaKeyword(pragmaDecl) == "LE") {
                SgPragma *pragmaNode = pragmaDecl->get_pragma();
                string pragmaString = pragmaNode->get_pragma();
                loopSkipPragma = "#pragma " + pragmaString;
            }

            break;
        }
        case V_SgReturnStmt: {
            SgStatement *returnstmt = dynamic_cast<SgStatement *>(astNode);
            break;
        }
        case V_SgTypedefDeclaration: {
            header_vec.push_back(astNode->unparseToString() + "\n");
            SgTypedefDeclaration *typedef_decl =
                dynamic_cast<SgTypedefDeclaration *>(astNode);
            if (typedef_decl->get_base_type()->variantT() == V_SgClassType) {
                typedef_struct_lineno_vec.push_back(getAstNodeLineNum(astNode));
            }
            break;
        }
        case V_SgClassDeclaration: {
            SgClassDeclaration *structC_decl =
                dynamic_cast<SgClassDeclaration *>(astNode);
            if (find(typedef_struct_lineno_vec.begin(),
                     typedef_struct_lineno_vec.end(),
                     getAstNodeLineNum(astNode)) ==
                typedef_struct_lineno_vec.end()) {
                header_vec.push_back(astNode->unparseToString() + "\n");
            }
            break;
        }
        //			case V_SgSourceFile: {
        /* add LoopExtractor header file into the source */
        //				SgSourceFile *sourceFile =
        // dynamic_cast<SgSourceFile
        //*>(astNode);
        //				SageInterface::insertHeader(sourceFile,
        // LoopExtractor_header_name, false, false);
        // break;
        //			}
        default: {
            // cerr << "Found node: " << astNode->class_name() << endl;
        }
        }

        /* For gathering the header files */
        SgLocatedNode *locatedNode = isSgLocatedNode(astNode);
        if (locatedNode != NULL) {
            SgStatement *locatedNode_SgStatement =
                dynamic_cast<SgStatement *>(astNode);
            AttachedPreprocessingInfoType *directives =
                locatedNode->getAttachedPreprocessingInfo();
            if (directives != NULL && locatedNode_SgStatement &&
                isSgGlobal(locatedNode_SgStatement->get_scope())) {
                /* Dirty trick to push a node like extern func after headers,
                 * since control flow get here after the node was pushed already
                 */
                string vector_top;
                if (!header_vec.empty()) {
                    vector_top = header_vec.back();
                    if (vector_top.find("#") == 0) {
                        vector_top = "";
                    } else
                        header_vec.pop_back();
                }
                AttachedPreprocessingInfoType::iterator i;
                for (i = directives->begin(); i != directives->end(); i++) {
                    string directiveTypeName =
                        PreprocessingInfo::directiveTypeName(
                            (*i)->getTypeOfDirective())
                            .c_str();
                    string headerName = (*i)->getString().c_str();
                    // cerr << "Header Type: " << directiveTypeName << endl;
                    // #include
                    if (directiveTypeName ==
                            "CpreprocessorIncludeDeclaration" &&
                        find(header_vec.begin(), header_vec.end(),
                             headerName) == header_vec.end()) {
                        header_vec.push_back(headerName);
                        /* If including a .c file then copy to LE data folder */
                        if (headerName.find(".c") != string::npos) {
                            copysourcefiles = true;
                        }
                        lastIncludeStmt = locatedNode_SgStatement;
                        // cerr << "Header: " << headerName << endl;
                    }
                    // #define
                    if (directiveTypeName == "CpreprocessorDefineDeclaration" &&
                        find(header_vec.begin(), header_vec.end(),
                             headerName) == header_vec.end()) {
                        header_vec.push_back(headerName);
                        // cerr << "Header: " << headerName << endl;
                    }
                    // #ifdef
                    if (directiveTypeName == "CpreprocessorIfdefDeclaration") {
                        header_vec.push_back(headerName);
                        // cerr << "Header: " << headerName << endl;
                    }
                    // #ifndef
                    if (directiveTypeName == "CpreprocessorIfndefDeclaration") {
                        header_vec.push_back(headerName);
                        // cerr << "Header: " << headerName << endl;
                    }
                    // #if
                    if (directiveTypeName == "CpreprocessorIfDeclaration") {
                        header_vec.push_back(headerName);
                        // cerr << "Header: " << headerName << endl;
                    }
                    // #else
                    if (directiveTypeName == "CpreprocessorElseDeclaration") {
                        header_vec.push_back(headerName);
                        // cerr << "Header: " << headerName << endl;
                    }
                    // #endif
                    if (directiveTypeName == "CpreprocessorEndifDeclaration") {
                        header_vec.push_back(headerName);
                        // cerr << "Header: " << headerName << endl;
                    }
                }
                if (!vector_top.empty())
                    header_vec.push_back(vector_top);
            }
        }

        /* Gather the global variables/static data member names */
        SgVariableDeclaration *variableDeclaration =
            isSgVariableDeclaration(astNode);
        if (variableDeclaration != NULL) {
            // Typically just one InitializedName in a VariableDecl, but still
            SgInitializedNamePtrList::iterator i =
                variableDeclaration->get_variables().begin();
            while (i != variableDeclaration->get_variables().end()) {
                SgInitializedName *initializedName = *i;
                if (initializedName != NULL) {
                    // Get Type for the variable
                    SgType *variableType = initializedName->get_type();
                    string var_type_str = variableType->unparseToString();
                    // Now check if this is a global variable or an static class
                    // member
                    SgScopeStatement *scope = variableDeclaration->get_scope();
                    if (isSgGlobal(scope) != NULL) {
                        string var_str =
                            initializedName->get_name().getString();
                        // cerr << "Found a global var: " << var_type_str + " "
                        // + var_str << endl;
                        if (variableType->variantT() == V_SgArrayType) {
                            /* To change to var_type var_name[][][] */
                            int first_square_brac =
                                var_type_str.find_first_of("[");
                            if (first_square_brac != string::npos)
                                global_vars.push_back(
                                    var_type_str.substr(0, first_square_brac) +
                                    var_str +
                                    var_type_str.substr(first_square_brac));
                            global_var_names.push_back(
                                initializedName->get_name().getString());
                        } else {
                            /* Bcoz Rose add wierd stuff like
                             * __PRETTY_FUNCTION__ on assert() calls */
                            if (var_str.find(ignorePrettyFunctionCall1) ==
                                    string::npos &&
                                var_str.find(ignorePrettyFunctionCall2) ==
                                    string::npos &&
                                var_str.find(ignorePrettyFunctionCall3) ==
                                    string::npos)
                                global_vars.push_back(var_type_str + " " +
                                                      var_str);
                            global_var_names.push_back(
                                initializedName->get_name().getString());
                        }
                        // lastIncludeStmt = dynamic_cast<SgStatement
                        // *>(astNode);
                    }
                    if (isSgClassDefinition(scope) != NULL) {
                        // Now check if it is a static data member
                        if (variableDeclaration->get_declarationModifier()
                                .get_storageModifier()
                                .isStatic() == true) {
                            // cerr << "Found a static global var: " <<
                            // var_type_str + " " +
                            // initializedName->get_name().getString() << endl;
                            global_vars.push_back(
                                var_type_str + " " +
                                initializedName->get_name().getString());
                            global_var_names.push_back(
                                initializedName->get_name().getString());
                            // lastIncludeStmt = dynamic_cast<SgStatement
                            // *>(astNode);
                        }
                    }
                }
                i++;
            }
        }
    } else {
        cout << "In Post traversal, generally shouldn't come here." << endl;
        /* If Post AST traversal */
        switch (astNode->variantT()) {
        case V_SgGlobal: {
            cout << "At Post traversal Global Node" << endl;
            addPostTraversalDefs();
            // global_node = isSgGlobal(astNode);
        }
        }
    }
    return inh_attr;
}

/* Required for Bottom Up parsing virtual function - Will not be used */
int Extractor::evaluateSynthesizedAttribute(
    SgNode *astNode, InheritedAttribute inh_attr,
    SubTreeSynthesizedAttributes syn_attr_list) {
    return 0;
}

void Extractor::addPostTraversalDefs() {
    for (std::map<SgStatement *, SgScopeStatement *>::iterator it =
             externFuncDef.begin();
         it != externFuncDef.end(); ++it) {
        BOOST_FOREACH (SgStatement *targetStmt,
                       (it->second)->generateStatementList()) {
            if (!isSgDeclarationStatement(targetStmt) ||
                targetStmt->variantT() == V_SgPragmaDeclaration) {
                SageInterface::insertStatementBefore(targetStmt, it->first);
                goto NEXTSTMT;
            }
        }
        SageInterface::appendStatement(it->first, it->second);
    NEXTSTMT:;
    }
    // SageInterface::insertStatementListBeforeFirstNonDeclaration (
    // externLoopFuncDefinitionsAdd, getLastIncludeStatement()->get_scope() );
    //    SageInterface::insertStatementBeforeFirstNonDeclaration ( it->first,
    //    it->second );
    //    SageInterface::insertStatementBefore(it->second, it->first,true);
    /* LastIncludeStatement point to either last include or global var declr
     * Due to bug in rosem insert After on include statement skip the next
     * subtree
     */
    /*if( getLastIncludeStatement() != NULL ){
            if( isSgVariableDeclaration( getLastIncludeStatement() ) != NULL ||
    isSgTypedefDeclaration( getLastIncludeStatement() ) != NULL )
                    SageInterface::insertStatementListAfter(
    getLastIncludeStatement(), externLoopFuncDefinitionsAdd );
            else
                    SageInterface::insertStatementListBefore(
    getLastIncludeStatement(), externLoopFuncDefinitionsAdd );

    } else {
            SageInterface::appendStatementList( externLoopFuncDefinitionsAdd,
    getGlobalNode() );
    }*/
}

void Extractor::modifyExtractedFileText(const string &base_file) {
    /* Remove static keyword from variables and functions in file */
    /*	string sed_command1 = "sed -i 's/static //g' " + base_file;
            executeCommand( sed_command1 );
            sed_command1 = "sed -i 's/inline //g' " + base_file;
            executeCommand( sed_command1 );
    */
    /* Remove register keyword from variables and functions in both profile file
     */
    string sed_command2 = "sed -i 's/register //g' " + base_file;
    executeCommand(sed_command2);

    /* Remove OMP pragma from file bcoz ROSE APIs can't */
    /*sed_command2 = "sed -i '/omp parallel for/d' " + base_file;
            executeCommand( sed_command2 );
            sed_command2 = "sed -i '/omp for/d' " + base_file;
            executeCommand( sed_command2 );
    */
}

// void Extractor::inlineFunctions(const vector<string> &argv) {
//     bool frontendConstantFolding = true;
//     SgProject *project = new SgProject(argv);
//     ConstantFolding::constantFoldingOptimization(project);
//     AstTests::runAllTests(project);
//     bool modifiedAST = true;
//     int count = 0;
//     do {
//         modifiedAST = false;
//         Rose_STL_Container<SgNode *> functionCallList =
//             NodeQuery::querySubTree(project, V_SgFunctionCallExp);
//         // Loop over all function calls
//         Rose_STL_Container<SgNode *>::iterator i = functionCallList.begin();
//         while (modifiedAST == false && i != functionCallList.end()) {
//             SgFunctionCallExp *functionCall = isSgFunctionCallExp(*i);
//             ROSE_ASSERT(functionCall != NULL);
//             // Not all function calls can be inlined in C, so report if
//             // successful.
//             bool sucessfullyInlined = doInline(functionCall);
//             if (sucessfullyInlined == true) {
//                 // As soon as the AST is modified recompute the list of function
//                 // calls (and restart the iterations over the modified list)
//                 modifiedAST = true;
//                 cout << "Function inlined" << endl;
//             } else {
//                 modifiedAST = false;
//             }
//             // Increment the list iterator
//             i++;
//         }
//         // Quite when we have ceased to do any inline transformations
//         // and only do a predefined number of inline transformations
//         count++;
//     } while (modifiedAST == true && count < 10);
//     // Adding check for isTransformed flag consistancy.
//     cout << "AST check 1" << endl;
//     checkTransformedFlagsVisitor(project);
//     // Call function to postprocess the AST and fixup symbol tables
//     cout << "AST check 2" << endl;
//     // FixSgProject(*project);
//     // Rename each variable declaration
//     cout << "AST check 3" << endl;
//     renameVariables(project);
//     // Fold up blocks
//     cout << "AST check 4" << endl;
//     flattenBlocks(project);
//     // Adding check for isTransformed flag consistancy.
//     cout << "AST check 5" << endl;
//     checkTransformedFlagsVisitor(project);
//     // Clean up inliner-generated code
//     cout << "AST check 6" << endl;
//     cleanupInlinedCode(project);
//     // Adding check for isTransformed flag consistancy.
//     cout << "AST check 7" << endl;
//     checkTransformedFlagsVisitor(project);
//     // Change members to public
//     cout << "AST check 8" << endl;
//     changeAllMembersToPublic(project);
//     // Adding check for isTransformed flag consistancy.
//     cout << "AST check 9" << endl;
//     checkTransformedFlagsVisitor(project);
//     backend(project);
// }
SgExprStatement* Extractor::buildSimpleFnCallStmt(string fnName, SgScopeStatement* scope) {
    return SageBuilder::buildExprStatement(SageBuilder::buildFunctionCallExp(
        fnName, SageBuilder::buildVoidType(), SageBuilder::buildExprListExp(), scope));
}
void Extractor::instrumentMain() {
    if (main_scope) {
        SgGlobal* glb_scope = SageInterface::getGlobalScope(main_scope);
        SgFunctionDefinition* main_defn = isSgFunctionDefinition(main_scope->get_parent());
        assert(main_defn);
        //SageInterface::insertHeader(main_defn, SageBuilder::buildHeader("tracee.h"), false);
        SageInterface::insertHeader("tracee.h", PreprocessingInfo::after, false, glb_scope);

        SgExprStatement *dump_init_call = buildSimpleFnCallStmt("dump_init", main_scope);
        SageInterface::prependStatement(dump_init_call, main_scope);
        // insertion of dump_close() call is a bit more tricky as we need to insert them before return statements too
        for (auto n : NodeQuery::querySubTree(main_scope, V_SgReturnStmt)) {
            SgReturnStmt* retStmt = isSgReturnStmt(n);
            SgExprStatement *dump_close_call = buildSimpleFnCallStmt("dump_close", main_scope);
            SageInterface::insertStatementBefore(retStmt, dump_close_call);
        }
        SgExprStatement *dump_close_call = buildSimpleFnCallStmt("dump_close", main_scope);
        SageInterface::appendStatement(dump_close_call, main_scope);
    }

}
void Extractor::do_extraction() {
    //this->tr = tr;

    SgProject *ast = NULL;
    /* Create AST and pass to the extraction functions */
    ast = frontend(filenameVec);
    ROSE_ASSERT(ast != NULL);
    InheritedAttribute inhr_attr;
    /* Traverse all files and their ASTs in Top Down fashion (Inherited Attr)
     * and extract loops */

    this->traverseInputFiles(ast, inhr_attr);
    // after traversing, main scope will be found
    this->instrumentMain();
    // this->generateHeaderFile();
    this->addPostTraversalDefs();
    //SgFile* my_file = SageBuilder::buildFile("/tmp/foo12.cc", "/tmp/foo12.cc");
    if (src_file_loop)
        ast->get_fileList().push_back(src_file_loop);
    if (src_file_restore)
        ast->get_fileList().push_back(src_file_restore);

    AstPostProcessing(ast);
    AstTests::runAllTests(ast);
    /* Generate rose_<orig file name> file for the transformed AST */
    ast->unparse();
    delete ast;

    /* If file doesn't have any loop, then LoopExtractor_file_name,_file_extn
     * would be empty at this point */
    if (LoopExtractor_file_name.empty()) {
        LoopExtractor_file_path = getFilePath(filenameVec.back());
        LoopExtractor_original_file_name = getOrigFileName(filenameVec.back());
        LoopExtractor_file_extn = getFileExtn(filenameVec.back());
    }
    string base_file = getDataFolderPath() + getBaseFileName();

    if (LoopExtractor_file_name.empty() && !mainFuncPresent) {
        /* Copy original file to the LoopExtractor data folder:
         * cp filename.x LoopExtractor_data/filename_base.x
         * rm rose_filename.x
         */
        executeCommand("cp " + filenameVec.back() + space_str + base_file);
        executeCommand("rm rose_" + getOrigFileName() + "." + getFileExtn());
    } else {
        /* Move base file to the LoopExtractor data folder:
         * mv rose_filename.x LoopExtractor_data/filename_base.x
         */
        executeCommand("mv rose_" + getOrigFileName() + "." + getFileExtn() +
                       space_str + base_file);
    }
    // modifyExtractedFileText(base_file);
    this->reportOutputFiles();

    files_to_compile.insert(base_file);
    /* After in-situ extraction is finished, all files are in the
     * LoopExtractor_data folder. Now, we need to compile them and link them
     * with the original file to generate the final executable.
     */

    /* All generated during the in-situ extraction process file names should
     *  be transferred to the Tracer
     */
    std::string loopExtrIncludeFlag = "-I";
    loopExtrIncludeFlag += LoopExtractor_curr_dir_path;
    // loopExtrIncludeFlag += forward_slash_str;
    loopExtrIncludeFlag += LoopExtractor_data_folder;
    //tr->setLoopExtrIncludeFlag(loopExtrIncludeFlag);

    string baseFileName = LoopExtractor_curr_dir_path +
                          LoopExtractor_data_folder + forward_slash_str +
                          getBaseFileName();
}

/* Extractor constructor, for initiating via driver */
//Extractor::Extractor(const vector<string> &argv, Tracer *tr) {
Extractor::Extractor(const vector<string> &argv) {
    filenameVec = argv;
    /* Get relative path unique code */
    if (LoopExtractor_input_file_relpathcode.find(argv.back()) !=
            LoopExtractor_input_file_relpathcode.end() &&
        !(LoopExtractor_input_file_relpathcode.find(argv.back())->second)
             .empty())
        relpathcode =
            LoopExtractor_input_file_relpathcode.find(argv.back())->second;

    if (LoopExtractor_enabled_options[STATICANALYSIS]) {
        // inlineFunctions(argv); // Has bugs bcoz of rose implementation
    }

}
