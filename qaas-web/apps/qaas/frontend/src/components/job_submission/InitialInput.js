export var INITIAL_INPUT = {
    account: {
        QAAS_ACCOUNT: "intel"
    },
    application: {
        APP_NAME: "",
        GIT: {
            USER: "",
            TOKEN: "",
            BRANCH: "",
            SRC_URL: "",
            DATA_USER: "",
            DATA_TOKEN: "",
            DATA_URL: "",
            DATA_BRANCH: "",
            DATA_DOWNLOAD_PATH: ""
        },
        RUN: {
            APP_DATA_ARGS: "",
            APP_RUN_CMD: "<binary>",
            APP_ENV_MAP: {},
            APP_SCALABILITY_TYPE: "Strong/Sequential"
        }
    },
    compiler: {
        USER_CC: "icc",
        USER_CC_VERSION: "2022",
        USER_C_FLAGS: "",
        USER_CXX_FLAGS: "",
        USER_FC_FLAGS: "",
        USER_LINK_FLAGS: "",
        USER_TARGET: "",
        USER_TARGET_LOCATION: ""
    },
    library: {
        USER_MPI: "Intel MPI",
        USER_MATH: "Intel MKL"
    },
    system: {
        USER_OPTION: {
            CPU: "",
            HYPERTHREADING: "",
            HUGEPAGE: "",
            TURBO_BOOST: "",
            FREQ_SCALING: "",
            PREFETCH: "",
        },
        SEARCH_OPTIONS: {
            CPU: ["Default"],
            HYPERTHREADING: ["Default"],
            HUGEPAGE: ["Default"],
            TURBO_BOOST: ["Default"],
            FREQ_SCALING: ["Default"],
            PREFETCH: ["Default"],
            COMPILER: ["Default"]
        }

    }
}