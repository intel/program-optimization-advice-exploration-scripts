export const INITIAL_FILTERS = {
    'Loops': {
        "Vectorization Ratio (%)": {
            'accessor': 'vectorization_ratio',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "Vectorization Length Use (%)": {
            'accessor': 'vectorization_efficiency',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
    },
    'Global': {
        "Total Time (s)": {
            'accessor': 'total_time',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "Profiled Time (s)": {
            'accessor': 'profiled_time',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "Array Access Efficiency (%)": {
            'accessor': 'array_access_efficiency',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "Model Name": {
            'accessor': 'model_name',
            'selected': false,
            'operator': 'like',
            'mode': 'all',
            'value': ''
        },
        "Number of Cores": {
            'accessor': 'number_of_cores',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "No Scalar Integer Potential Speedup": {
            'accessor': 'speedup_if_clean',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "FP Vectorised Potential Speedup": {
            'accessor': 'speedup_if_fp_vect',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "Fully Vectorised Potential Speedup": {
            'accessor': 'speedup_if_fully_vectorised',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
        "FP Arithmetic Potential Speedup": {
            'accessor': 'speedup_if_FP_only',
            'selected': false,
            'operator': 'less than',
            'mode': 'all',
            'value': ''
        },
    }
};
