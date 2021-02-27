#ifndef DRIVER_H_
#define DRIVER_H_

#include "common.h"
#include "extractor/extractor.h"
#include "options.h"

using namespace std;

class Driver {
  string compiler_flags;
  vector<string> *loop_funcName_vec = new vector<string>;
  ofstream header_file_buf;
  ofstream header_code_file_buf;
  src_lang src_type;

  Extractor *extr;

public:
  bool mainFuncPresent = false;
  bool isLastSrcFile   = false;

public:
  Driver(){};
  src_lang getSrcType() { return src_type; }
  string getDataFolderPath() { return LoopExtractor_data_folder_path; };
  void createLoopExtractorDataFolder();
  void removeLoopExtractorDataFolder();
  void moveLoopExtractorDataFolder();
  void copyInFolderHeaders(string folder_path, bool copysourcefiles);
  void initiateExtractor(string file_name);
};

#endif
