#ifndef COMMON_H_
#define COMMON_H_

#ifdef OS_CENTOS
#include <boost/preprocessor/stringize.hpp>
#endif
#include <cctype>
#include <cstdio>
#include <ctime>
#include <dirent.h>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <regex>
#include <set>
#include <string>
#include <utility>
#include <vector>

// For Extractor especially
// clang-format off
#include "rose.h"
#include "ASTtools.hh"
#include "constantFolding.h"
// clang-format on

using namespace std;

typedef enum {
    src_lang_C = 0,
    src_lang_CPP = 1,
    src_lang_FORTRAN = 2,
} src_lang;

typedef enum {
    INVITRO,
    INSITU,
    INVIVO
} LoopExtractorMode;

typedef enum {
    EXTRACT,
    PARALLEL,
    EXTRACTKERNEL,
    RESTRICT,
    STATICANALYSIS,
    OUTPUT_OBJECT,
    C99,
    INCLUDE_PATH,
    MACRO_DEFS,
    INFO,
    HELP,
    WORKDIR,
    MODE,
    SRC_PREFIX,
    UNKNOWN
} LoopExtractor_options;

enum class ParamPassingStyle {
    POINTER, REFERENCE, DIRECT
};

/* For the tracer */
std::string parseFileName(const std::string *fullName);

extern string space_str;
extern string forward_slash_str;
extern string minus_c_str;
extern string minus_o_str;
extern string dot_o_str;
extern string base_str;
extern string LoopExtractor_skiplooppragma_str;

extern string LoopExtractor_unique_str;

extern string LoopExtractor_work_folder;
extern string LoopExtractor_data_folder;
extern string LoopExtractor_data_folder_path;
extern string LoopExtractor_curr_dir_path;
extern string LoopExtractor_extract_src_info_csv;
extern string LoopExtractor_src_prefix;
extern LoopExtractorMode LoopExtractor_mode;

/* For the extractor */
extern vector<string> LoopExtractor_input_file;
extern map<string, string> LoopExtractor_input_file_relpathcode;
extern set<string> files_to_compile;

extern string LoopExtractor_macro_defs;
extern string LoopExtractor_include_path;
extern string LoopExtractor_extraPreSrcFlags;
extern string LoopExtractor_extraPostSrcFlags;

extern map<LoopExtractor_options, bool> LoopExtractor_enabled_options;

string executeCommand(string cmd_str);
bool isDirExist(const string &path);
bool isFileExist(const string &filename);
bool isFileRecent(const string &filename);
bool isEndingWith(string const &fullString, string const &ending);
double getVectorMean(vector<double> *dataVec);
double getVectorStdev(vector<double> *dataVec);
double getVectorMedian(vector<double> *dataVec);
void genRandomStr(string &str, const int len);
void stringReplaceAll(string &str, const string &from, const string &to);
string getAbsolutePath(string const &fullString);
ParamPassingStyle getPassingStyle(SgType* arg_type, src_lang lang);
bool isAnonymousName(const SgName& name);
SgStatement* get_loop_body(SgScopeStatement* loop) ;
#endif
