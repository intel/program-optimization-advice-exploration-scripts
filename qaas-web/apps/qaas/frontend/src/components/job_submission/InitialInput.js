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


    runtime: {
        MPI: "no",
        OPENMP: "strong"
    }
}