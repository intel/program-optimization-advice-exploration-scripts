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

string Extractor::getFileName(const string &fileNameWithPath) {
  int lastSlashPos = fileNameWithPath.find_last_of('/');
  int lastDotPos   = fileNameWithPath.find_last_of('.');
  string fileStr   = (fileNameWithPath.substr(lastSlashPos + 1,
                                            lastDotPos - lastSlashPos - 1));
  /* Since you cannot start Function name with a digit */
  if (isdigit(fileStr[0]))
    fileStr.insert(0, 1, '_');
  /* Since you cannot have '-' in Function name */
  while (fileStr.find('-') != string::npos)
    fileStr.replace(fileStr.find('-'), 1, string("X_X"));
  return fileStr;
}

string Extractor::getOrigFileName(const string &fileNameWithPath) {
  int lastSlashPos = fileNameWithPath.find_last_of('/');
  int lastDotPos   = fileNameWithPath.find_last_of('.');
  return (
      fileNameWithPath.substr(lastSlashPos + 1, lastDotPos - lastSlashPos - 1));
}

string Extractor::getFileExtn(const string &fileNameWithPath) {
  int lastDotPos = fileNameWithPath.find_last_of('.');
  string extn    = fileNameWithPath.substr(lastDotPos + 1);
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

string Extractor::getExtractionFileName(SgNode *astNode) {
  string fileNameWithPath = (astNode->get_file_info())->get_filenameString();
  LoopExtractor_file_path = getFilePath(fileNameWithPath);
  LoopExtractor_file_name = getFileName(fileNameWithPath);
  LoopExtractor_original_file_name = getOrigFileName(fileNameWithPath);
  LoopExtractor_file_extn          = getFileExtn(fileNameWithPath);
  int lineNumber                   = getAstNodeLineNum(astNode);

  string output_path = getDataFolderPath();
  string file_name   = LoopExtractor_original_file_name;
  string file_extn   = LoopExtractor_file_extn;

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

  return output_path + file_name;
}

void Extractor::updateUniqueCounter(SgNode *astNode) {
  uniqueCounter    = 0;
  string file_name = getExtractionFileName(astNode);
  boost::erase_all(file_name, getDataFolderPath());
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
  while (loopName.find('-') != string::npos)
    loopName.replace(loopName.find('-'), 1, string("X_X"));
  boost::erase_all(loopName, getDataFolderPath());
  /* Since you cannot start Function name with a digit */
  if (isdigit(loopName[0]))
    loopName.insert(0, 1, '_');
  boost::erase_all(loopName, "." + LoopExtractor_file_extn);
  return loopName;
}

void Extractor::printHeaders(ofstream &loop_file_buf) {
  vector<string>::iterator iter;
  bool hasOMP         = false;
  bool hasIO          = false;
  if_else_macro_count = 0;

  for (iter = header_vec.begin(); iter != header_vec.end(); iter++) {
    string header_str = *iter;
    /* If including a .c file then copy to LE data folder */
    if (header_str.find(".c") != string::npos) {
      continue;
    }
    if (header_str.find("#endif") == 0 && if_else_macro_count == 0)
      continue;
    loop_file_buf << header_str; // header_vec has space at the end already
    if (header_str.find("omp.h") != string::npos)
      hasOMP = true;
    if (src_type == src_lang_C && header_str.find("stdio.h") != string::npos)
      hasIO = true;
    if (src_type == src_lang_CPP && header_str.find("iostream") != string::npos)
      hasIO = true;

    if (header_str.find("#if") == 0)
      if_else_macro_count++;
    if (header_str.find("#endif") == 0)
      if_else_macro_count--;
  }

  // TODO: if it is a fortran code
  if (!hasOMP && (src_type == src_lang_C || src_type == src_lang_CPP))
    loop_file_buf << "#include <omp.h>" << endl;
  if (src_type == src_lang_C && !hasIO)
    loop_file_buf << "#include <stdio.h>" << endl;
  if (src_type == src_lang_CPP && !hasIO)
    loop_file_buf << "#include <iostream>" << endl;
}

void Extractor::printGlobalsAsExtern(ofstream &loop_file_buf) {
  vector<string>::iterator iter;
  for (iter = global_vars.begin(); iter != global_vars.end(); iter++) {
    string var_str = *iter;
    if (var_str.find("pragma") != string::npos)
      loop_file_buf << var_str << endl;
    else {
      /* In case struct type contains stuct definition */
      if (var_str.find("struct") != string::npos &&
          var_str.find("{") != string::npos) {
        var_str.erase(var_str.find_first_of("{"),
                      var_str.find_last_of("}") - var_str.find_first_of("{") +
                          1);
      }
      loop_file_buf << "extern " << var_str << ";" << endl;
    }
  }
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
  vector<string> temp_vec2;
  SageInterface::collectVarRefs(dynamic_cast<SgLocatedNode *>(loop), sym_table);

  if (extr.getOMPpragma() != "")
    analyzeOMPprivateArrays(extr.getOMPpragma());

  vector<SgVarRefExp *>::iterator iter;
  for (iter = sym_table.begin(); iter != sym_table.end(); iter++) {
    SgVariableSymbol *var       = (*iter)->get_symbol();
    SgScopeStatement *var_scope = (var->get_declaration())->get_scope();

    /* To clean OMP clauses with non-scope variables */
    if (extr.getOMPpragma() != "")
      OMPscope_symbol_vec.push_back(var->get_name().getString());
    /* Neither globals variables nor variables declared inside the loop body nor
     * struct members(dirty way - scope name not NULL) should be passed */
    if (!(isSgGlobal(var_scope) || isDeclaredInInnerScope(var_scope) ||
          var_scope->get_qualified_name() != "") &&
        find(scope_vars_symbol_vec.begin(), scope_vars_symbol_vec.end(), var) ==
            scope_vars_symbol_vec.end()) {
      // cerr << "Var Scope: "<< var->get_name().getString() << ", " <<
      // var_scope->get_qualified_name() << endl;
      // SgVariableSymbol *var = dynamic_cast<SgVariableSymbol *>(*iter);
      string temp_str1;
      string var_type_str = (var->get_type())->unparseToString();
      if (extr.getSrcType() == src_lang_C) {
        /*
         * Add '_primitive' after primitive parameter name,
         * so that actual name can be used inside the body
         */
        // cerr << "Var info: "<<var->get_name().getString() << ", " <<
        // (var->get_type())->variantT() << endl;
        bool isTypedefArray  = false;
        bool isTypedefStruct = false;
        if ((var->get_type())->variantT() == V_SgTypedefType) {
          SgTypedefType *type_def_var =
              dynamic_cast<SgTypedefType *>(var->get_type());
          if ((type_def_var->get_base_type())->variantT() == V_SgArrayType) {
            isTypedefArray = true;
            // var_type_str =
            // (type_def_var->get_base_type())->unparseToString();
          } else if (SageInterface::isStructType(
                         type_def_var->get_base_type())) {
            isTypedefStruct = true;
            // var_type_str = "struct " + var_type_str;
          }
          // cerr << "Typedef: " << (type_def_var->get_base_type())->variantT()
          // << ", isStruct: " <<
          // SageInterface::isStructType(type_def_var->get_base_type()) << endl;
        }
        /* Skipping OMP private arrays */
        if ((var->get_type())->variantT() == V_SgArrayType || isTypedefArray) {
          temp_str1 = var->get_name().getString();
          if (find(privateOMP_array_vec.begin(), privateOMP_array_vec.end(),
                   temp_str1) != privateOMP_array_vec.end()) {
            temp_vec2.push_back(temp_str1);
            int first_square_brac = var_type_str.find_first_of("[");
            if (first_square_brac != string::npos)
              OMParray_type_map.insert(pair<string, string>(
                  temp_str1, var_type_str.substr(0, first_square_brac) +
                                 var->get_name().getString() +
                                 var_type_str.substr(first_square_brac)));
            else
              OMParray_type_map.insert(pair<string, string>(
                  temp_str1,
                  var_type_str + space_str + var->get_name().getString()));
            continue;
          }
        }
        if ((var->get_type())->variantT() == V_SgArrayType || isTypedefArray) {
          int first_square_brac = var_type_str.find_first_of("[");
          string var_base_type  = var_type_str.substr(0, first_square_brac);
          //          if(!isTypedefArray &&
          //          var_type_str.find(var->get_type()->findBaseType()->unparseToString())
          //          == string::npos)
          //            var_base_type =
          //            var->get_type()->findBaseType()->unparseToString() +
          //            space_str;
          /* Add "restrict" keyword for arrays to get rid of aliasing problem */
          if (LoopExtractor_enabled_options[RESTRICT] &&
              first_square_brac != string::npos) {
            int first_square_close_brac = var_type_str.find_first_of("]");
            string restrict_keyword     = "restrict";
            var_type_str.replace(first_square_brac + 1,
                                 first_square_close_brac - first_square_brac -
                                     1,
                                 restrict_keyword);
          }

          /* To change to var_type var_name[][][] */
          if (first_square_brac != string::npos)
            scope_vars_str_vec.push_back(
                var_base_type + var->get_name().getString() +
                var_type_str.substr(first_square_brac));
          else
            scope_vars_str_vec.push_back(var_type_str + space_str +
                                         var->get_name().getString());
        } else if (SageInterface::isStructType(var->get_type()) ||
                   isTypedefStruct) {
          scope_vars_str_vec.push_back(
              var_type_str + "* " + var->get_name().getString() + "_primitive");
          scope_struct_str_vec.push_back(var->get_name().getString());
        } else if ((var->get_type())->variantT() == V_SgPointerType) {
          SgType *var_pointer_type = var->get_type()->stripType(1 << 2);
          if (var_pointer_type->variantT() == V_SgTypedefType) {
            SgTypedefType *type_def_var =
                dynamic_cast<SgTypedefType *>(var_pointer_type);
            var_pointer_type = type_def_var->get_base_type();
          }
          /* Strip var type hidden under pointer to check if array */
          if (var_pointer_type->variantT() == V_SgArrayType) {
            /* To change to var_type var_name[][][] */
            int first_endparan = var_type_str.find_first_of(")");
            if (first_endparan != string::npos)
              scope_vars_str_vec.push_back(var_type_str.insert(
                  first_endparan, var->get_name().getString()));
            else
              scope_vars_str_vec.push_back(var_type_str + space_str +
                                           var->get_name().getString());
          } else if (var_pointer_type->variantT() == V_SgFunctionType) {
            /* If function pointer, then return_type (*var_name)(params) */
            if (var_type_str.find("(*") != string::npos)
              scope_vars_str_vec.push_back(var_type_str.insert(
                  var_type_str.find("(*") + 2, var->get_name().getString()));
            else // might be a typedef function ptr
              scope_vars_str_vec.push_back(var_type_str + space_str +
                                           var->get_name().getString());
          } else if (SageInterface::isStructType(var_pointer_type)) {
            if (var_type_str.find("{") != string::npos) {
              var_type_str.erase(var_type_str.find_first_of("{"),
                                 var_type_str.find_last_of("}") -
                                     var_type_str.find_first_of("{") + 1);
            }
            scope_vars_str_vec.push_back(var_type_str + "* " +
                                         var->get_name().getString() +
                                         "_primitive");
            scope_struct_str_vec.push_back(var->get_name().getString());
          } else {
            scope_vars_str_vec.push_back(var_type_str + space_str +
                                         var->get_name().getString());
          }
        } else {
          scope_vars_str_vec.push_back(
              var_type_str + "* " + var->get_name().getString() + "_primitive");
          // cout << "Primitive var: " << var->get_name() << endl;
        }
      } else if (extr.getSrcType() == src_lang_CPP) {
        scope_vars_str_vec.push_back(var_type_str + "& " +
                                     var->get_name().getString());
      }
      // cerr << "Symbol Table : " << *(scope_vars_str_vec.rbegin()) << endl;
      scope_vars_symbol_vec.push_back(var); // Needed for function call
      scope_vars_initName_vec.push_back(
          var->get_declaration()); // Needed for function extern defn
    } else if (isSgGlobal(var_scope) && var_scope->get_qualified_name() != "") {
      // cout << "In scope global: " << (var->get_type())->unparseToString() <<
      // space_str << var->get_name().getString() << endl;
      scope_globals_vec.push_back((var->get_type())->unparseToString() +
                                  space_str + var->get_name().getString());
    }
  }
  /* Erase vector of all non-array OMP privates */
  vector<string>::iterator iter2 = privateOMP_array_vec.begin();
  while (iter2 != privateOMP_array_vec.end()) {
    if (find(temp_vec2.begin(), temp_vec2.end(), *iter2) == temp_vec2.end())
      iter2 = privateOMP_array_vec.erase(iter2);
    else
      ++iter2;
  }
}

bool LoopInfo::hasFuncCallInScope() {
  Rose_STL_Container<SgNode *> funcCallList =
      NodeQuery::querySubTree(loop_scope, V_SgFunctionCallExp);
  Rose_STL_Container<SgNode *>::iterator funcCallIter = funcCallList.begin();
  /* If loop contain no function call */
  if (funcCallIter == funcCallList.end())
    return false;

  for (; funcCallIter != funcCallList.end(); funcCallIter++) {
    SgFunctionCallExp *funcCallExp = isSgFunctionCallExp(*funcCallIter);
    //    bool inliningOK = doInline(funcCallExp);
    //    if(inliningOK) continue;
    SgFunctionDeclaration *funcDecl =
        funcCallExp->getAssociatedFunctionDeclaration();
    if (funcDecl != NULL && !SageInterface::isExtern(funcDecl)) {
      scope_funcCall_vec.insert(funcDecl);
    }
  }
  if (!scope_funcCall_vec.empty())
    return true;
  return false;
}

void LoopInfo::addScopeFuncAsExtern(string &externFuncStr) {
  set<SgFunctionDeclaration *>::iterator iter;
  for (iter = scope_funcCall_vec.begin(); iter != scope_funcCall_vec.end();
       iter++) {
    SgFunctionDeclaration *declFunc = *iter;
    bool consider_as_Extern         = true;
    /* Check if it is a inline function */
    for (auto const &inlineFunc : extr.inline_func_map) {
      if (SageInterface::isSameFunction(declFunc, inlineFunc.first)) {
        externFuncStr += inlineFunc.second;
        consider_as_Extern = false;
      }
    }
    if (consider_as_Extern)
      externFuncStr += "extern " + declFunc->unparseToString() + '\n';
  }
}

void LoopInfo::addScopeGlobalsAsExtern(string &externGlobalsStr) {
  for (auto const &str : scope_globals_vec) {
    externGlobalsStr += "extern " + str + ";\n";
  }
}

/* Only called if C */
void LoopInfo::pushPointersToLocalVars(ofstream &loop_file_buf) {
  // ofstream& loop_file_buf = extr.loop_file_buf;

  vector<SgVariableSymbol *>::iterator iter;
  for (iter = scope_vars_symbol_vec.begin();
       iter != scope_vars_symbol_vec.end(); iter++) {
    SgVariableSymbol *var = (*iter);
    string var_type_str   = (var->get_type())->unparseToString();
    string var_name_str   = (var->get_name()).getString();
    bool isTypedefArray   = false;
    bool isTypedefStruct  = false;
    if ((var->get_type())->variantT() == V_SgTypedefType) {
      SgTypedefType *type_def_var =
          dynamic_cast<SgTypedefType *>(var->get_type());
      if ((type_def_var->get_base_type())->variantT() == V_SgArrayType)
        isTypedefArray = true;
      if (SageInterface::isStructType(type_def_var->get_base_type()))
        isTypedefStruct = true;
    }
    bool isPrimitive = true;
    if ((var->get_type())->variantT() == V_SgArrayType || isTypedefArray) {
      isPrimitive = false;
    } else if (SageInterface::isStructType(var->get_type()) ||
               isTypedefStruct) {
      isPrimitive = true;
    } else if ((var->get_type())->variantT() == V_SgPointerType) {
      isPrimitive              = false;
      SgType *var_pointer_type = var->get_type()->stripType(1 << 2);
      if (var_pointer_type->variantT() == V_SgTypedefType) {
        SgTypedefType *type_def_var =
            dynamic_cast<SgTypedefType *>(var_pointer_type);
        var_pointer_type = type_def_var->get_base_type();
      }
      if (SageInterface::isStructType(var_pointer_type))
        isPrimitive = true;
    }
    /* In case struct type contains stuct definition */
    if (isPrimitive && var_type_str.find("{") != string::npos) {
      var_type_str.erase(var_type_str.find_first_of("{"),
                         var_type_str.find_last_of("}") -
                             var_type_str.find_first_of("{") + 1);
    }

    if (isPrimitive) {
      loop_file_buf << var_type_str << " " << var_name_str << " = "
                    << "*" << var_name_str << "_primitive"
                    << ";" << endl;
    }
  }
}

/* Only called if C */
void LoopInfo::popLocalVarsToPointers(ofstream &loop_file_buf) {
  // ofstream& loop_file_buf = extr.loop_file_buf;

  vector<SgVariableSymbol *>::iterator iter;
  for (iter = scope_vars_symbol_vec.begin();
       iter != scope_vars_symbol_vec.end(); iter++) {
    SgVariableSymbol *var = (*iter);
    string var_type_str   = (var->get_type())->unparseToString();
    string var_name_str   = (var->get_name()).getString();
    bool isTypedefArray   = false;
    bool isTypedefStruct  = false;
    if ((var->get_type())->variantT() == V_SgTypedefType) {
      SgTypedefType *type_def_var =
          dynamic_cast<SgTypedefType *>(var->get_type());
      if ((type_def_var->get_base_type())->variantT() == V_SgArrayType)
        isTypedefArray = true;
      if (SageInterface::isStructType(type_def_var->get_base_type()))
        isTypedefStruct = true;
    }

    bool isConst = false;
    if (SageInterface::isConstType(var->get_type()))
      isConst = true;

    bool isPrimitive = true;
    if ((var->get_type())->variantT() == V_SgArrayType || isTypedefArray) {
      isPrimitive = false;
    } else if (SageInterface::isStructType(var->get_type()) ||
               isTypedefStruct) {
      isPrimitive = true;
    } else if ((var->get_type())->variantT() == V_SgPointerType) {
      isPrimitive              = false;
      SgType *var_pointer_type = var->get_type()->stripType(1 << 2);
      if (var_pointer_type->variantT() == V_SgTypedefType) {
        SgTypedefType *type_def_var =
            dynamic_cast<SgTypedefType *>(var_pointer_type);
        var_pointer_type = type_def_var->get_base_type();
      }
      if (SageInterface::isStructType(var_pointer_type))
        isPrimitive = true;
    }

    if (isPrimitive && !isConst) {
      loop_file_buf << "*" << var_name_str << "_primitive"
                    << " = " << var_name_str << ";" << endl;
    }
  }
}

/* Static arrays(local) can be private in OMP region, but cannot be passed to
 * Loop function
 * Need to (re)declared inside the loop function and Removed from function
 * parameter */
void LoopInfo::analyzeOMPprivateArrays(const string &pragmaStr) {
  if (pragmaStr.find(" private") != string::npos) {
    int tmp = pragmaStr.find("(", pragmaStr.find(" private"));
    string privateStr =
        pragmaStr.substr(tmp + 1, pragmaStr.find(")", tmp) - tmp - 1);
    boost::char_separator<char> sep(",");
    boost::tokenizer<boost::char_separator<char>> tokens(privateStr, sep);
    for (const auto &t : tokens) {
      string s(t);
      boost::algorithm::trim(s);
      privateOMP_array_vec.push_back(s);
    }
  }
}

string LoopInfo::printOMPprivateArrays() {
  string arrays = "";
  for (auto const &str : privateOMP_array_vec) {
    if (OMParray_type_map.find(str) != OMParray_type_map.end()) {
      arrays += (OMParray_type_map.find(str))->second;
      arrays += ";\n";
    }
  }
  return arrays;
}

/* SPEC write variables, that are not used in OMP loop, inside clauses which
 * extractor doesn't extract */
string LoopInfo::sanitizeOMPpragma(const string &pragmaStr) {
  string sanitizedStr(pragmaStr);
  string tmpStr            = "";
  vector<string> clauseStr = {" private", " lastprivate", " firstprivate",
                              " shared"};
  for (auto const &str : clauseStr) {
    tmpStr = sanitizedStr;
    if (sanitizedStr.find(str) != string::npos) {
      string vars       = "";
      int tmp1          = sanitizedStr.find("(", sanitizedStr.find(str));
      int tmp2          = sanitizedStr.find(")", tmp1);
      string privateStr = sanitizedStr.substr(tmp1 + 1, tmp2 - tmp1 - 1);
      boost::char_separator<char> sep(",");
      boost::tokenizer<boost::char_separator<char>> tokens(privateStr, sep);
      for (const auto &t : tokens) {
        string s(t);
        boost::algorithm::trim(s);
        if (find(OMPscope_symbol_vec.begin(), OMPscope_symbol_vec.end(), s) !=
            OMPscope_symbol_vec.end())
          vars += s + ",";
      }
      if (vars != "")
        tmpStr = sanitizedStr.substr(0, tmp1 + 1) +
                 vars.substr(0, vars.length() - 1) + sanitizedStr.substr(tmp2);
      else
        tmpStr = sanitizedStr.substr(0, sanitizedStr.find(str)) +
                 sanitizedStr.substr(tmp2 + 1);
    }
    sanitizedStr = tmpStr;
  }
  return sanitizedStr;
}

/*
 * Take cares of print complete loop function and adding func calls
 * and extern loop func to the base file.
 * Manages SCoP pragmas.
 * Add OMP Timer around the loop. (Not sure)
 * Manages variables that are needed for extracting the loop.
 */
void LoopInfo::printLoopFunc(ofstream &loop_file_buf) {

  //	ofstream& loop_file_buf = extr.loop_file_buf;

  /* Scope of loop body contains the variables needed for this loop to compile
   */
  for (vector<SgForStatement *>::iterator iter = extr.consecutiveLoops.begin();
       iter != extr.consecutiveLoops.end(); iter++) {
    loop       = *iter;
    loop_scope = (loop->get_loop_body())->get_scope();

    if (hasFuncCallInScope()) {
      string externFuncStr;
      addScopeFuncAsExtern(externFuncStr);
      loop_file_buf << externFuncStr;
    }

    // getParamatersInFunc - Dont need same analysis twice
    getVarsInScope();
  }
  loop       = *(extr.consecutiveLoops.begin());
  loop_scope = (loop->get_loop_body())->get_scope();
  /*
   if( !scope_globals_vec.empty() ){
     string externGlobalsStr;
     addScopeGlobalsAsExtern( externGlobalsStr );
     loop_file_buf << externGlobalsStr;
   }
 */
  // Function definition
  loop_file_buf << endl << "void " << getFuncName() << "( ";
  if (!scope_vars_str_vec.empty()) {
    vector<string>::iterator iter = scope_vars_str_vec.begin();
    loop_file_buf << *iter;
    iter++;
    for (; iter != scope_vars_str_vec.end(); iter++)
      loop_file_buf << ", " << *iter;
  }
  loop_file_buf << " ){" << endl; // Function Start

  // Required only for C, since C++ is passed through reference(&)
  if (extr.getSrcType() == src_lang_C)
    pushPointersToLocalVars(loop_file_buf);

  if (LoopExtractor_enabled_options[PARALLEL] && extr.getOMPpragma() != "")
    loop_file_buf << printOMPprivateArrays() << endl;

  // TODO: Add SCoP pragma based on tool option
  loop_file_buf << "#pragma scop" << endl;

  // Get OMP pragma for this loop
  if (LoopExtractor_enabled_options[PARALLEL] && extr.getOMPpragma() != "")
    loop_file_buf << endl << sanitizeOMPpragma(extr.getOMPpragma()) << endl;

  // Print all the loops
  string kernel_body_str = "";
  for (vector<SgForStatement *>::iterator iter = extr.consecutiveLoops.begin();
       iter != extr.consecutiveLoops.end(); iter++) {
    // Entire Loop Body
    string loop_body_str = "";
    if (extr.getSrcType() == src_lang_C) {
      loop_body_str = (*iter)->unparseToString();
    } else if (extr.getSrcType() == src_lang_CPP) {
      loop_body_str = (*iter)->unparseToString();
    }
    if (loop_body_str.find("#else") == 0)
      loop_body_str.erase(0, loop_body_str.find("\n") + 1);
    if (loop_body_str.find("#endif") == 0)
      loop_body_str.erase(0, loop_body_str.find("\n") + 1);
    kernel_body_str += loop_body_str + '\n';
  }
  loop       = *(extr.consecutiveLoops.begin());
  loop_scope = (loop->get_loop_body())->get_scope();

  loop_file_buf << kernel_body_str << endl;

  loop_file_buf << "#pragma endscop" << endl;

  // Required only for C, since C++ is passed through reference(&)
  if (extr.getSrcType() == src_lang_C)
    popLocalVarsToPointers(loop_file_buf);

  loop_file_buf << "}" << endl; // Function End

  /* close unclosed macros */
  for (int i = 0; i < extr.if_else_macro_count; i++)
    loop_file_buf << "#endif" << endl;
}

void Extractor::addExternDefs(SgFunctionDeclaration *func) {
  externFuncDef.insert(pair<SgStatement *, SgScopeStatement *>(
      dynamic_cast<SgStatement *>(func), loopParentFuncScope));
  // externFuncDef.insert(pair<SgStatement*,SgStatement*>(
  // dynamic_cast<SgStatement *>(func),
  // SageInterface::getFirstStatement(loopParentFuncScope) ));
}

/* Add loop function call as extern in the base source file */
void LoopInfo::addLoopFuncAsExtern() {
  if (extr.getGlobalNode() != NULL) {
    vector<SgInitializedName *>::iterator iter;
    SgFunctionParameterList *paramList =
        SageBuilder::buildFunctionParameterList();
    for (iter = scope_vars_initName_vec.begin();
         iter != scope_vars_initName_vec.end(); iter++) {
      // Create parameter list
      SgName arg_name = (*iter)->get_name();
      SgInitializedName *arg_init_name;
      if (extr.getSrcType() == src_lang_C) {
        // Pointers for C
        bool isTypedefArray  = false;
        bool isTypedefStruct = false;
        if (((*iter)->get_type())->variantT() == V_SgTypedefType) {
          SgTypedefType *type_def_var =
              dynamic_cast<SgTypedefType *>((*iter)->get_type());
          if ((type_def_var->get_base_type())->variantT() == V_SgArrayType)
            isTypedefArray = true;
          else if (SageInterface::isStructType(type_def_var->get_base_type()))
            isTypedefStruct = true;
        }
        if (((*iter)->get_type())->variantT() == V_SgArrayType ||
            isTypedefArray) {
          arg_init_name =
              SageBuilder::buildInitializedName(arg_name, (*iter)->get_type());
        } else if (((*iter)->get_type())->variantT() == V_SgPointerType) {
          SgType *var_pointer_type = (*iter)->get_type()->stripType(1 << 2);
          if (var_pointer_type->variantT() == V_SgTypedefType) {
            SgTypedefType *type_def_var =
                dynamic_cast<SgTypedefType *>(var_pointer_type);
            var_pointer_type = type_def_var->get_base_type();
          }
          if (SageInterface::isStructType(var_pointer_type)) {
            SgPointerType *arg_type =
                SageBuilder::buildPointerType((*iter)->get_type());
            arg_init_name =
                SageBuilder::buildInitializedName(arg_name, arg_type);
          } else {
            arg_init_name = SageBuilder::buildInitializedName(
                arg_name, (*iter)->get_type());
          }
        } else { // TypedefStruct will be handled here
          SgPointerType *arg_type =
              SageBuilder::buildPointerType((*iter)->get_type());
          arg_init_name = SageBuilder::buildInitializedName(arg_name, arg_type);
        }
      } else if (extr.getSrcType() == src_lang_CPP) {
        // Reference for C++
        SgReferenceType *arg_type =
            SageBuilder::buildReferenceType((*iter)->get_type());
        arg_init_name = SageBuilder::buildInitializedName(arg_name, arg_type);
      }
      SageInterface::appendArg(paramList, arg_init_name);
    }
    // Create function declaration
    SgName func_name = getFuncName();
    SgFunctionDeclaration *func =
        SageBuilder::buildNondefiningFunctionDeclaration(
            func_name, SageBuilder::buildVoidType(), paramList,
            extr.getGlobalNode());
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
    if (extr.getSrcType() == src_lang_C) {
      // 'Address Of' for C except when its an array
      bool isTypedefArray  = false;
      bool isTypedefStruct = false;
      if (((*iter)->get_type())->variantT() == V_SgTypedefType) {
        SgTypedefType *type_def_var =
            dynamic_cast<SgTypedefType *>((*iter)->get_type());
        if ((type_def_var->get_base_type())->variantT() == V_SgArrayType)
          isTypedefArray = true;
        else if (SageInterface::isStructType(type_def_var->get_base_type()))
          isTypedefStruct = true;
      }
      if (((*iter)->get_type())->variantT() == V_SgArrayType ||
          isTypedefArray) {
        expr_list.push_back(SageBuilder::buildVarRefExp((*iter)));
      } else if (((*iter)->get_type())->variantT() == V_SgPointerType) {
        SgType *var_pointer_type = (*iter)->get_type()->stripType(1 << 2);
        if (var_pointer_type->variantT() == V_SgTypedefType) {
          SgTypedefType *type_def_var =
              dynamic_cast<SgTypedefType *>(var_pointer_type);
          var_pointer_type = type_def_var->get_base_type();
        }
        if (SageInterface::isStructType(var_pointer_type)) {
          expr_list.push_back(SageBuilder::buildAddressOfOp(
              SageBuilder::buildVarRefExp((*iter))));
        } else {
          expr_list.push_back(SageBuilder::buildVarRefExp((*iter)));
        }
      } else { // typedef struct handled here
        expr_list.push_back(SageBuilder::buildAddressOfOp(
            SageBuilder::buildVarRefExp((*iter))));
      }
    } else if (extr.getSrcType() == src_lang_CPP) {
      // Reference for C++
      expr_list.push_back(SageBuilder::buildVarRefExp((*iter)));
    }
  }
  SgName func_name             = getFuncName();
  SgFunctionCallExp *call_expr = SageBuilder::buildFunctionCallExp(
      func_name, SageBuilder::buildVoidType(),
      SageBuilder::buildExprListExp(expr_list), loop_scope);
  /* Check if previous statement is OMP pragma, then remove it */
  SgStatement *prevStmt = SageInterface::getPreviousStatement(loop, false);
  if (prevStmt != NULL && prevStmt->variantT() == V_SgPragmaDeclaration) {
    SgPragmaDeclaration *pragmaDecl =
        dynamic_cast<SgPragmaDeclaration *>(prevStmt);
    if (SageInterface::extractPragmaKeyword(pragmaDecl) == "omp") {
      SageInterface::replaceStatement(prevStmt,
                                      SageBuilder::buildNullStatement(), true);
    }
  }
  /* Replace for loop with function call - Keep preprocessing info */
  SageInterface::replaceStatement(
      loop, SageBuilder::buildExprStatement(call_expr), true);
}

/* Intended to get rid of variable mentioned in OpenMP clauses that are not
 * required for the loop */
// void Extractor::getVarsInFunction( SgNode *astNode ){
//	/* collectVarRefs will collect all variables used in the function body
//*/
//	vector<SgVarRefExp *> sym_table;
//	SageInterface::collectVarRefs( dynamic_cast<SgLocatedNode *>(astNode),
// sym_table );
//
//	vector<SgVarRefExp *>::iterator iter;
//	for( iter = sym_table.begin(); iter != sym_table.end(); iter++ ){
//		SgVariableSymbol *var = (*iter)->get_symbol();
//		SgScopeStatement *var_scope = ( var->get_declaration()
//)->get_scope();
//
//		/* Neither globals variables nor variables declared inside the
// loop body nor struct members(dirty way - scope name not NULL) should be
// passed
//*/
//		if( !( isSgGlobal(var_scope) ||
// isDeclaredInInnerScope(var_scope)
//|| var_scope->get_qualified_name() != "" ) ){
//      func_var_str_vec.push_back(var->get_name().getString());
//    }
//  }
//}

bool Extractor::skipLoop(SgNode *astNode) {
  if (!loopSkipPragma.empty() &&
      loopSkipPragma.find(LoopExtractor_skiplooppragma_str) != string::npos) {
    loopSkipPragma = "";
    return true;
  }
  SgForStatement *loop    = dynamic_cast<SgForStatement *>(astNode);
  SgScopeStatement *scope = (loop->get_loop_body())->get_scope();
  Rose_STL_Container<SgNode *> returnStmt =
      NodeQuery::querySubTree(scope, V_SgReturnStmt);
  if (returnStmt.begin() != returnStmt.end())
    return true;

  /* Skip loop with macro def in the body, Rose will extract the first instance
   * of complete loop */
  string loop_body_orig = loop->unparseToString();
  string loop_body = loop_body_orig.substr(loop_body_orig.find_first_of("for"));
  if (loop_body.find("#if") != string::npos ||
      loop_body.find("#else") != string::npos ||
      loop_body.find("#endif") != string::npos) {
    int count_if = 0;
    string sub   = "#if";
    for (size_t offset = loop_body.find(sub); offset != string::npos;
         offset        = loop_body.find(sub, offset + sub.length()))
      ++count_if;
    int count_endif = 0;
    sub             = "#endif";
    for (size_t offset = loop_body.find(sub); offset != string::npos;
         offset        = loop_body.find(sub, offset + sub.length()))
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

void Extractor::extractLoops(SgNode *astNode) {
  SgForStatement *loop = dynamic_cast<SgForStatement *>(astNode);
  updateUniqueCounter(astNode);
  string loop_file_name = getExtractionFileName(astNode);

  ofstream loop_file_buf;
  loop_file_buf.open(loop_file_name.c_str(), ofstream::out);

  files_to_compile.insert(loop_file_name);

  // Create loop object
  LoopInfo curr_loop(astNode, loop, getLoopName(astNode), *this);

  printHeaders(loop_file_buf);
  printGlobalsAsExtern(loop_file_buf);

  // cerr << "Adding loop to file: " << curr_loop.getFuncName() << endl;
  /*
   * Take cares of print complete loop function and adding func calls
   * and extern loop func to the base file.
   */
  curr_loop.printLoopFunc(loop_file_buf);
  curr_loop.addLoopFuncCall();
  curr_loop.addLoopFuncAsExtern();

  // to replace remaining consecutive loops with null statements */
  if (consecutiveLoops.size() > 1) {
    vector<SgForStatement *>::iterator iter = consecutiveLoops.begin();
    iter++; // First loop is already removed by addLoopFuncCall()
    for (; iter != consecutiveLoops.end(); iter++) {
      SageInterface::replaceStatement((*iter),
                                      SageBuilder::buildNullStatement(), false);
    }
  }

  loop_file_buf.close();

  /* Remove preprocessor text, since ROSE preprocessor has already worked */
  /*	string sed_command;
    sed_command = "sed -i '/^#if/ d' " + loop_file_name;
          executeCommand( sed_command );
    sed_command = "sed -i '/^#else/ d' " + loop_file_name;
          executeCommand( sed_command );
    sed_command = "sed -i '/^#endif/ d' " + loop_file_name;
          executeCommand( sed_command );*/
  /* Change struct access with pointer to struct */
  //	for( auto const &str : curr_loop.scope_struct_str_vec ){
  //		/* change struct access: 'st =' to '(*st) =' */
  //		string sed_command1 = "sed -i 's/" + str + " =/(*" + str + ")
  //=/g'
  //";
  //		executeCommand(sed_command1 + loop_file_name );
  //		/* change struct access: st.member to st->member */
  //		string sed_command2 = "sed -i 's/" + str + " \\./" + str + "
  //->/g'
  //";
  //		executeCommand(sed_command2 + loop_file_name );
  //	}
  /* TODO: Call astyleFormatter here in distant future */
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
    // cout << "Statement: " <<
    // SageInterface::getNextStatement(loop)->class_name()
    //     << endl <<
    //     SageInterface::getNextStatement(loop)->unparseToCompleteString() <<
    //     endl;
    return;
  }
  return;
}

void Extractor::extractFunctions(SgNode *astNode) {}

/* Required for Top Down parsing */
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
      // cerr << "Found node: " << loop->class_name() << " with depth: " <<
      // inh_attr.loop_nest_depth_ << endl;
      // TODO: Upto what loop depth to extract as tool option
      if (inh_attr.loop_nest_depth_ < 2) {
        // cerr << "Extracting loop now" << endl;
        // if( SageInterface::getNextStatement(loop)->variantT() != NULL &&
        // SageInterface::getNextStatement(loop)->variantT() == V_SgForStatement
        // )
        if (!skipLoop(astNode)) {
          if (LoopExtractor_enabled_options[EXTRACTKERNEL])
            collectAdjoiningLoops(dynamic_cast<SgStatement *>(astNode));
          else
            consecutiveLoops.push_back(dynamic_cast<SgForStatement *>(astNode));
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

      /* Inline function are copied to be put in loops files where neccesary
         Function body is present only here through function declaration. */
      if (declModf.isInline()) {
        string inline_func_str = declFunc->unparseToString() + '\n';
        inline_func_map.insert(
            pair<SgFunctionDeclaration *, string>(declFunc, inline_func_str));
      }

      if (SageInterface::isExtern(declFunc)) {
        header_vec.push_back(declFunc->unparseToString() + '\n');
      }

      if (SageInterface::isMain(astNode)) {
        mainFuncPresent = true;
        main_scope      = dynamic_cast<SgScopeStatement *>(
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
        static_funcs_vec.push_back(funcDef->get_declaration()->get_name());
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
        string pragmaString  = pragmaNode->get_pragma();
        if (pragmaString.find("parallel") == string::npos &&
            pragmaString.find("threadprivate") != string::npos) {
          global_vars.push_back("#pragma " + pragmaString);
          //          } else if( pragmaString.find("parallel") != string::npos
          //          &&
          //                     pragmaString.find("for") == string::npos ){
          //            /* Do nothing since it should be covered in a base file
          //            or inside the body of loop */
        } else if (pragmaString.find("for") != string::npos) {
          /* Should only be concerned with 'for' directive,
           * every other directive remains where they are.
           * i.e. either in base file or inside the loop */
          loopOMPpragma = "#pragma " + pragmaString;
        }
      }
      if (SageInterface::extractPragmaKeyword(pragmaDecl) == "LE") {
        SgPragma *pragmaNode = pragmaDecl->get_pragma();
        string pragmaString  = pragmaNode->get_pragma();
        loopSkipPragma       = "#pragma " + pragmaString;
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
               getAstNodeLineNum(astNode)) == typedef_struct_lineno_vec.end()) {
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
         * since control flow get here after the node was pushed already */
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
              PreprocessingInfo::directiveTypeName((*i)->getTypeOfDirective())
                  .c_str();
          string headerName = (*i)->getString().c_str();
          // cerr << "Header Type: " << directiveTypeName << endl;
          // #include
          if (directiveTypeName == "CpreprocessorIncludeDeclaration" &&
              find(header_vec.begin(), header_vec.end(), headerName) ==
                  header_vec.end()) {
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
              find(header_vec.begin(), header_vec.end(), headerName) ==
                  header_vec.end()) {
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
          string var_type_str  = variableType->unparseToString();
          // Now check if this is a global variable or an static class member
          SgScopeStatement *scope = variableDeclaration->get_scope();
          if (isSgGlobal(scope) != NULL) {
            string var_str = initializedName->get_name().getString();
            // cerr << "Found a global var: " << var_type_str + " " + var_str <<
            // endl;
            if (variableType->variantT() == V_SgArrayType) {
              /* To change to var_type var_name[][][] */
              int first_square_brac = var_type_str.find_first_of("[");
              if (first_square_brac != string::npos)
                global_vars.push_back(
                    var_type_str.substr(0, first_square_brac) + var_str +
                    var_type_str.substr(first_square_brac));
            } else {
              /* Bcoz Rose add wierd stuff like __PRETTY_FUNCTION__ on assert()
               * calls */
              if (var_str.find(ignorePrettyFunctionCall1) == string::npos &&
                  var_str.find(ignorePrettyFunctionCall2) == string::npos &&
                  var_str.find(ignorePrettyFunctionCall3) == string::npos)
                global_vars.push_back(var_type_str + " " + var_str);
            }
            // lastIncludeStmt = dynamic_cast<SgStatement *>(astNode);
          }
          if (isSgClassDefinition(scope) != NULL) {
            // Now check if it is a static data member
            if (variableDeclaration->get_declarationModifier()
                    .get_storageModifier()
                    .isStatic() == true) {
              // cerr << "Found a static global var: " << var_type_str + " " +
              // initializedName->get_name().getString() << endl;
              global_vars.push_back(var_type_str + " " +
                                    initializedName->get_name().getString());
              // lastIncludeStmt = dynamic_cast<SgStatement *>(astNode);
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
   * Due to bug in rosem insert After on include statement skip the next subtree
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

void Extractor::inlineFunctions(const vector<string> &argv) {
  bool frontendConstantFolding = true;
  SgProject *project           = new SgProject(argv);
  ConstantFolding::constantFoldingOptimization(project);
  AstTests::runAllTests(project);
  bool modifiedAST = true;
  int count        = 0;
  do {
    modifiedAST = false;
    Rose_STL_Container<SgNode *> functionCallList =
        NodeQuery::querySubTree(project, V_SgFunctionCallExp);
    // Loop over all function calls
    Rose_STL_Container<SgNode *>::iterator i = functionCallList.begin();
    while (modifiedAST == false && i != functionCallList.end()) {
      SgFunctionCallExp *functionCall = isSgFunctionCallExp(*i);
      ROSE_ASSERT(functionCall != NULL);
      // Not all function calls can be inlined in C, so report if successful.
      bool sucessfullyInlined = doInline(functionCall);
      if (sucessfullyInlined == true) {
        // As soon as the AST is modified recompute the list of function
        // calls (and restart the iterations over the modified list)
        modifiedAST = true;
        cout << "Function inlined" << endl;
      } else {
        modifiedAST = false;
      }
      // Increment the list iterator
      i++;
    }
    // Quite when we have ceased to do any inline transformations
    // and only do a predefined number of inline transformations
    count++;
  } while (modifiedAST == true && count < 10);
  // Adding check for isTransformed flag consistancy.
  cout << "AST check 1" << endl;
  checkTransformedFlagsVisitor(project);
  // Call function to postprocess the AST and fixup symbol tables
  cout << "AST check 2" << endl;
  // FixSgProject(*project);
  // Rename each variable declaration
  cout << "AST check 3" << endl;
  renameVariables(project);
  // Fold up blocks
  cout << "AST check 4" << endl;
  flattenBlocks(project);
  // Adding check for isTransformed flag consistancy.
  cout << "AST check 5" << endl;
  checkTransformedFlagsVisitor(project);
  // Clean up inliner-generated code
  cout << "AST check 6" << endl;
  cleanupInlinedCode(project);
  // Adding check for isTransformed flag consistancy.
  cout << "AST check 7" << endl;
  checkTransformedFlagsVisitor(project);
  // Change members to public
  cout << "AST check 8" << endl;
  changeAllMembersToPublic(project);
  // Adding check for isTransformed flag consistancy.
  cout << "AST check 9" << endl;
  checkTransformedFlagsVisitor(project);
  backend(project);
}

/* Extractor constructor, for initiating via driver */
Extractor::Extractor(const vector<string> &argv) {
  /* Get relative path unique code */
  if (LoopExtractor_input_file_relpathcode.find(argv.back()) !=
          LoopExtractor_input_file_relpathcode.end() &&
      !(LoopExtractor_input_file_relpathcode.find(argv.back())->second).empty())
    relpathcode =
        LoopExtractor_input_file_relpathcode.find(argv.back())->second;

  if (LoopExtractor_enabled_options[STATICANALYSIS]) {
    // inlineFunctions(argv); // Has bugs bcoz of rose implementation
  }

  SgProject *ast = NULL;
  /* Create AST and pass to the extraction functions */
  ast = frontend(argv);
  ROSE_ASSERT(ast != NULL);
  InheritedAttribute inhr_attr;
  /* Traverse all files and their ASTs in Top Down fashion (Inherited Attr) and
   * extract loops */
  this->traverseInputFiles(ast, inhr_attr);
  // this->generateHeaderFile();
  this->addPostTraversalDefs();
  AstTests::runAllTests(ast);
  /* Generate rose_<orig file name> file for the transformed AST */
  ast->unparse();
  delete ast;

  /* If file doesn't have any loop, then LoopExtractor_file_name,_file_extn
   * would be empty at this point */
  if (LoopExtractor_file_name.empty()) {
    LoopExtractor_file_path          = getFilePath(argv.back());
    LoopExtractor_original_file_name = getOrigFileName(argv.back());
    LoopExtractor_file_extn          = getFileExtn(argv.back());
  }
  string base_file = getDataFolderPath() + getOrigFileName() + base_str + "_" +
                     relpathcode + "." + getFileExtn();

  if (LoopExtractor_file_name.empty() && !mainFuncPresent) {
    /* Copy original file to the LoopExtractor data folder:
     * cp filename.x LoopExtractor_data/filename_base.x
     * rm rose_filename.x
     */
    executeCommand("cp " + argv.back() + space_str + base_file);
    executeCommand("rm rose_" + getOrigFileName() + "." + getFileExtn());
  } else {
    /* Move base file to the LoopExtractor data folder:
     * mv rose_filename.x LoopExtractor_data/filename_base.x
     */
    executeCommand("mv rose_" + getOrigFileName() + "." + getFileExtn() +
                   space_str + base_file);
  }
  // modifyExtractedFileText(base_file);

  files_to_compile.insert(base_file);
}
