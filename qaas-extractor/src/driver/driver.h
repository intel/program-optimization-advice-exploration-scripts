#ifndef DRIVER_H_
#define DRIVER_H_

#include "common.h"
#include "extractor/extractor.h"
#include "options.h"
//#include "tracer/tracer.h"

using namespace std;

class Driver {
    string compiler_flags;
    vector<string> loop_funcName_vec ;
    //ofstream header_file_buf;
    //ofstream header_code_file_buf;
    src_lang src_type;

    // vector<string> filename_vec;
    Extractor *extr;
    // Tracer *tr;

public:
    bool mainFuncPresent = false;
    bool isLastSrcFile = false;

    vector<LoopInfo> loop_info_vec;

public:
    Driver() : extr(NULL) { };
    src_lang getSrcType() { return src_type; }
    string getDataFolderPath() { return LoopExtractor_data_folder_path; };
    void createLoopExtractorDataFolder();
    void removeLoopExtractorDataFolder();
    void moveLoopExtractorDataFolder();
    void copyInFolderHeaders(string folder_path, bool copysourcefiles);
    void initiateExtractor(string file_name);
    // void generateCodelets();
    // void dumpExtrLoopInfo();
    void scanLineNumbers(string loopFileName);
    void scanOneLine(const string& line, string& filename, int& firstLine, int& lastLine);
};

#endif
