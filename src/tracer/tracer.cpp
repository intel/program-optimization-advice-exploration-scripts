#include "tracer.h"

/**
 * @brief visit function is used to traverse the AST
 *        and find the insertBefore insertion point
 *        Being called inside of traverseInputFiles function
 * @param node is the current node of the AST
 */
void Tracer::visit(SgNode *n) {

    if (isSgExprStatement(n)) {
        SgExprStatement *func_stmt = isSgExprStatement(n);
        SgFunctionCallExp *func_call =
            isSgFunctionCallExp(func_stmt->get_expression());
        if (func_call) {
            string func_name =
                func_call->getAssociatedFunctionDeclaration()->get_name();
            if (func_name == current_lfi->getFuncName()) {
                loopFuncScope = SageInterface::getScope(func_stmt);
                insertBefore = func_stmt;
                loopFuncNode = func_stmt;
            }
        }
    }
}

/**
 * @brief visit function is used to traverse the AST
 *        and find the headers only from the loop file
 *        Being called inside of traverseInputFiles function
 * @param node is the current node of the AST
 */
void ParseLoopFiles::visit(SgNode *node) {
    SgLocatedNode *locatedNode = isSgLocatedNode(node);
    if (locatedNode) {
        AttachedPreprocessingInfoType *directives =
            locatedNode->getAttachedPreprocessingInfo();
        if (directives != NULL) {
            AttachedPreprocessingInfoType::iterator i;
            for (i = directives->begin(); i != directives->end(); i++) {
                std::string directiveTypeName =
                    PreprocessingInfo::directiveTypeName(
                        (*i)->getTypeOfDirective())
                        .c_str();
                if (directiveTypeName == "CpreprocessorIncludeDeclaration") {
                    std::string incFileName = ((*i)->getFilename());
                    string loopFileName = tr->getCurrentLoopFileName();
                    if (parseFileName(&incFileName) ==
                        parseFileName(&loopFileName)) {
                        std::string headerLine = (*i)->getString().c_str();
                        tr->addHeaderLine(headerLine);
                    }
                }
            }
        }
    }
}

/**
 * @brief Function that starts the generation of codelet sourcefiles
 */
void Tracer::initTracing() {
    std::vector<std::string> argv = filenameVec;
    argv.pop_back();
    argv.push_back(loopExtrIncludeFlag);
    argv.push_back(baseFileName);
    vector<string> argv_copy(argv);
    for (int i = 0; i < loopFileNames.size(); i++) {
        argv_copy.push_back(loopFileNames[i]);
    }
    size_t found = baseFileName.find_last_of("/");
    string source_file_name = baseFileName.substr(found + 1);

    ParseLoopFiles *PLF = new ParseLoopFiles(&loopFileNames);
    PLF->tr = this;
    SgProject *parseLoopFilesProject = frontend(argv_copy);

    /* Iterate over LFI and generate all necessary info */
    for (int i = 0; i < LFI.size(); i++) {
        headerLines.clear();
        current_lfi = LFI[i];

        currentLoopFileName = loopFileNames[i];
        size_t found = currentLoopFileName.find_last_of("/");
        string currentShortLoopFileName = currentLoopFileName.substr(found + 1);
        PLF->traverseInputFiles(parseLoopFilesProject, preorder);

        /* Separate project for TRACE source file generation */
        SgProject *tracePrj = frontend(argv);
        project = tracePrj;
        if (project == NULL)
            cout << "TRACE project is NULL" << endl;
        ROSE_ASSERT(project != NULL);
        globalscope = SageInterface::getFirstGlobalScope(project);
        this->buildHeaders();
        this->traverseInputFiles(project, preorder);
        /* The most important function that inserts memory tracing lines of code
         */
        this->insertTraceInfo();
        project->unparse();
        string tracePrefixStr = "trace";
        moveCodeletSourcefile(tracePrefixStr, current_lfi->getFuncName(),
                              source_file_name, false);
        delete (tracePrj);

        /* Separate project for SAVE header file generation */
        SgProject *savePrj = frontend(argv);
        project = savePrj;
        if (project == NULL)
            cout << "SAVE project is NULL" << endl;
        ROSE_ASSERT(project != NULL);
        globalscope = SageInterface::getFirstGlobalScope(project);
        this->buildHeaders();
        this->traverseInputFiles(project, preorder);
        /* The most important function that inserts data saving lines of code */
        this->insertSaveInfo();
        string savePrefixStr = "save";

        /* Generation of RESTORE driver file */
        string driverFileName = "restore_" + source_file_name;
        restoreOutfile.open(driverFileName, ofstream::out);
        globalNames = current_lfi->getGlobalVars();
        insertRestoreHeaders();
        // TODO: here should go the rest of preprocessing info
        insertLoopFuncDecl();
        insertClassDeclarations();
        insertGlobalVarDeclarations();
        insertMainFunction();
        restoreOutfile.close();
        moveCodeletSourcefile("restore", current_lfi->getFuncName(),
                              source_file_name, true);
        moveDriverFile("restore", current_lfi->getFuncName(), source_file_name);

        /* We unparse ast for SAVE source file after finishing the generation of
         *  a RESTORE source file, because we need some data (globalscope,
         *  loopFuncNode, classes, etc) from SAVE ast to generate the RESTORE
         *  source file.
         */
        project->unparse();
        moveCodeletSourcefile(savePrefixStr, current_lfi->getFuncName(),
                              source_file_name, false);
        delete (savePrj);

        /* Callgraph generation is necessary for new memory tracing pintool
         *  which traces memory accesses from all functions that were called
         *  from the loop function.
         */
        CallGraphBuilder CGBuilder(parseLoopFilesProject);
        CGBuilder.buildCallGraph(builtinFilter());
        auto CG = CGBuilder.getGraph();
        auto mapCG = CGBuilder.getGraphNodesMapping();
        auto loopFuncDecl = current_lfi->getFuncDecl();
        SgName loopFuncName = loopFuncDecl->get_qualified_name();
        for (auto it = mapCG.begin(); it != mapCG.end(); ++it) {
            if (it->second->get_name() == loopFuncName.getString()) {
                traverseCG(it->second, CG, mapCG);
            }
        }
    }
    /* Exporting visited function calls that were collected during CallGraph
     *  traversal to a file for later use in memory tracing pintool
     */
    exportFuncCalls();
}

/**
 * @brief Recursive function that traverses the CallGraph and collects all
 *        function calls that were made from the loop function
 */
void Tracer::traverseCG(
    SgGraphNode *CGNode, SgIncidenceDirectedGraph *CG,
    boost::unordered_map<SgFunctionDeclaration *, SgGraphNode *> &mapCG) {
    cout << "TRAVERSE CG" << endl;
    cout << "CGNode: " << CGNode->get_name() << endl;
    auto edge = CG->getEdge(CGNode);
    if (edge.size() > 0) {
        for (auto it2 = edge.begin(); it2 != edge.end(); ++it2) {
            cout << "EDGE: \nNode A: " << (*it2)->get_node_A()->get_name()
                 << "; Node B: " << (*it2)->get_node_B()->get_name() << endl;
            auto funcName = (*it2)->get_node_B()->get_name();
            auto isVisited = visitedFuncCalls.insert(funcName);
            if (isVisited.second == false) {
                cout << "Function " << funcName << " already visited" << endl;
                return;
            }
            traverseCG((*it2)->get_node_B(), CG, mapCG);
        }
    }
    cout << "Exited from traversal func" << endl;
}

/**
 * @brief Function that exports all visited function calls to a file
 */
void Tracer::exportFuncCalls() {
    cout << "EXPORTING FUNC CALLS" << endl;
    ofstream funcCallsOutfile;
    string funcCallsFileName = "callgraphResult.extr";
    funcCallsOutfile.open(funcCallsFileName, ofstream::out);
    for (auto it = visitedFuncCalls.begin(); it != visitedFuncCalls.end();
         ++it) {
        string funcName = (*it).getString();
        std::string::size_type prev_pos = 0, pos = 0;
        std::string separator = ":";
        while ((pos = (funcName).find(separator, pos)) != std::string::npos) {
            std::string substring((funcName).substr(prev_pos, pos - prev_pos));
            prev_pos = ++pos;
        }
        std::string substring((funcName).substr(prev_pos, pos - prev_pos));
        cout << "Exporting function name: " << substring << endl;
        funcCallsOutfile << substring << endl;
    }
    funcCallsOutfile.close();
    moveFile(funcCallsFileName, "./LoopExtractor_data");
}

/**
 * @brief Function that moves a file to a specified directory
 */
void Tracer::moveFile(string fileName, string dirName) {
    cout << "Moving file " << fileName << " to " << dirName << endl;
    string command = "mv " + fileName + " " + dirName;
    string result = executeCommand(command);
    if (result.find("failed") != string::npos) {
        cout << "mv FAILED!!!!" << endl;
    }
}

/**
 * @brief Function that inserts headers for RESTORE driver file
 */
void Tracer::insertRestoreHeaders() {
    restoreOutfile << "#include \"util.h\" \n#include \"addresses.h\" "
                      "\n#include \"saved_pointers.h\" \n#include \"unistd.h\" "
                      "\n#include <alloca.h> \n";
    for (int i = 0; i < headerLines.size(); i++) {
        restoreOutfile << headerLines[i];
    }
}

/**
 * @brief Function that inserts declaration of the loop function in RESTORE
 *        driver file
 */
void Tracer::insertLoopFuncDecl() {
    SgExprStatement *exprStmt = isSgExprStatement(loopFuncNode);
    if (exprStmt) {
        SgExpression *expr = exprStmt->get_expression();
        SgFunctionCallExp *funcExpr = isSgFunctionCallExp(expr);
        if (funcExpr) {
            SgFunctionDeclaration *funcDecl =
                funcExpr->getAssociatedFunctionDeclaration();
            if (funcDecl) {
                restoreOutfile << funcDecl->unparseToString() << endl;
            } else {
                cout << "Function Declaration can't be resolved statically!!! "
                     << endl;
            }
        } else {
            cout << "Something went wrong with funcExpr " << endl;
        }
    } else {
        cout << "SOMETHING WENT WRONG with exprStmt!" << endl;
    }
}

/**
 * @brief Function that inserts class declarations in RESTORE driver file
 */
void Tracer::insertClassDeclarations() {
    for (int i = 0; i < globalNames.size(); i++) {
        SgName name(globalNames[i]);
        SgVariableSymbol *smbl = globalscope->lookup_variable_symbol(name);

        if (smbl) {
            string varName = smbl->get_name();
            SgType *varType = smbl->get_type();

            typeDeclaration(varType);

        } else {
            cout << "NOT found variable with name " << globalNames[i] << endl;
        }
    }

    restoreOutfile << classDeclarations.str();
}

/**
 * @brief Function that inserts custom type declarations in RESTORE driver file
 */
void Tracer::typeDeclaration(SgType *tp) {
    std::string typeClass = tp->class_name();
    if (SgModifierType *modTp = isSgModifierType(tp)) {
        auto inserted = declaredTypes.insert(tp);
        if (inserted.second == false) {
            std::cout << "THIS TYPE WAS ALREADY DECLARED!" << std::endl;
        } else {
            if (SgType *modBaseType = modTp->get_base_type()) {
                typeDeclaration(modBaseType);
            }
        }
    } else if (SgClassType *classType = isSgClassType(tp)) {
        auto inserted = declaredTypes.insert(tp);
        if (inserted.second == false) {
            std::cout << "THIS TYPE WAS ALREADY DECLARED!" << std::endl;
        } else {
            SgDeclarationStatement *typeDecl =
                classType->getAssociatedDeclaration();
            if (SgClassDeclaration *classDecl =
                    isSgClassDeclaration(typeDecl)) {
                SgClassDeclaration *declStatOfClassDecl =
                    isSgClassDeclaration(classDecl->get_definingDeclaration());
                SgClassDefinition *classDef =
                    declStatOfClassDecl->get_definition();

                SgDeclarationStatementPtrList declStmtList =
                    classDef->get_members();
                SgDeclarationStatementPtrList::iterator declIt =
                    declStmtList.begin();
                SgDeclarationStatementPtrList::iterator declEnd =
                    declStmtList.end();
                for (; declIt != declEnd; ++declIt) {
                    SgDeclarationStatement *declStmt =
                        isSgDeclarationStatement(*declIt);
                    SgVariableDeclaration *varDecl =
                        isSgVariableDeclaration(declStmt);
                    SgInitializedNamePtrList memVariables =
                        varDecl->get_variables();
                    for (int i = 0; i < memVariables.size(); i++) {
                        SgInitializedName *memPtr =
                            isSgInitializedName(memVariables[i]);
                        SgType *memType = memPtr->get_type();
                        typeDeclaration(memType);
                    }
                }
            }
        }
    } else if (SgTypedefType *typedefType = isSgTypedefType(tp)) {
        auto inserted = declaredTypes.insert(tp);
        if (inserted.second == false) {
            std::cout << "THIS TYPE WAS ALREADY DECLARED!" << std::endl;
        } else {
            if (SgType *baseType = typedefType->get_base_type()) {
                typeDeclaration(baseType);
                classDeclarations << "typedef " << baseType->unparseToString()
                                  << " " << tp->unparseToString() << ";"
                                  << std::endl;
            }
        }
    } else if (SgPointerType *ptrType = isSgPointerType(tp)) {
        if (SgType *baseType = ptrType->get_base_type()) {
            typeDeclaration(baseType);
        }

    } else if (SgEnumType *enumType = isSgEnumType(tp)) {
        classDeclarations << enumType->get_declaration()->unparseToString()
                          << std::endl;
    } else {
        std::cout << "Type Class: " << typeClass << std::endl;
        std::cout << "@@@@@@@@@@@@@ Exiting typeDeclaration!!!" << std::endl;
    }
}

/**
 * @brief Function that inserts global variable declarations in RESTORE driver
 * file
 */
void Tracer::insertGlobalVarDeclarations() {
    for (int i = 0; i < globalNames.size(); i++) {
        SgName name(globalNames[i]);
        SgVariableSymbol *smbl = globalscope->lookup_variable_symbol(name);
        if (smbl == nullptr) {
            std::cout << "Can't find variable symbol! " << std::endl;
        }
        if (smbl)
            variableDeclaration(smbl);
    }
    restoreOutfile << variableDeclarations.str();
    variableDeclarations.str("");
}

/**
 * @brief Function that inserts local variable declarations in string stream
 *        that will be inserted in RESTORE driver file
 */
void Tracer::variableDeclaration(SgVariableSymbol *smbl) {
    SgDeclarationStatement *varDecl =
        smbl->get_declaration()->get_declaration();
    SgType *varType = smbl->get_declaration()->get_type();
    typeDeclaration(varType);
    variableDeclarations << varDecl->unparseToString() << std::endl;
}

/**
 * @brief Function that inserts main function in RESTORE driver file
 */
void Tracer::insertMainFunction() {
    restoreOutfile << "int main(void) {\n";
    // Stack allocation
    restoreOutfile << "register void* preRSP __asm__ (\"sp\");\n";
    restoreOutfile << "unsigned long size = ((unsigned long long)preRSP) - "
                      "((unsigned long long) min_stack_address);\n";
    restoreOutfile << "printf(\"size=%d\\n\", size);\n";
    restoreOutfile << "void* ptr = alloca (size);\n";
    restoreOutfile << "printf(\"sp = %p\\n\", ptr);\n";
    // Restore heap and stack
    restoreOutfile << "my_mallocMemoryChunkInclusive(\"myDataFile/test.hd\", "
                      "min_heap_address, max_heap_address); \n";
    restoreOutfile << "// Restored heap.  Now safe to use heap, including "
                      "fopen(), etc. \n";
    restoreOutfile << "readDataRangeFromFile(\"myDataFile/test.st\", "
                      "min_stack_address, max_stack_address);\n";
    restoreOutfile << "// Restored stack.\n";
    // Restore global variables
    insertGlobalVariablesRead();

    // Call a loop function
    insertLoopFuncCall();

    restoreOutfile << "}\n";
}

/**
 * @brief Function that inserts fread lines to restore global variables in
 * RESTORE driver file
 */
void Tracer::insertGlobalVariablesRead() {
    restoreOutfile << "FILE* fp = fopen(\"myDataFile/test.nhd\", \"r\");\n";
    for (int i = 0; i < globalNames.size(); i++) {
        SgName name(globalNames[i]);
        SgVariableSymbol *smbl = globalscope->lookup_variable_symbol(name);
        if (smbl) {
            restoreOutfile << "fread ((void*)&" << globalNames[i]
                           << ", sizeof (" << globalNames[i] << "), 1, fp);\n";
        } else {
            std::cout << "NOT found variable with name " << globalNames[i]
                      << std::endl;
        }
    }
    restoreOutfile << "fclose(fp);\n";
}

/**
 * @brief Function that inserts function call to loop function in RESTORE driver
 * file Parameters of the loop function are the pointers to the memory (either
 * stack or heap)
 */
void Tracer::insertLoopFuncCall() {
    SgExprStatement *exprStmt = isSgExprStatement(loopFuncNode);
    if (exprStmt) {
        SgExpression *expr = exprStmt->get_expression();
        SgFunctionCallExp *funcExpr = isSgFunctionCallExp(expr);
        if (funcExpr) {
            std::string funcName = funcExpr->get_function()->unparseToString();
            restoreOutfile << funcName << " (";
            auto funcArgs = funcExpr->get_args()->get_expressions();
            for (int i = 0; i < funcArgs.size(); i++) {
                if (i > 0)
                    restoreOutfile << ", ";
                auto funcArgument = funcArgs[i];
                SgVarRefExp *varArg = isSgVarRefExp(funcArgument);
                if (varArg) {
                    SgPointerType *ptrToVar =
                        SageBuilder::buildPointerType(varArg->get_type());
                    restoreOutfile << "*SAVED_" << varArg->unparseToString();
                } else if (isSgAddressOfOp(funcArgument)) {
                    SgAddressOfOp *addrArg = isSgAddressOfOp(funcArgument);
                    SgType *type = addrArg->get_type();
                    auto operand = addrArg->get_operand();
                    SgType *operandType = operand->get_type();
                    restoreOutfile << "SAVED_" << operand->unparseToString();
                } else
                    std::cout << "Argument is not a variable expression! "
                              << std::endl;
            }
            restoreOutfile << ");" << std::endl;
        } else
            std::cout << "Something went wrong with funcExpr " << std::endl;
    } else
        std::cout << "SOMETHING WENT WRONG with exprStmt!" << std::endl;

    std::cout << "Inserting loop function call! " << std::endl;
}

/**
 * @brief Function that moves RESTORE driver file to the codelet directory
 */
void Tracer::moveDriverFile(string prefixStr, string funcName,
                            string baseFileName) {
    string dirPath = "./LoopExtractor_data/codelet_" + funcName + "/";
    string mkdirCommand = "mkdir -p " + dirPath;
    string result = executeCommand(mkdirCommand);
    if (result.find("failed") != string::npos) {
        cout << "mkdir FAILED!!!!" << endl;
    }
    string targetPath = dirPath + prefixStr + "_" + baseFileName;
    moveFile(baseFileName, targetPath);
}

/**
 * @brief Function that inserts lines of code to save data in SAVE source file
 */
void Tracer::insertSaveInfo() {
    SageBuilder::pushScopeStack(loopFuncScope);

    SgStatement *ifBody = buildDataSavingLines();
    buildInstanceCheck(current_lfi->getInstanceNum(), ifBody);
    buildInstanceIncrement();

    SageBuilder::popScopeStack();
}

/**
 * @brief Function that generates a basic block with most of code lines to save
 * data
 * @return SgStatement* that contains the generated basic block
 */
SgStatement *Tracer::buildDataSavingLines() {
    SageInterface::insertHeader("addresses.h", PreprocessingInfo::after, false,
                                globalscope);
    /* Most of code lines will be in a single basic block */
    std::vector<SgStatement *> basicBlockStmts;
    /* Saving Loop Parameter addresses */
    std::vector<SgStatement *> funcParamsStmts = saveLoopFuncParamAddresses();
    for (int i = 0; i < funcParamsStmts.size(); i++) {
        basicBlockStmts.push_back(funcParamsStmts[i]);
    }
    /* Saving global variables */
    std::vector<SgStatement *> globalVarStmts = saveGlobalVars();
    for (int i = 0; i < globalVarStmts.size(); i++) {
        basicBlockStmts.push_back(globalVarStmts[i]);
    }
    /* Environment variables */
    basicBlockStmts.push_back(buildVarDecl("_end", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("_etext", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("_start", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("_edata", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("__bss_start", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("__data_start", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("environ", "extern char**"));
    /* Segment (stack, heap, data segment) variables */
    std::vector<SgStatement *> segmentPtrs = buildSegmentPtrs();
    for (int i = 0; i < segmentPtrs.size(); i++) {
        basicBlockStmts.push_back(segmentPtrs[i]);
    }
    basicBlockStmts.push_back(
        buildPrintFunc("BP(STACK END): %09lx\\n", "basepointer"));
    basicBlockStmts.push_back(
        buildPrintFunc("SP(STACK BEGIN): %09lx\\n", "((char*)stackpointer)-1"));
    basicBlockStmts.push_back(
        buildPrintFunc("DS START: %09lx\\n", "&__data_start"));
    basicBlockStmts.push_back(
        buildPrintFunc("DS END: %09lx\\n", "((char*)&_end)-1"));
    basicBlockStmts.push_back(buildPrintFunc("HEAP START: %09lx\\n", "&_end"));
    basicBlockStmts.push_back(buildPrintFunc("HEAP END: %09lx\\n", "brk"));
    /* Saving heap and stack */
    basicBlockStmts.push_back(buildWriteHeap("myDataFile/test"));
    basicBlockStmts.push_back(buildWriteStack("myDataFile/test"));

    SgStatement *result = SageBuilder::buildBasicBlock_nfi(basicBlockStmts);
    return result;
}

/**
 * @brief Function that generates heap saving lines of code
 */
SgStatement *Tracer::buildWriteHeap(string datafileName) {
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
SgStatement *Tracer::buildWriteStack(string datafileName) {
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
 * @brief Function that inserts header lines to SAVE source file
 */
void Tracer::buildHeaders() {
    SageInterface::insertHeader("unistd.h", PreprocessingInfo::after, false,
                                globalscope);
    SageInterface::insertHeader("config.h", PreprocessingInfo::after, false,
                                globalscope);
    SageInterface::insertHeader("util.h", PreprocessingInfo::after, false,
                                globalscope);
    SageInterface::insertHeader("alloca.h", PreprocessingInfo::after, false,
                                globalscope);
}

/**
 * @brief Function that moves SAVE source file to the codelet directory
 */
void Tracer::moveCodeletSourcefile(string prefixStr, string funcName,
                                   string baseFileName, bool isRestore) {
    string dirPath = "./LoopExtractor_data/codelet_" + funcName + "/";
    string mkdirCommand = "mkdir -p " + dirPath;
    string result = executeCommand(mkdirCommand);
    if (result.find("failed") != string::npos) {
        cout << "mkdir FAILED!!!!" << endl;
    }
    string targetPath = dirPath + prefixStr + "_" + baseFileName;
    string prefixOfGeneratedSourcefile = isRestore ? "restore_" : "rose_";
    moveFile(prefixOfGeneratedSourcefile + baseFileName, targetPath);
}

/**
 * @brief Function that inserts code lines to TRACE source file
 */
void Tracer::insertTraceInfo() {
    SageBuilder::pushScopeStack(loopFuncScope);

    SgStatement *ifBody = buildAddrPrinting();
    buildInstanceCheck(current_lfi->getInstanceNum(), ifBody);
    buildInstanceIncrement();

    SageBuilder::popScopeStack();
}

/**
 * @brief Setters of the class
 */
void Tracer::setBaseFileName(std::string fileName) {
    this->baseFileName = fileName;
}
void Tracer::setLoopExtrIncludeFlag(std::string loopExtrIncludeFlag) {
    this->loopExtrIncludeFlag = loopExtrIncludeFlag;
}
void Tracer::setFilenameVec(std::vector<std::string> filenameVec) {
    this->filenameVec = filenameVec;
}
void Tracer::setLoopScope(SgScopeStatement *loopScope) {
    this->loopScope = loopScope;
}
void Tracer::setLoopFuncScope(SgScopeStatement *loopFuncScope) {
    this->loopFuncScope = loopFuncScope;
}
void Tracer::setLoopNode(SgNode *loopNode) { this->loopNode = loopNode; }
void Tracer::setLocalVars(std::vector<std::string> localVariableNames) {
    this->localVariableNames = localVariableNames;
}
void Tracer::setGlobalVars(std::vector<std::string> globalVariableNames) {
    this->globalVariableNames = globalVariableNames;
}
void Tracer::setInsertStatement(SgStatement *insertBefore) {
    this->insertBefore = insertBefore;
}

void Tracer::addLoopFileName(std::string fileName) {
    this->loopFileNames.push_back(fileName);
}

void Tracer::addLoopFuncInfo(LoopFuncInfo *loopFuncInfo) {
    this->LFI.push_back(loopFuncInfo);
}

void Tracer::addHeaderLine(std::string headerLine) {
    this->headerLines.push_back(headerLine);
}

string Tracer::getCurrentLoopFileName() { return this->currentLoopFileName; }

/**
 * @brief Function that generates code lines to print segment boundary addresses
 *        and imitates the behavior of the SAVE code (to avoid different memory
 * allocation)
 * @return SgStatement* that contains the generated basic block
 */
SgStatement *Tracer::buildAddrPrinting() {
    /* Most of code lines will be in a single basic block */
    std::vector<SgStatement *> basicBlockStmts;
    /* Saving Loop Parameter addresses */
    std::vector<SgStatement *> funcParamsStmts = saveLoopFuncParamAddresses();
    for (int i = 0; i < funcParamsStmts.size(); i++) {
        basicBlockStmts.push_back(funcParamsStmts[i]);
    }
    /* Saving global variables */
    vector<SgStatement *> globalVarStmts = saveGlobalVars();
    for (int i = 0; i < globalVarStmts.size(); i++) {
        basicBlockStmts.push_back(globalVarStmts[i]);
    }
    /* Environment variables */
    basicBlockStmts.push_back(buildVarDecl("_end", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("_etext", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("_start", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("_edata", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("__bss_start", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("__data_start", "extern int"));
    basicBlockStmts.push_back(buildVarDecl("environ", "extern char**"));
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
        buildPrintFunc("BP(STACK END): %09lx\\n", "basepointer"));
    basicBlockStmts.push_back(
        buildPrintFunc("SP(STACK BEGIN): %09lx\\n", "((char*)stackpointer)-1"));
    basicBlockStmts.push_back(
        buildPrintFunc("DS START: %09lx\\n", "&__data_start"));
    basicBlockStmts.push_back(
        buildPrintFunc("DS END: %09lx\\n", "((char*)&_end)-1"));
    basicBlockStmts.push_back(buildPrintFunc("HEAP START: %09lx\\n", "&_end"));
    basicBlockStmts.push_back(buildPrintFunc("HEAP END: %09lx\\n", "brk"));
    /* Imitation of SAVE code */
    basicBlockStmts.push_back(buildPrintImitFunc("myDataFile/test"));
    basicBlockStmts.push_back(buildPrintImitFunc("myDataFile/test"));

    SgStatement *result = SageBuilder::buildBasicBlock_nfi(basicBlockStmts);
    return result;
}

/**
 * @brief Function that generates if statement for instance check
 * @param instanceNum - number of the instance
 * @param ifBody - body of the if statement (basic block)
 */
void Tracer::buildInstanceCheck(int instanceNum, SgStatement *body) {
    /* cond is "extr_instance == 1" */
    SgVarRefExp *instVar = SageBuilder::buildVarRefExp("extr_instance");
    // TODO: should be instanceNum instead of 1
    SgIntVal *oneVal = SageBuilder::buildIntVal(1);
    SgEqualityOp *cmp = SageBuilder::buildEqualityOp(instVar, oneVal);
    SgStatement *cond = SageBuilder::buildExprStatement(cmp);
    SgIfStmt *instCheck = SageBuilder::buildIfStmt(cond, body, nullptr);
    SageInterface::insertStatementBefore(insertBefore, instCheck);
}

/**
 * @brief Function that generate the increment of an instance counter
 */
void Tracer::buildInstanceIncrement() {
    SgVarRefExp *instVar = SageBuilder::buildVarRefExp("extr_instance");
    instVar->set_parent(globalscope); // SageBuilder::topScopeStack());
    SgPlusPlusOp *incOp = SageBuilder::buildPlusPlusOp(instVar);
    incOp->set_parent(globalscope); // SageBuilder::topScopeStack());
    SgStatement *incStmt = SageBuilder::buildExprStatement(incOp);
    incStmt->set_parent(globalscope); // SageBuilder::topScopeStack());
    SageInterface::insertStatement(insertBefore, incStmt);
}

/**
 * @brief Function that generates a variable declaration
 * @param varName - name of the variable
 * @param varType - type of the variable
 * @return SgStatement* that contains the generated variable declaration
 */
SgStatement *Tracer::buildVarDecl(std::string varName, std::string varType) {
    SgType *brkType =
        SageBuilder::buildOpaqueType(varType, SageBuilder::topScopeStack());
    SgVariableDeclaration *brkStmt =
        SageBuilder::buildVariableDeclaration(varName, brkType);
    return brkStmt;
}

/**
 * @brief Function that generates code lines that traces segment boundaries
 *        by receiving the addresses of base frame (rbp) and stack frame (rsp)
 * @return vector of SgStatement* that contains the generated code lines
 */
vector<SgStatement *> Tracer::buildSegmentPtrs() {
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
SgStatement *Tracer::buildPrintFunc(std::string printStr,
                                    std::string variableName) {
    SgType *return_type = SageBuilder::buildIntType();
    SgExprListExp *arg_list = SageBuilder::buildExprListExp();
    SgStringVal *arg = SageBuilder::buildStringVal(printStr);
    SageInterface::appendExpression(arg_list, arg);
    SgVarRefExp *varArg = SageBuilder::buildVarRefExp(SgName(variableName));
    SageInterface::appendExpression(arg_list, varArg);
    SgExprStatement *callStmt1 = SageBuilder::buildFunctionCallStmt(
        SgName("printf"), return_type, arg_list);
    return callStmt1;
}

/**
 * @brief Function that generates code lines that imitates SAVE code
 *        and prints line that is supposed to be saved in a header file
 * @param printStr - parameter of printf function call (format string)
 * @return generated printf call statement
 */
SgStatement *Tracer::buildPrintImitFunc(std::string printStr) {
    SgType *return_type = SageBuilder::buildIntType();
    SgExprListExp *arg_list = SageBuilder::buildExprListExp();
    SgStringVal *arg = SageBuilder::buildStringVal(printStr);
    SageInterface::appendExpression(arg_list, arg);
    SgExprStatement *callStmt1 = SageBuilder::buildFunctionCallStmt(
        SgName("printf"), return_type, arg_list);
    return callStmt1;
}

/**
 * @brief Function that generates code lines that calls brk function
 *        to get heap address
 * @return vector of SgStatement* that contains the generated code lines
 */
std::vector<SgStatement *> Tracer::buildBrkStmt() {
    std::vector<SgStatement *> ret;
    SgStatement *brkDecl = buildVarDecl("brk", "char*");
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
 * @brief Function that generates code lines that saves global variable
 *        addresses in a datafile
 * @return vector of SgStatement* that contains the generated code lines
 */
std::vector<SgStatement *> Tracer::saveGlobalVars() {
    std::vector<SgStatement *> ret;
    /* 'FILE* fp;' line of a function pointer declaration */
    auto file_type = SageBuilder::buildPointerType(
        SageBuilder::buildOpaqueType("FILE", SageBuilder::topScopeStack()));
    std::string uniqueFileName = SageInterface::generateUniqueVariableName(
        SageBuilder::topScopeStack(), "fp");
    auto fileNameDecl = SageBuilder::buildVariableDeclaration(
        uniqueFileName, file_type, NULL, SageBuilder::topScopeStack());
    ret.push_back(fileNameDecl);
    /* 'fp = fopen("datafile", "w");' line of a function call */
    SgExpression *fp = SageBuilder::buildVarRefExp(fileNameDecl);
    SgExprListExp *fopen_arg_list = SageBuilder::buildExprListExp();
    SgStringVal *file_name = SageBuilder::buildStringVal("myDataFile/test.nhd");
    SgStringVal *file_modifier = SageBuilder::buildStringVal("w");
    SageInterface::appendExpression(fopen_arg_list, file_name);
    SageInterface::appendExpression(fopen_arg_list, file_modifier);
    SgFunctionCallExp *rhs = SageBuilder::buildFunctionCallExp(
        "fopen", file_type, fopen_arg_list, SageBuilder::topScopeStack());
    SgStatement *fopenStmt = SageBuilder::buildAssignStatement(fp, rhs);
    ret.push_back(fopenStmt);
    /* 'fwrite(&var, sizeof(var), 1, fp);' line of a function call for each
     * global variable */
    SgSymbolTable *global_tbl = globalscope->get_symbol_table();
    SgType *return_void_type = SageBuilder::buildVoidType();
    unsigned numOfGlobalVariables = globalVariableNames.size();
    for (int i = 0; i < numOfGlobalVariables; i++) {
        SgVariableSymbol *smbl =
            global_tbl->find_variable(SgName(globalVariableNames[i]));
        if (smbl != nullptr) {
            SgExprListExp *fwrt_arg_list = SageBuilder::buildExprListExp();
            std::string varName = "&";
            varName += smbl->get_name().getString();
            SgVarRefExp *varRef = SageBuilder::buildVarRefExp(SgName(varName));
            SageInterface::appendExpression(fwrt_arg_list, varRef);
            SgExprListExp *sizeArg = SageBuilder::buildExprListExp();
            SageInterface::appendExpression(sizeArg,
                                            SageBuilder::buildVarRefExp(smbl));
            SgFunctionCallExp *sizeFunc = SageBuilder::buildFunctionCallExp(
                "sizeof", SageBuilder::buildUnsignedIntType(), sizeArg);
            SageInterface::appendExpression(fwrt_arg_list, sizeFunc);
            SgIntVal *oneVal = SageBuilder::buildIntVal(1);
            SageInterface::appendExpression(fwrt_arg_list, oneVal);
            SageInterface::appendExpression(
                fwrt_arg_list, fp); // inserting fp to the list of arguments
            SgExprStatement *fwrt = SageBuilder::buildFunctionCallStmt(
                "fwrite", return_void_type, fwrt_arg_list);
            ret.push_back(fwrt);
        }
    }
    /* 'fclose(fp);' line of a function call */
    SgExprListExp *fclose_arg_list = SageBuilder::buildExprListExp();
    SgExpression *filePointer = SageBuilder::buildVarRefExp(fileNameDecl);
    SageInterface::appendExpression(fclose_arg_list, filePointer);
    SgExprStatement *fcloseStmt = SageBuilder::buildFunctionCallStmt(
        SgName("fclose"), return_void_type, fclose_arg_list);
    ret.push_back(fcloseStmt);
    return ret;
}

/**
 * @brief Function that generates code lines that saves loop function
 *        parameter addresses in a header file
 * @return vector of SgStatement* that contains the generated code lines
 */
vector<SgStatement *> Tracer::saveLoopFuncParamAddresses() {
    vector<SgStatement *> ret;
    SgExprStatement *exprStmt = isSgExprStatement(insertBefore);
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
                for (int i = 0; i < numOfArgs; i++) {
                    auto funcArgument = funcArgs[i];
                    SgVarRefExp *varArg = isSgVarRefExp(funcArgument);
                    if (varArg) {
                        /* if the argument is a variable */
                        SgExprListExp *fprintf_line_args =
                            SageBuilder::buildExprListExp();
                        SageInterface::appendExpression(fprintf_line_args, lhs);
                        std::string fpline = "#define SAVED_";
                        fpline.append(varArg->unparseToString());
                        fpline.append(" (");
                        fpline.append(varArg->get_type()->unparseToString());
                        fpline.append("*)%ld \\n");
                        SgStringVal *lineVal =
                            SageBuilder::buildStringVal(fpline);
                        SageInterface::appendExpression(fprintf_line_args,
                                                        lineVal);
                        std::string varName = "&";
                        varName.append(varArg->unparseToString());
                        SgVarRefExp *varRef =
                            SageBuilder::buildVarRefExp(SgName(varName));
                        SageInterface::appendExpression(fprintf_line_args,
                                                        varRef);
                        SgExprStatement *fprintf_funccall =
                            SageBuilder::buildFunctionCallStmt(
                                "fprintf", return_void_type, fprintf_line_args);
                        ret.push_back(fprintf_funccall);
                    } else if (isSgAddressOfOp(funcArgument)) {
                        /* if the argument is a reference */
                        SgAddressOfOp *addrArg = isSgAddressOfOp(funcArgument);
                        SgType *type = addrArg->get_type();
                        auto operand = addrArg->get_operand();
                        SgType *operandType = operand->get_type();
                        SgExprListExp *fprintf_line_args =
                            SageBuilder::buildExprListExp();
                        SageInterface::appendExpression(fprintf_line_args, lhs);
                        std::string fpline = "#define SAVED_";
                        fpline.append(operand->unparseToString());
                        fpline.append(" (");
                        fpline.append(type->unparseToString());
                        fpline.append(")%ld \\n");
                        SgStringVal *lineVal =
                            SageBuilder::buildStringVal(fpline);
                        SageInterface::appendExpression(fprintf_line_args,
                                                        lineVal);
                        std::string varName = "&";
                        varName.append(operand->unparseToString());
                        SgVarRefExp *varRef =
                            SageBuilder::buildVarRefExp(SgName(varName));
                        SageInterface::appendExpression(fprintf_line_args,
                                                        varRef);
                        SgExprStatement *fprintf_funccall =
                            SageBuilder::buildFunctionCallStmt(
                                "fprintf", return_void_type, fprintf_line_args);
                        ret.push_back(fprintf_funccall);

                    } else
                        std::cout << "Argument is not a variable expression! \n"
                                  << "funcArgument: "
                                  << funcArgument->unparseToString()
                                  << std::endl;
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