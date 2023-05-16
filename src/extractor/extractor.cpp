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
    ParamPassingStyle style = getPassingStyle(func_arg_decl->get_type(), extr->getSrcType());
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
        SgType* bt = type_def_decl->get_base_type();
        if (type_decl_visited.count(type_def_decl) == 0) {
            mark_decl_visited(type_def_decl);
            SgName typedef_name = type_def_decl->get_name();
            if (typedef_name.getString() == "__builtin_va_list") {
                return; // skip builtin va_list type
            }
            if (isSgClassType(bt) 
                && isSgClassType(bt)->get_declaration()->get_definingDeclaration() 
                && isSgGlobal(isSgClassType(bt)->get_declaration()->get_definingDeclaration()->get_parent())) {
                SgClassType* ct = isSgClassType(bt);
                //add_decl(type_def_decl);
                add_decl(SageBuilder::buildTypedefDeclaration(typedef_name.getString(), ct, global_scope));
                this->visit_if_namedtype(bt);
            } else {
                cout << "visiting: " << typedef_name.getString() << endl;
                this->visit_if_namedtype(bt);
                add_decl(type_def_decl);
                cout << "visited: " << typedef_name.getString() << endl;
            }
        }
    } else if (SgClassDeclaration* class_decl = isSgClassDeclaration(n)) {
        visit_defining_decl(class_decl);
    } else if (SgInitializedName* in = isSgInitializedName(n)) {
        // std::cout << "initedname:" <<n->unparseToString() << std::endl;
        // std::cout << "typedecl type:" <<decl_type->unparseToString() << std::endl;
        this->visit_if_namedtype(in->get_type());
    } else if (SgEnumDeclaration* enum_decl = isSgEnumDeclaration(n)) {
        if (type_decl_visited.count(enum_decl) == 0) {
            mark_decl_visited(enum_decl);
            add_decl(enum_decl);
        }
    }
}

void TypeDeclTraversal::visit_if_namedtype(SgType * type) {
    // get rid of pointer decls
    while(true) {
        if (SgPointerType* ptr_type = isSgPointerType(type)) {
            type = ptr_type->get_base_type();
            continue;
        }
        if (SgArrayType* arr_type = isSgArrayType(type)) {
            type = arr_type->get_base_type();
            continue;
        }
        if (SgModifierType* mod_type = isSgModifierType(type)) {
            type = mod_type->get_base_type();
            continue;
        }
        break;  // done getting rid array and pointer types modifiers
    }

    if (SgNamedType* named_exp_type = isSgNamedType(type)) {
        SgDeclarationStatement* type_decl = named_exp_type->get_declaration();
        //this->visit_defining_decl(type_decl);
        this->visit(type_decl);
    } else if (SgFunctionType* fn_type = isSgFunctionType(type)) {
        for (SgType* arg_type : fn_type->get_arguments()) {
            visit_if_namedtype(arg_type);
        }
        visit_if_namedtype(fn_type->get_return_type());
    }
}

void TypeDeclTraversal::visit_defining_decl (SgDeclarationStatement* type_decl) {
    SgDeclarationStatement* def_type_decl = type_decl->get_definingDeclaration(); // ensure full decl
    if (def_type_decl == NULL && type_decl_visited.count(type_decl) == 0) {
        // no concrete type definition for this struct/class.  Cannot visit member decls.
        mark_decl_visited(type_decl);
        if (isSgGlobal(type_decl->get_parent())) {
            add_decl(type_decl);
        }
        return;
    }
    // fall through to do the case with concrete definition
    if (type_decl_visited.count(def_type_decl) == 0) {
        mark_decl_visited(def_type_decl);
        // be careful.  Need to create new traversal after inserting visited
        TypeDeclTraversal decl_traversal(*this);
        decl_traversal.traverse(def_type_decl, postorder);
        // copy out the list and set before end of search
        *this = decl_traversal;
        //type_decl_ios = decl_traversal.type_decl_ios;
        //type_decl_visited = decl_traversal.type_decl_visited;
        // after traversing all needed declaration, then record this decl
        if (isSgGlobal(def_type_decl->get_parent())) {
            SgClassDeclaration* cls_decl = isSgClassDeclaration(def_type_decl);
            add_decl_pending(def_type_decl);
        }
    }
}


void CallTraversal::sub_visit(SgNode * n) {
    CallTraversal call_traversal(*this); 
    call_traversal.traverse(n, postorder);
    *this = call_traversal;
}
void CallTraversal::visit(SgNode * n) {
    if (SgExpression* exp = isSgExpression(n)) {
        types.insert(exp->get_type());
        if (SgFunctionCallExp* fn_call = isSgFunctionCallExp(n)) {
            SgFunctionRefExp* fn_ref = isSgFunctionRefExp(fn_call->get_function());
            // cannot resolve function as a function reference (e.g. function pointer, etc)
            if (fn_ref == NULL)
                return;
            SgFunctionDeclaration* fn_decl = fn_ref->getAssociatedFunctionDeclaration();
            SgFunctionDeclaration* fn_decl_def = isSgFunctionDeclaration(fn_decl->get_definingDeclaration()); // ensure full decl
            fn_decl_s.insert(fn_decl);
            if (fn_decl_def != NULL && fn_defn_visited.count(fn_decl_def) == 0) {
                fn_defn_visited.insert(fn_decl_def); 
                SgBasicBlock* fn_body = fn_decl_def->get_definition()->get_body(); 
                sub_visit(fn_body);
                fn_defn_ios.insert(fn_decl_def);
            }
        } else if (SgVarRefExp* var = isSgVarRefExp(n)) {
            SgVariableSymbol* var_sym = var->get_symbol();
            SgVariableDeclaration *var_decl = isSgVariableDeclaration(var_sym->get_declaration()->get_declaration());
            if (!var_decl)
                return;  // this happens when variable is a parameter
            if (SgGlobal *gdb = isSgGlobal(var_decl->get_parent())) {
                cout << "global Var:" << var->unparseToString() << endl;
                globals.insert(var_decl);
                // for static global, also traverse initializer which may have other function call and also 
                // access other types, etc
                if (SageInterface::isStatic(var_decl)) {
                    for (SgInitializedName* in : var_decl->get_variables()) {
                        assert (in->get_name() == var_sym->get_name());
                        sub_visit(in->get_initializer());
                    }
                }
            }
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

void LoopInfo::printLoopReplay(string replay_file_name) {
    std::remove(replay_file_name.c_str());
    SgSourceFile* my_restore_src_file = isSgSourceFile(SageBuilder::buildFile(replay_file_name, replay_file_name));
    SgGlobal * glb_restore_src = my_restore_src_file->get_globalScope();
    extr->add_src_file_restore(my_restore_src_file);

    //for(type_decls_iter=type_decls_needed.begin(); type_decls_iter != type_decls_needed.end(); type_decls_iter++) {
    for(auto decl : type_decls_needed) {
        SgDeclarationStatement* type_decl = isSgDeclarationStatement(SageInterface::deepCopy(decl));
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
        ParamPassingStyle style = getPassingStyle(arg_type, extr->getSrcType());

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
/*
 * Take cares of print complete loop function and adding func calls
 * and extern loop func to the base file.
 * Manages SCoP pragmas.
 * Add OMP Timer around the loop. (Not sure)
 * Manages variables that are needed for extracting the loop.
 */
void LoopInfo::printLoopFunc(string outfile_name) {

    // /* Scope of loop body contains the variables needed for this loop to compile
    //  */
    // for (vector<SgForStatement *>::iterator iter =
    //          extr->consecutiveLoops.begin();
    //      iter != extr->consecutiveLoops.end(); iter++) {
    //     loop = *iter;
    //     loop_scope = (loop->get_loop_body())->get_scope();

	// /*
    //     if (hasFuncCallInScope()) {
    //         string externFuncStr;
    //         addScopeFuncAsExtern(externFuncStr);
    //     }
    // */

    //     // getParamatersInFunc - Dont need same analysis twice
    //     getVarsInScope();
    // }

    loop_scope = (loop->get_loop_body())->get_scope();
    getVarsInScope();



    //loop = *(extr->consecutiveLoops.begin());
    //loop_scope = (loop->get_loop_body())->get_scope();
    // Function definition


    files_to_compile.insert(outfile_name);
    const char* outfile = outfile_name.c_str();
    std::remove(outfile);
    SgProject* project = TransformationSupport::getProject(loop);
    SgSourceFile* src_file_loop = isSgSourceFile(SageBuilder::buildFile(outfile, outfile));
    extr->add_src_file_loop(src_file_loop);

    Sg_File_Info* file_info = src_file_loop->get_file_info();
    SgGlobal * glb_loop_src = src_file_loop->get_globalScope();
    TypeDeclTraversal decl_traversal(glb_loop_src);


    // Check whether calls are called
    CallTraversal call_traversal;
    call_traversal.traverse(loop, postorder);

    for (SgType* type : call_traversal.get_type_v()) {
        decl_traversal.visit_if_namedtype(type); 
    }

    /*
    Rose_STL_Container<SgNode *> expList = NodeQuery::querySubTree(loop, V_SgExpression);
    for (Rose_STL_Container<SgNode*>::iterator iter = expList.begin(); iter !=expList.end(); iter ++) {
        SgExpression* exp = isSgExpression(*iter);
        decl_traversal.visit_if_namedtype(exp->get_type()); 
    }
    /*/
    // also consider initializer in static global variables
    /*
    for (SgVariableDeclaration* var_decl : call_traversal.get_global_decl_v()) {
        if (!SageInterface::isStatic(var_decl))
            continue;  // skip if not static
        for (SgInitializedName* in : var_decl->get_variables()) {
            assert (in->get_name() == gvar->get_name());
            for (SgNode* n : NodeQuery::querySubTree(in->get_initializer(), V_SgExpression)) {
                decl_traversal.visit_if_namedtype(isSgExpression(n)->get_type()); 
            }
        }
    }
    */
    /*
    for (SgInitializedName* gvar : global_vars_initName_vec) {
        SgVariableDeclaration* var_decl = isSgVariableDeclaration(gvar->get_declaration());
        if (!SageInterface::isStatic(var_decl))
            continue;  // skip if not static
        for (SgInitializedName* in : var_decl->get_variables()) {
            assert (in->get_name() == gvar->get_name());
            for (SgNode* n : NodeQuery::querySubTree(in->get_initializer(), V_SgExpression)) {
                decl_traversal.visit_if_namedtype(isSgExpression(n)->get_type()); 
            }
        }
    }
    */
    
    //for(type_decls_iter=type_decls_v.begin(); type_decls_iter != type_decls_v.end(); type_decls_iter++) {
    type_decls_needed = decl_traversal.get_type_decl_v();

    vector<SgDeclarationStatement*>::iterator type_decls_iter;
    //for(type_decls_iter=type_decls_needed.begin(); type_decls_iter != type_decls_needed.end(); type_decls_iter++) {
    int ii=0;
    for(auto decl : type_decls_needed) {
        ii ++;
        /*
        if (ii < 88)
            continue;
        if (ii >= 90)
            break;
        */
        SgDeclarationStatement* type_decl = isSgDeclarationStatement(SageInterface::deepCopy(decl));

        // Don't want the extra #include from original file
        //cout << decl->unparseToString() << endl;
        type_decl->set_attachedPreprocessingInfoPtr(NULL);

        if(SgTypedefDeclaration* typedef_decl = isSgTypedefDeclaration(type_decl)) {
            cout << "ADD TYPE:" << typedef_decl->get_name().getString() << "("<< typedef_decl<<")" << endl;
            cout << "ADD TYPE0:" << isSgTypedefDeclaration(decl)->get_name().getString() << "("<< decl<<")" << endl;
        }
        for (SgNode* tn : NodeQuery::querySubTree(type_decl, V_SgClassDefinition)) {
            SgClassDefinition* class_defn = isSgClassDefinition(tn);
            cout << "FIXING: " << class_defn->get_mangled_name().getString() << "(" << class_defn<<")"<< endl;
            SgSymbolTable* the_symtable = class_defn->get_symbol_table();
            SgSymbolTable::BaseHashType* internalTable1 = the_symtable->get_table();
            SgSymbolTable::hash_iterator i1 = internalTable1->begin();
            vector<SgSymbol*> syms_to_remove;
            while (i1 != internalTable1->end()) {
                SgSymbol* symbol = isSgSymbol((*i1).second);
                if (symbol->get_name().getString().substr(0,14) == "__anonymous_0x") {
                    // fix the symbol tble as deepcopy somehow added extra anonymous class symbols
                    syms_to_remove.push_back(symbol);
                }
                i1++;
            }
            for (SgSymbol* rs : syms_to_remove) { 
                cout << "Removing ANONYMOUS SYM:" << rs->get_name().getString() << endl;
                the_symtable->remove(rs);
                delete rs;
            }

        }
        std::map<SgName,int> name_to_gnu_attribute_alignment;
        for (SgNode* decl_node : NodeQuery::querySubTree(decl, V_SgDeclarationStatement)) {
            SgDeclarationStatement* decl_stmt = isSgDeclarationStatement(decl_node);
            assert(name_to_gnu_attribute_alignment.find(decl_stmt->get_mangled_name()) == name_to_gnu_attribute_alignment.end());
            name_to_gnu_attribute_alignment[decl_stmt->get_mangled_name()] = 
                decl_stmt->get_declarationModifier().get_typeModifier().get_gnu_attribute_alignment();
        }
        for (SgNode* decl_node : NodeQuery::querySubTree(type_decl, V_SgDeclarationStatement)) {
            SgDeclarationStatement* decl_stmt = isSgDeclarationStatement(decl_node);
            SgName name = decl_stmt->get_mangled_name();
            int alignment = name_to_gnu_attribute_alignment[name];
            if (alignment> -1) 
                decl_stmt->get_declarationModifier().get_typeModifier().set_gnu_attribute_alignment(alignment);
        }


	#if 0
        if(SgTypedefDeclaration* typedef_decl = isSgTypedefDeclaration(type_decl)) {
          //if (typedef_decl->get_name().getString()== "x264_param_t") {
          if (true) {
            //SgDeclarationStatement* debug_type_decl = isSgDeclarationStatement(SageInterface::deepCopy(decl));
            SgTypedefDeclaration *td = isSgTypedefDeclaration(decl);
            SgTypedefDeclaration *ctd = isSgTypedefDeclaration(type_decl);
            if (SgClassDeclaration* bclass_decl = isSgClassDeclaration(td->get_baseTypeDefiningDeclaration())) {
                SgSymbolTable::BaseHashType* internalTable = bclass_decl->get_definition()->get_symbol_table()->get_table();
                SgSymbolTable::hash_iterator i = internalTable->begin();
                while (i != internalTable->end()) {
                    SgSymbol* symbol = isSgSymbol((*i).second);
                    cout << "SYM:" << symbol->get_name().getString() << endl;
                    i++;
                }

                for (SgDeclarationStatement* mdecl : bclass_decl->get_definition()->get_members()) {
                    if (SgVariableDeclaration* vdecl = isSgVariableDeclaration(mdecl)) {
                        for (SgInitializedName* in : vdecl->get_variables()) {
                            if (SgNamedType* nt = isSgNamedType(in->get_type())) {
                                if (SgClassDeclaration* ctd = isSgClassDeclaration(nt->get_declaration())) {
                                    in->unparseToString();
                                }
                            }
                        }

                    }

                }

                SgClassDeclaration* bclass_decl1 = isSgClassDeclaration(ctd->get_baseTypeDefiningDeclaration());


                SgSymbolTable* the_symtable = bclass_decl1->get_definition()->get_symbol_table();
                SgSymbolTable::BaseHashType* internalTable1 = the_symtable->get_table();
                SgSymbolTable::hash_iterator i1 = internalTable1->begin();
                vector<SgSymbol*> syms_to_remove;
                while (i1 != internalTable1->end()) {
                    SgSymbol* symbol = isSgSymbol((*i1).second);
                    if (symbol->get_name().getString().substr(0,14) == "__anonymous_0x") {
                        // fix the symbol tble as deepcopy somehow added extra anonymous class symbols
                        syms_to_remove.push_back(symbol);
                    }
                    i1++;
                }
                for (SgSymbol* rs : syms_to_remove) { 
                    cout << "Removing ANONYMOUS SYM:" << rs->get_name().getString() << endl;
                    the_symtable->remove(rs);
                    delete rs;
                }

                for (SgDeclarationStatement* mdecl : bclass_decl1->get_definition()->get_members()) {
                    if (SgVariableDeclaration* vdecl = isSgVariableDeclaration(mdecl)) {
                        for (SgInitializedName* in : vdecl->get_variables()) {
                            if (SgNamedType* nt = isSgNamedType(in->get_type())) {
                                if (SgClassDeclaration* ctd = isSgClassDeclaration(nt->get_declaration())) {
                                    in->unparseToString();
                                }
                            }
                        }

                    }
                }
            }
          }
          //if (typedef_decl->get_name().getString()== "x264_weight_t") {
            SgTypedefDeclaration *td = isSgTypedefDeclaration(decl);
            if (SgClassDeclaration* bclass_decl = isSgClassDeclaration(td->get_baseTypeDefiningDeclaration())) {
                std::map<SgName,int> name_to_gnu_attribute_alignment;

                for (SgDeclarationStatement* mdecl : bclass_decl->get_definition()->get_members()) {
                    name_to_gnu_attribute_alignment[mdecl->get_mangled_name()] = 
                        mdecl->get_declarationModifier().get_typeModifier().get_gnu_attribute_alignment();
                }

                SgTypedefDeclaration *ctd = isSgTypedefDeclaration(type_decl);
                SgClassDeclaration* bclass_decl1 = isSgClassDeclaration(ctd->get_baseTypeDefiningDeclaration());
                for (SgDeclarationStatement* mdecl : bclass_decl1->get_definition()->get_members()) {
                    SgName name = mdecl->get_mangled_name();
                    int alignment = name_to_gnu_attribute_alignment[name];
                    if (alignment> -1) {
                        mdecl->get_declarationModifier().get_typeModifier().set_gnu_attribute_alignment(alignment);
                    }
                }
                type_decl->get_declarationModifier().get_typeModifier().set_gnu_attribute_alignment
                    (decl->get_declarationModifier().get_typeModifier().get_gnu_attribute_alignment());


                SgClassType* bt = isSgClassType(typedef_decl->get_base_type());
                cout << "BT: " << bt->unparseToString() << endl;
                cout << "TBT: " << typedef_decl->unparseToString() << endl;
            }
          //}
        }
    #endif

        SgSymbol* type_decl_sym = type_decl->get_symbol_from_symbol_table();
        if (type_decl_sym == NULL) {
            SgSymbol* decl_sym = decl->get_symbol_from_symbol_table();
            SgSymbol* type_decl_sym1 = type_decl->get_symbol_from_symbol_table();
            if (type_decl->get_scope() != glb_loop_src) {
                type_decl->set_scope(glb_loop_src);
                if (SgTypedefDeclaration* typedef_decl = isSgTypedefDeclaration(type_decl)) {
                    glb_loop_src->insert_symbol(typedef_decl->get_name(), new SgTypedefSymbol(typedef_decl));
                } else if (SgClassDeclaration* class_decl = isSgClassDeclaration(type_decl)) {
                    SgClassDeclaration* nondefdecl = isSgClassDeclaration(class_decl->get_firstNondefiningDeclaration());
                    nondefdecl->set_scope(glb_loop_src);
                    glb_loop_src->insert_symbol(class_decl->get_name(), new SgClassSymbol(nondefdecl));
                } else if (SgEnumDeclaration* enum_decl = isSgEnumDeclaration(type_decl)) {
                    glb_loop_src->insert_symbol(enum_decl->get_name(), new SgEnumSymbol(enum_decl));
                } else {
                    assert(false);  // unexpected case
                }
            }
        }
        SageInterface::appendStatement(type_decl, glb_loop_src);
    }
    //this->addGlobalVarDecls(glb_loop_src, true);
    for (SgVariableDeclaration* var_decl : call_traversal.get_global_decl_v()) {
        addGlobalVarDecl(glb_loop_src, true, var_decl);
    }

    for (auto const& fn_decl : call_traversal.get_fn_decl_s()) {
        auto fn_decl_copy = SageInterface::deepCopy(fn_decl);
        SageInterface::appendStatement(fn_decl_copy, glb_loop_src);
    }
    for (auto const& fn_defn : call_traversal.get_fn_defn_v()) {
        // std::cout << fn_defn->unparseToString() << std::endl;
        auto fn_defn_copy = SageInterface::deepCopy(fn_defn);
        // only guard for those non-static function (where they are imported from outside)
        if (!SageInterface::isStatic(fn_defn_copy)) {
            SageInterface::guardNode(fn_defn_copy, RESTORE_GUARD_NAME);
        }
        fn_defn_copy->set_attachedPreprocessingInfoPtr(NULL);
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
        ParamPassingStyle style = getPassingStyle(arg_type, extr->getSrcType());
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

void Extractor::addExternDefs(SgFunctionDeclaration *func, SgFunctionDefinition* encl_fn) {
    externFuncDef.insert(pair<SgStatement *, SgScopeStatement *>(
        dynamic_cast<SgStatement *>(func), encl_fn));
    // externFuncDef.insert(pair<SgStatement*,SgStatement*>(
    // dynamic_cast<SgStatement *>(func),
    // SageInterface::getFirstStatement(loopParentFuncScope) ));
}

void LoopInfo::dumpGlobalVarNames(const string& data_folder, const string& loop_file_name) {
    string report_file = data_folder + "globalVarNames_"+loop_file_name+".txt";
    ofstream info_file(report_file);
    for (auto var : global_vars_initName_vec) {
        SgName name = var->get_name();
        info_file << name << endl;
    }
    info_file.close();
}
/* Add loop function call as extern in the base source file */
void LoopInfo::addGlobalVarDecls(SgGlobal* glb, bool as_extern) {
    vector<SgInitializedName *>::iterator iter;
    for (SgInitializedName* var : global_vars_initName_vec) {
    //for (iter = global_vars_initName_vec.begin();
    //        iter != global_vars_initName_vec.end(); iter++) {
        // Create parameter list
        SgDeclarationStatement* cur_var_decl = var->get_declaration();
        addGlobalVarDecl(glb, as_extern, cur_var_decl);
    }
}
void LoopInfo::addGlobalVarDecl(SgGlobal* glb, bool as_extern, SgDeclarationStatement* cur_var_decl) {
    SgVariableDeclaration *var_decl = isSgVariableDeclaration(cur_var_decl);
    SgInitializedName* var = NULL;
    for (SgInitializedName* cv : var_decl->get_variables()) {
        assert (var == NULL);
        var = cv;
        // expect no next iteration, otherwise var != NULL and will abort.
    }

    if (SageInterface::isStatic(var_decl)) {
        // for static variables, add them as is
        var_decl = isSgVariableDeclaration(SageInterface::deepCopy(var_decl));
        for (SgInitializedName* in : var_decl->get_variables()) {
            // make sure only one this variable shows up in the declaration
            assert (in->get_name() == var->get_name());
        }
    } else {
        SgName arg_name = var->get_name();
        //SgInitializedName *arg_init_name;
        var_decl = SageBuilder::buildVariableDeclaration( arg_name, var->get_type());
        //SageInterface::appendArg(paramList, arg_init_name);
        if (as_extern)
            SageInterface::setExtern(var_decl);
        //std::cout << "David deArg type unparse 2:" << paramList->unparseToString() << std::endl;
    }
    SageInterface::appendStatement(var_decl , glb);
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

        ParamPassingStyle style = getPassingStyle(arg_type, extr->getSrcType());

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
    if (extr->getGlobalNode() != NULL) {
        SgFunctionDeclaration* func = this->makeLoopFunc(false, extr->getGlobalNode());
        SageInterface::setExtern(func);
        // Insert Function into Global scope
        // SageInterface::prependStatement( func, extr->getGlobalNode() );

        SgFunctionDefinition* encl_fn = SageInterface::getEnclosingFunctionDefinition(loop);
        extr->addExternDefs(func, encl_fn);

    } else {
        ROSE_ASSERT(extr->getGlobalNode() != NULL);
    }
}

void InvitroExtractor::generateBaseHeaders(SgGlobal* glb_scope) {
    SageInterface::insertHeader("tracee.h", PreprocessingInfo::before, false, glb_scope);
}

void InvitroExtractor::generateBasePreLoop(SgScopeStatement* loop_scope, 
    SgExprStatement * call_expr_stmt, LoopInfo* loop_info, vector<SgInitializedName *> scope_vars_initName_vec) {
    int instance_num = 1;

    SgFunctionCallExp* call_expr = isSgFunctionCallExp(call_expr_stmt->get_expression());
    assert(call_expr != NULL);
    auto funcArgs = call_expr->get_args()->get_expressions();
    SgName func_name = call_expr->getAssociatedFunctionSymbol()->get_name();

    int numOfArgs = funcArgs.size();
    SgExprListExp* dump_args = SageBuilder::buildExprListExp(
        SageBuilder::buildStringVal(func_name.str()), SageBuilder::buildIntVal(instance_num),
        SageBuilder::buildIntVal(numOfArgs));

    for (int i = 0; i < numOfArgs; i++) {
        SgExpression* funcArgument = funcArgs[i]; 
        SgInitializedName * func_arg_decl = scope_vars_initName_vec[i];
        SgExpression* dump_arg = loop_info->getFuncParamAddr(func_arg_decl, funcArgument);
        dump_args->append_expression(dump_arg);
    }
    SgExprStatement *dump_call = SageBuilder::buildExprStatement(SageBuilder::buildFunctionCallExp(
        "dump", SageBuilder::buildVoidType(), dump_args, loop_scope));
    SageInterface::insertStatementBefore(call_expr_stmt, dump_call);
}

void InvitroExtractor::generateBasePostLoop(SgScopeStatement* loop_scope, SgExprStatement * call_expr_stmt) {
    SgExprStatement *after_dump_call = SageBuilder::buildExprStatement(SageBuilder::buildFunctionCallExp(
        "after_dump", SageBuilder::buildVoidType(), SageBuilder::buildExprListExp(), loop_scope));
    SageInterface::insertStatementAfter(call_expr_stmt, after_dump_call);
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

        ParamPassingStyle style = getPassingStyle(arg_type, extr->getSrcType());

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

    extr->generateBaseHeaders(glb_scope);

    // END Add save stuff here
    SageInterface::replaceStatement(loop, call_expr_stmt, true);


    extr->generateBasePreLoop(loop_scope, call_expr_stmt, this, scope_vars_initName_vec);
    extr->generateBasePostLoop(loop_scope, call_expr_stmt);
    #endif

    //loop_func_call = call_expr_stmt;
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

bool Extractor::skipLoop(SgForStatement *astNode) {
    return !collected_loops.matches(astNode);
}

#if 0
// Lots of logic that may be put in the collection phases if needed
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
#endif

//void Extractor::reportOutputFiles(const vector<SgSourceFile*> files) {
void Extractor::reportOutputFile(ofstream& info_file, const string& loop_file_name, const string& type) {
    cout << type << "_FILE_NAME: " << loop_file_name << endl;
    string parsed_loop_file_name = parseFileName(&loop_file_name);
    cout << "PARSED "<< type <<"_file_name: " << parsed_loop_file_name << endl;
    info_file << type << "," << parsed_loop_file_name << endl;
}
void Extractor::reportOutputFiles(ofstream& info_file, SgSourceFile* src_file_loop, const string& type) {
    string loop_file_name;
    if (src_file_loop) {
        loop_file_name = src_file_loop->get_file_info()->get_filenameString();
        reportOutputFile(info_file, loop_file_name, type);
    }
}

void Extractor::reportOutputFiles(ofstream& info_file, const vector<SgSourceFile*>& src_file_loops, const string& type) {
    for (SgSourceFile* src_file_loop : src_file_loops) {
        reportOutputFiles(info_file, src_file_loop, type);
    }
}

void Extractor::reportOutputFiles() {
    string report_file = getDataFolderPath() + "loopFileNames.txt";
    ofstream info_file(report_file);
    // parse loop_file_name and do fprintf to tmp/loopFileNames.txt
    string loop_file_name, base_file_name, restore_file_name;
    base_file_name = getDataFolderPath() + getBaseFileName();
    reportOutputFile(info_file, base_file_name, "BASE");
    reportOutputFiles(info_file, src_file_loops, "LOOP");
    reportOutputFiles(info_file, src_file_restores, "RESTORE");

    info_file.close();
    cout << "Output file info: " << report_file << endl;
}

void OutliningExtractor::extractLoop(SgForStatement* loop) {
    LoopInfo curr_loop(loop, getLoopName(loop), this);
    extractLoop(loop, curr_loop);
}

void OutliningExtractor::extractLoop(SgForStatement* loop, LoopInfo& curr_loop) {
    /*
        * Take cares of print complete loop function and adding func calls
        * and extern loop func to the base file.
        */

    string output_path = getDataFolderPath();
    string loop_file_name = getExtractionFileName(loop);
    string full_loop_file_name = output_path + loop_file_name;

    curr_loop.printLoopFunc(full_loop_file_name);
    curr_loop.addLoopFuncCall();
    curr_loop.addLoopFuncAsExtern();
    curr_loop.dumpGlobalVarNames(output_path, loop_file_name);
}

void InvitroExtractor::extractLoop(SgForStatement* loop, LoopInfo& curr_loop) {
    string output_path = getDataFolderPath();
    OutliningExtractor::extractLoop(loop, curr_loop);
    string replay_loop_file_name = output_path + getReplayFileName(loop);
    curr_loop.printLoopReplay(replay_loop_file_name);
}

void InvivoExtractor::extractLoop(SgForStatement* loop) {
    // Invivo extraction means inserting Locus pragma at loop head
    SgScopeStatement* loop_scope = (loop->get_loop_body())->get_scope();
    SgPragmaDeclaration* locus_pragma = SageBuilder::buildPragmaDeclaration("@ICE loop=scop", loop_scope);
    SageInterface::insertStatementBefore(loop, locus_pragma);
}

/**
 * @brief Most important function in the extractor, it will extract the loop
 *        body and create a new function
 * @param astNode The loop to be extracted
 */
void Extractor::extractLoops(SgForStatement *astNode) {
    Sg_File_Info* file_info = astNode->get_file_info();
    string file_name = file_info->get_filenameString();
    int lineNum = file_info->get_line();
    /*
    cout << "line number of ast node: " << astNode->unparseToString() << endl;
    cout << "is " << lineNum << endl;
    */

    /* Here we check if loop file number is the one we need */
    //if (file_name == targetfilename && lineNum >= lineNumbers.first && lineNum <= lineNumbers.second) {
    if (collected_loops.matches(astNode)) {
        // cout << "PASSED the lineNum check" << endl;
        //SgForStatement *loop = dynamic_cast<SgForStatement *>(astNode);
        SgForStatement *loop = isSgForStatement(astNode);
        updateUniqueCounter(loop);

        //ofstream loop_file_buf;
        //loop_file_buf.open(loop_file_name.c_str(), ofstream::out);



        // Create loop object
        extractLoop(loop);


        // to replace remaining consecutive loops with null statements */
        // if (consecutiveLoops.size() > 1) {
        //     vector<SgForStatement *>::iterator iter = consecutiveLoops.begin();
        //     iter++; // First loop is already removed by addLoopFuncCall()
        //     for (; iter != consecutiveLoops.end(); iter++) {
        //         SageInterface::replaceStatement(
        //             (*iter), SageBuilder::buildNullStatement(), false);
        //     }
        // }
        // set it done after extraction
        // extracted.insert(lineNumbers);
    }

}

// void Extractor::collectAdjoiningLoops(SgStatement *loop) {
//     if (loop == NULL)
//         return;
//     // cout << "Loop: " << loop->class_name() << endl <<
//     // loop->unparseToCompleteString() << endl;
//     consecutiveLoops.push_back(dynamic_cast<SgForStatement *>(loop));
//     SgStatement *nextStmt = SageInterface::getNextStatement(loop);
//     if (nextStmt && nextStmt->variantT() &&
//         nextStmt->variantT() == V_SgForStatement) {
//         collectAdjoiningLoops(nextStmt);
//     } else {
//         return;
//     }
//     return;
// }

void Extractor::extractFunctions(SgNode *astNode) {}

bool LoopLocations::matches(SgNode* astNode) {
    Sg_File_Info* file_info = astNode->get_file_info();
    string file_name = file_info->get_filenameString();
    int lineNum = file_info->get_line();
    for(auto matching : locs) {
        // matching is <filename, lineno>
        if (matching.first == file_name && matching.second == lineNum) {
            return true;
        }
    }
    return false;
}

LoopLocations
LoopCollector::evaluateInheritedAttribute(SgNode *astNode, LoopLocations locs) { 
    //LoopLocations ret;
    //cout << "INH:" << astNode->unparseToString() << endl;
    // just pass it on
    if (isSgForStatement(astNode)) { 
        locs.incLevel();
    }
    return locs;
}

void CollectedLoops::addAll(const CollectedLoops& loops) { 
    collected.insert(loops.collected.begin(), loops.collected.end()); 
    deepest_nest = max(deepest_nest, loops.deepest_nest);
}

void CollectedLoops::set(SgForStatement* loop, int nest_level) { 
    assert(collected.size() == 0);
    collected.insert(loop); 
    deepest_nest = nest_level;
}

/* Required for Bottom Up parsing virtual function - Will not be used */
CollectedLoops LoopCollector::evaluateSynthesizedAttribute(SgNode *astNode, LoopLocations locs,
 SubTreeSynthesizedAttributes syn_attr_list) {
    CollectedLoops children_loops;
    for (auto const &child_loops : syn_attr_list) { 
        children_loops.addAll(child_loops);
    }
    if (SgForStatement *for_loop = isSgForStatement(astNode)) { 
        int children_depth = children_loops.getLoopDepth();
        bool check_depth = false;
        bool depth_test = check_depth ? (children_depth <=2) : true;

        if (locs.matches(for_loop) || (!children_loops.isEmpty() && depth_test)) {
        //if (locs.matches(for_loop) || (!children_loops.isEmpty() && children_depth <= 3)) {
            CollectedLoops loops;
            cout << "matched or children matched:" << endl;
            loops.set(for_loop, children_depth + 1);
            return loops;
        } 
        // fall through to use children nests, this is for loop so increase one level
        children_loops.incLoopDepth();
    } 
    return children_loops;
}

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
            //SgForStatement *loop = dynamic_cast<SgForStatement *>(astNode);
            SgForStatement *loop = isSgForStatement(astNode);
            if (collected_loops.matches(loop)) {
                Sg_File_Info* file_info = loop->get_file_info();
                cout << "MATCHED:" << file_info->get_filenameString() << ":"
                     << file_info->get_line() << endl;
            }
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
                if (!skipLoop(loop)) {
                    /*
                    if (LoopExtractor_enabled_options[EXTRACTKERNEL])
                        collectAdjoiningLoops(loop);
                    else
                        consecutiveLoops.push_back(loop);
                    */
                    extractLoops(loop);
                }
                // consecutiveLoops.clear(); // Clear vector for next kernel
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
            // loopParentFuncScope = dynamic_cast<SgScopeStatement *>(astNode);
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

void InvitroExtractor::instrumentMain() {
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
Extractor* Extractor::createExtractor(LoopExtractorMode mode, const vector<string>& argv) {
    switch(mode) {
        case INSITU: 
            return new InsituExtractor(argv);
        case INVIVO: 
            return new InvivoExtractor(argv);
        default: 
            break;
    }
    return new InvitroExtractor(argv);
}
void Extractor::final_pushback_fileList(SgProject* ast) {
    for (SgSourceFile* src_file_loop : src_file_loops) {
        ast->get_fileList().push_back(src_file_loop);
    }
    for (SgSourceFile* src_file_restore : src_file_restores) {
        ast->get_fileList().push_back(src_file_restore);
    }
    //if (src_file_restore)
    //    ast->get_fileList().push_back(src_file_restore);
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

    LoopCollector loop_collect;
    //LoopLocations loop_locs;
    //loop_locs.addLoc(targetfilename, lineNumbers.first);
    collected_loops = loop_collect.traverse(ast, loop_locs);
    //cout << "Result:" << result << endl;


    // should do a traverse first to collect all loops before doing transformation
    // so the input line numbers will be correct
    this->traverseInputFiles(ast, inhr_attr);
    // after traversing, main scope will be found
    this->instrumentMain();
    // this->generateHeaderFile();
    this->addPostTraversalDefs();
    //SgFile* my_file = SageBuilder::buildFile("/tmp/foo12.cc", "/tmp/foo12.cc");
    final_pushback_fileList(ast);

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
