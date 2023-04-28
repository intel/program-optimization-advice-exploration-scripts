#ifndef OPTIONS_H
#define OPTIONS_H

#include "common.h"
#include "optionparser.h"

struct Arg : public option::Arg {
  static void printError(const char *msg1, const option::Option &opt,
                         const char *msg2) {
    fprintf(stderr, "%s", msg1);
    fwrite(opt.name, opt.namelen, 1, stderr);
    fprintf(stderr, "%s", msg2);
  }
  static option::ArgStatus Unknown(const option::Option &option, bool msg) {
    if (msg)
      printError("Unknown option '", option, "'\n");
    return option::ARG_ILLEGAL;
  }
  static option::ArgStatus Required(const option::Option &option, bool msg) {
    if (option.arg != 0)
      return option::ARG_OK;
    if (msg)
      printError("Option '", option, "' requires an argument\n");
    return option::ARG_ILLEGAL;
  }
  static option::ArgStatus Numeric(const option::Option &option, bool msg) {
    char *endptr = 0;
    if (option.arg != 0 && strtol(option.arg, &endptr, 10)) {
    };
    if (endptr != option.arg && *endptr == 0)
      return option::ARG_OK;
    if (msg)
      printError("Option '", option, "' requires a numeric argument\n");
    return option::ARG_ILLEGAL;
  }
};
// clang-format off
const option::Descriptor usage[] = {
  {UNKNOWN            , 0, ""  , ""                ,Arg::None     , "Usage:  LoopExtractor <input_files> [options] [-o output]\nOptions:" },
  {HELP               , 0, "h" , "help"            ,Arg::None     , "    -h,--help                 Print usage" },
  {EXTRACT            , 0, ""  , "noextract"       ,Arg::None     , "    --[no]extract             Extract hotspots" },
  {PARALLEL           , 0, ""  , "parallel"        ,Arg::None     , "    --parallel                Extract hotspots with OpenMP directives\n"
                                                                    "                              Default: Serial code" },
  {EXTRACTKERNEL      , 0, ""  , "extractkernel"   ,Arg::None     , "    --extractkernel           Extract consecutive loop nests, if possible." },
  {RESTRICT           , 0, ""  , "restrict"        ,Arg::None     , "    --restrict                Add restrict keyword." },
  {STATICANALYSIS     , 0, ""  , "static"          ,Arg::None     , "    --static                  Perform static analysis to determine read-only values." },
  {C99                , 0, ""  , "c99"             ,Arg::None     , "    --c99                     Conforms to ISO C99 standards. Default: C11" },
  {INCLUDE_PATH       , 0, "I" , "include"         ,Arg::Required , "    -I[<arg>]                 Directory to include file search path" },
  {MACRO_DEFS         , 0, "D" , "DEFS"            ,Arg::Required , "    -D[<arg>]                 Macro definition" },
  {INFO               , 0, ""  , "info"            ,Arg::None     , "    --info                    Print information for LoopExtractor workflow" },
  {WORKDIR            , 0, ""  , "extractwd"       ,Arg::Required , "    --extractwd[<arg>]        Extractor Work directory" },
  {MODE               , 0, ""  , "extractmode"     ,Arg::Required , "    --extractmode[<arg>]      Extractor Mode" },
  {SRC_PREFIX         , 0, ""  , "extractsrcprefix",Arg::Required , "    --extractsrcprefix[<arg>] Source path prefix to be removed in loop naming" },
  {0, 0, 0, 0, 0, 0}
};

LoopExtractorMode str2mode(const string& input) {
  if (input == "invitro") return INVITRO;
  if (input == "insitu") return INSITU;
  if (input == "invivo") return INVIVO;
  return INVITRO;  // default
}
// clang-format on
void set_LoopExtractor_options(int argc, char *argv[]) {
  LoopExtractor_enabled_options = {
      {EXTRACT, true},   {PARALLEL, false},       {EXTRACTKERNEL, false},
      {RESTRICT, false}, {STATICANALYSIS, false}, {C99, false},
      {INFO, false},
  };
  argc -= (argc > 0);
  argv += (argc > 0); // skip program name argv[0] if present
  option::Stats stats(usage, argc, argv);

#ifdef __GNUC__
  // GCC supports C99 VLAs for C++ with proper constructor calls.
  option::Option options[stats.options_max], buffer[stats.buffer_max];
#else
  option::Option *options =
      (option::Option *)calloc(stats.options_max, sizeof(option::Option));
  option::Option *buffer =
      (option::Option *)calloc(stats.buffer_max, sizeof(option::Option));
#endif

  option::Parser parse(true, usage, argc, argv, options, buffer);

  if (parse.error()) {
    cout << "Invalid command line option" << endl;
    exit(EXIT_FAILURE);
  }

  /* After Help option is printed in case no args or -help flag */
  if (options[HELP] || argc == 0) {
    int columns = getenv("COLUMNS") ? atoi(getenv("COLUMNS")) : 120;
    option::printUsage(fwrite, stdout, usage, columns);
    exit(EXIT_FAILURE);
  }

  bool postSourceFlags = false;
  string tmpstr        = "";

  for (int i = 0; i < parse.optionsCount(); ++i) {
    option::Option &opt = buffer[i];
    switch (opt.index()) {
    case EXTRACT:
      LoopExtractor_enabled_options[EXTRACT] = false;
      break;
    case PARALLEL:
      LoopExtractor_enabled_options[PARALLEL] = true;
      break;
    case EXTRACTKERNEL:
      LoopExtractor_enabled_options[EXTRACTKERNEL] = true;
      break;
    case RESTRICT:
      LoopExtractor_enabled_options[RESTRICT] = true;
      break;
    case STATICANALYSIS:
      LoopExtractor_enabled_options[STATICANALYSIS] = true;
      break;
    case C99:
      LoopExtractor_enabled_options[C99] = true;
      break;
    case INCLUDE_PATH:
      LoopExtractor_include_path += space_str + "-I" +
                                    LoopExtractor_curr_dir_path +
                                    string(opt.arg) + space_str;
      break;
    case MACRO_DEFS:
      LoopExtractor_macro_defs +=
          space_str + "-D" + string(opt.arg) + space_str;
      break;
    case INFO:
      LoopExtractor_enabled_options[INFO] = true;
      break;
    case WORKDIR:
      LoopExtractor_work_folder = string(opt.arg);
      break;
    case SRC_PREFIX:
      LoopExtractor_src_prefix = string(opt.arg);
      break;
    case MODE:
      LoopExtractor_mode = str2mode(string(opt.arg));
      break;
    }
  }

  for (int i = 0; i < parse.nonOptionsCount(); ++i) {
    string str = parse.nonOption(i);
    if (isEndingWith(str, ".c") || isEndingWith(str, ".cc") ||
        isEndingWith(str, ".cpp") || isEndingWith(str, ".C") ||
        isEndingWith(str, ".f") || isEndingWith(str, ".f77") ||
        isEndingWith(str, ".f90") || isEndingWith(str, ".f95")) {
      /* Search for source files in the name */
      LoopExtractor_input_file.push_back(getAbsolutePath(str));
      postSourceFlags = true;

      string srcparentdir = str.substr(0, str.find_last_of("/"));
      if (srcparentdir.compare(str) != 0) { 
        // remove the source prefix if matched
        if (!LoopExtractor_src_prefix.empty() 
          && srcparentdir.rfind(LoopExtractor_src_prefix, 0) == 0) { 
            if(srcparentdir.rfind(LoopExtractor_src_prefix+"/", 0) == 0)
              boost::erase_first(srcparentdir, LoopExtractor_src_prefix+"/");
            else
              boost::erase_first(srcparentdir, LoopExtractor_src_prefix);
        }
        //boost::erase_all(srcparentdir, "/");
        //boost::erase_all(srcparentdir, ".");
        boost::replace_all(srcparentdir, "/", "_");
        boost::replace_all(srcparentdir, ".", "_");
        LoopExtractor_input_file_relpathcode.insert(
            pair<string, string>(getAbsolutePath(str), srcparentdir));
      } else {
        LoopExtractor_input_file_relpathcode.insert(
            pair<string, string>(getAbsolutePath(str), ""));
      }

    } else {
      cout << "Non-option argument: " << str << endl;
      if (postSourceFlags)
        LoopExtractor_extraPostSrcFlags += space_str + str;
      else
        LoopExtractor_extraPreSrcFlags += space_str + str;
    }
  }
}
#endif
