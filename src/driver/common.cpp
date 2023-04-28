#include "common.h"

map<LoopExtractor_options, bool> LoopExtractor_enabled_options;

string space_str = " ";
string forward_slash_str = "/";
string minus_c_str = "-c";
string minus_o_str = "-o";
string dot_o_str = ".o";
string base_str = "_base";
string LoopExtractor_skiplooppragma_str = "skiploop";

/* Each run of LoopExtractor will have a unique str associated to it */
string LoopExtractor_unique_str = "";

string LoopExtractor_work_folder = "/tmp";
string LoopExtractor_data_folder = "LoopExtractor_data";
string LoopExtractor_data_folder_path;
string LoopExtractor_curr_dir_path;
string LoopExtractor_extract_src_info_csv = "tmpLoop.csv";
string LoopExtractor_src_prefix = "";
LoopExtractorMode LoopExtractor_mode = INVITRO;

/*** Parameter that change based on the CL input ***/
/* For the extractor */
vector<string> LoopExtractor_input_file;
map<string, string> LoopExtractor_input_file_relpathcode;
set<string> files_to_compile;

string LoopExtractor_macro_defs = "";
string LoopExtractor_include_path = "";
string LoopExtractor_extraPreSrcFlags = "";
string LoopExtractor_extraPostSrcFlags = "";

/*** END: Parameter that change based on the CL input ***/

string executeCommand(string cmd_str) {
    // Since, pipe doesn't capture stderr, redirect it to stdout
    cmd_str = cmd_str + " 2>&1";
    const char *cmd_char_ptr = cmd_str.c_str();
    array<char, 128> buffer;
    string result;
    if (LoopExtractor_enabled_options[INFO])
        cout << "Executing command:" << endl << cmd_str << endl;
    shared_ptr<FILE> pipe(popen(cmd_char_ptr, "r"), pclose);

    if (!pipe)
        throw runtime_error("popen() while executing command failed!");

    while (!feof(pipe.get())) {
        if (fgets(buffer.data(), 128, pipe.get()) != NULL)
            result += buffer.data();
    }
    if (LoopExtractor_enabled_options[INFO]) {
        if (!result.empty()) {
            cout << "Result of the previous command:" << endl << result << endl;
            // if( result.find("error") == string::npos )
            //	exit(EXIT_FAILURE);
        }
    }
    return result;
}

bool isDirExist(const string &path) {
    struct stat info;
    if (stat(path.c_str(), &info) != 0)
        return false;
    else if (info.st_mode & S_IFDIR)
        return true;
    else
        return false;
}

bool isFileExist(const string &filename) {
    struct stat info;
    return (stat(filename.c_str(), &info) == 0);
}

bool isFileRecent(const string &filename) {
    struct stat info;
    if (stat(filename.c_str(), &info) == 0) {
        auto mtime = info.st_mtime;
        /* Check if file was modified before 5 seconds */
        if (time(0) - info.st_mtime > 5)
            return false;
        return true;
    }
    return false;
}

bool isEndingWith(string const &fullString, string const &ending) {
    if (fullString.length() >= ending.length())
        return (fullString.compare(fullString.length() - ending.length(),
                                   ending.length(), ending) == 0);
    else
        return false;
}

double getVectorMean(vector<double> *dataVec) {
    double sum = accumulate(dataVec->begin(), dataVec->end(), 0.0);
    double mean = sum / dataVec->size();
    return mean;
}

double getVectorStdev(vector<double> *dataVec) {
    double mean = getVectorMean(dataVec);
    vector<double> diff(dataVec->size());
    transform(dataVec->begin(), dataVec->end(), diff.begin(),
              [mean](double x) { return x - mean; });
    double sq_sum = inner_product(diff.begin(), diff.end(), diff.begin(), 0.0);
    double stdev = sqrt(sq_sum / dataVec->size());
    return stdev;
}

double getVectorMedian(vector<double> *dataVec) {
    sort(dataVec->begin(), dataVec->end());
    if (dataVec->size() % 2 == 0) {
        return (dataVec->at((dataVec->size() / 2) - 1) +
                dataVec->at(dataVec->size() / 2)) /
               2.0;
    }
    return dataVec->at(dataVec->size() / 2);
}

void genRandomStr(string &str, const int len) {
    static const char alphanum[] = "0123456789"
                                   "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                   "abcdefghijklmnopqrstuvwxyz";

    for (int i = 0; i < len; ++i) {
        str += alphanum[rand() % (sizeof(alphanum) - 1)];
    }
}

void stringReplaceAll(string &str, const string &from, const string &to) {
    size_t start_pos = 0;
    while ((start_pos = str.find(from, start_pos)) != string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos +=
            to.length(); // Handles case where 'to' is a substring of 'from'
    }
}

string getAbsolutePath(string const &fullString) {
    string result = executeCommand("realpath " + fullString);
    // To remove \n at the end
    result.pop_back();
    if (result.find("No such file or directory") == string::npos) {
        return result;
    } else {
        cerr << "Driver: Incorrect Path -> " << fullString << endl;
        exit(EXIT_FAILURE);
    }
}

std::string parseFileName(std::string *fullName) {
    if (fullName != nullptr) {
        std::string::size_type prev_pos = 0, pos = 0;
        std::string separator = "/";
        while ((pos = (*fullName).find(separator, pos)) != std::string::npos) {
            std::string substring((*fullName).substr(prev_pos, pos - prev_pos));
            prev_pos = ++pos;
        }
        std::string substring((*fullName).substr(prev_pos, pos - prev_pos));
        return substring;
    }
    return "";
}

ParamPassingStyle getPassingStyle(SgType* arg_type, src_lang lang) {
    if (lang == src_lang_C) {
        // 'Address Of' for C except when its an array
        bool isTypedefArray = false;
        bool isTypedefStruct = false;
        if (arg_type->variantT() == V_SgTypedefType) {
            SgTypedefType *type_def_var =
                dynamic_cast<SgTypedefType *>(arg_type);
            if ((type_def_var->get_base_type())->variantT() ==
                V_SgArrayType)
                isTypedefArray = true;
            else if (SageInterface::isStructType(
                        type_def_var->get_base_type()))
                isTypedefStruct = true;
        }

        if (arg_type->variantT() == V_SgArrayType ||
            isTypedefArray) {
            return ParamPassingStyle::DIRECT;
        } else if (arg_type->variantT() == V_SgPointerType) {
            SgType *var_pointer_type = arg_type->stripType(1 << 2);
            if (var_pointer_type->variantT() == V_SgTypedefType) {
                SgTypedefType *type_def_var =
                    dynamic_cast<SgTypedefType *>(var_pointer_type);
                var_pointer_type = type_def_var->get_base_type();
            }
            if (SageInterface::isStructType(var_pointer_type)) {
                return ParamPassingStyle::POINTER;
            } else {
                return ParamPassingStyle::DIRECT;
            }
        } else { // typedef struct handled here
            return ParamPassingStyle::POINTER;
        }
    } else if (lang == src_lang_CPP) {
        // Reference for C++
        return ParamPassingStyle::REFERENCE;
    }
    return ParamPassingStyle::DIRECT;
}