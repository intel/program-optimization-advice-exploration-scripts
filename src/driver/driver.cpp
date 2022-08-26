#include "driver.h"

/* Create data folder in /tmp */
void Driver::createLoopExtractorDataFolder() {
  LoopExtractor_data_folder_path =
      "/tmp/" + LoopExtractor_data_folder + forward_slash_str;
  if (!isDirExist(LoopExtractor_data_folder_path)) {
    const int dir_err = mkdir(LoopExtractor_data_folder_path.c_str(),
                              S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
    if (dir_err == -1) {
      cout << "Error creating LoopExtractor data directory:"
           << LoopExtractor_data_folder_path << endl;
      exit(EXIT_FAILURE);
    }
  }
}

void Driver::removeLoopExtractorDataFolder() {
  string CL = "rm -rf ";
  CL += LoopExtractor_data_folder_path;
  executeCommand(CL);
}

void Driver::moveLoopExtractorDataFolder() {
  string CL = "mv ";
  CL +=
      LoopExtractor_data_folder_path + space_str + LoopExtractor_curr_dir_path;
  string result = executeCommand(CL);
  if (result.find("failed") != string::npos) {
    CL = "cp -a ";
    CL += LoopExtractor_data_folder_path + forward_slash_str + "." + space_str +
          LoopExtractor_curr_dir_path + forward_slash_str +
          LoopExtractor_data_folder;
    string result = executeCommand(CL);
  }
}

void Driver::copyInFolderHeaders(string folder_path, bool copysourcefiles) {
  string cmd_str = "cp " + folder_path + "*.h " + getDataFolderPath();
  executeCommand(cmd_str);
  cmd_str = "cp " + folder_path + "*.inc " + getDataFolderPath();
  executeCommand(cmd_str);
  if (copysourcefiles) {
    string cmd_str = "cp " + folder_path + "*.c " + getDataFolderPath();
    executeCommand(cmd_str);
  }
}

/* file_name is the relative path to the file to be extracted */
void Driver::initiateExtractor(string file_name) {
  if (FILE *file = fopen(file_name.c_str(), "r")) {
    fclose(file);
  } else {
    cerr << "The input file doesn't exist: " << file_name << endl;
    exit(EXIT_FAILURE);
  }
  vector<string> filename_vec;
  string dummy_arg_for_extractor_frontend =
      "Rose, please let me run the extractor!";
  filename_vec.push_back(dummy_arg_for_extractor_frontend);
#ifdef OS_CENTOS
  dummy_arg_for_extractor_frontend =
      "-I" + rose_path + "include/edg/gcc_HEADERS/";
  filename_vec.push_back(dummy_arg_for_extractor_frontend);
#endif
  /* Rose frontend needs each include path in different vector entry */
  istringstream bufI(LoopExtractor_include_path);
  istream_iterator<string> begI(bufI), endI;
  vector<string> tokensI(begI, endI);
  for (auto &sI : tokensI)
    filename_vec.push_back(sI);

  /* Rose frontend needs each Macro definition in different vector entry */
  if (LoopExtractor_enabled_options[PARALLEL])
    filename_vec.push_back("-D_OPENMP");
  istringstream bufM(LoopExtractor_macro_defs);
  istream_iterator<string> begM(bufM), endM;
  vector<string> tokensM(begM, endM);
  for (auto &sM : tokensM)
    filename_vec.push_back(sM);

  filename_vec.push_back(file_name);

    tr = new Tracer();
  extr = new Extractor(filename_vec, tr);
  tr->setFilenameVec(filename_vec);

  mainFuncPresent = extr->mainFuncPresent;
  src_type        = extr->getSrcType();

  /* Keep on collection Loop Functions name - Append two vector */
  loop_funcName_vec->insert(loop_funcName_vec->end(),
                            (extr->loop_funcName_vec)->begin(),
                            (extr->loop_funcName_vec)->end());

  /* Copy headers that are in same folder as Source to LE data folder */
  copyInFolderHeaders(extr->getFilePath(), extr->copysourcefiles);
}


void Driver::generateCodelets() {
    tr->initTracing();
}


int main(int argc, char *argv[]) {
  Driver *driver = new Driver();
  set_LoopExtractor_options(argc, argv);

  /* Get current working directory path */
  LoopExtractor_curr_dir_path = getAbsolutePath(".") + forward_slash_str;
  driver->createLoopExtractorDataFolder();

  genRandomStr(LoopExtractor_unique_str, 5);

  /* Send all files in the command line for extraction */
  if (LoopExtractor_enabled_options[EXTRACT]) {
    vector<string>::iterator iter;
    for (iter = LoopExtractor_input_file.begin();
         iter != LoopExtractor_input_file.end(); iter++) {
      if (*iter == LoopExtractor_input_file.back()) {
        driver->isLastSrcFile = true;
      }
      driver->initiateExtractor(*iter);

      //driver->generateCodelet();

    }
  }

  driver->moveLoopExtractorDataFolder();

    cout << "In-Situ extraction completed" << endl;

    driver->generateCodelets();
  //tr->"initTracing();


    cout << "In-Vitro extraction completed" << endl;

  delete driver;
  return 0;
}
