export const RANGES = ['0-0.33', '0.33-0.5', '0.5-0.85', '0.85-1.0', '1.0-1.15', '1.15-2', '2-3', '3-4', '>4'];
export const DEFAULT_COLOR_SCHEME = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F', '#B276B2', '#DECF3F', '#F15854'];
export const TABLE_COLOR_SCHEME = ['#FFF5E1', '#FFB6C1', '#E8F5E9', '#E1F5FE']
export const TOGGLE_BUTTON_COLOR_SCHEME = ['#FFDA8D', '#FFA6B9', '#B0E57C', '#AEDFF7']

export const formatNumber = value => {
    if (value === "Not Available") return value;
    const num = parseFloat(value);
    return isNaN(num) ? value : num.toExponential(2);
};
export const APPLICATION_TABLE_COLUMNS = [
    { Header: 'Workload', accessor: 'workload', id: 'workload' },
    { Header: 'Program', accessor: 'program', id: 'program' },
    { Header: 'Experiment Name', accessor: 'experiment_name', id: 'experiment_name' },
    { Header: 'Commit ID', accessor: 'commit_id', id: 'commit_id', width: 80 },
    {
        groupName: 'time',
        Header: 'Time',
        className: 'time-background',
        columns: [
            { Header: 'Total Time(s)', accessor: d => formatNumber(d.total_time), id: 'total_time' },
            { Header: 'Profiled Time(s)', accessor: d => formatNumber(d.profiled_time), id: 'profiled_time', },
            { Header: 'Time in analyzed loops (%)', accessor: d => formatNumber(d.time_in_analyzed_loops), id: 'time_in_analyzed_loops', },
            { Header: 'Time in user code (%)', accessor: d => formatNumber(d.time_in_user_code), id: 'time_in_user_code', }
        ]
    },
    {
        groupName: 'globalScore',
        Header: 'Global Score',

        columns: [
            { Header: 'Compilation Options Score (%)', accessor: d => formatNumber(d.compilation_options_score), id: 'compilation_options_score', },
            { Header: 'Array Access Efficiency (%)', accessor: d => formatNumber(d.array_access_efficiency), id: 'array_access_efficiency', }
        ]
    },
    {
        groupName: 'speedup',
        Header: 'Speedup',

        columns: [
            { Header: 'Perfect Flow Complexity', accessor: d => formatNumber(d.perfect_flow_complexity), id: 'perfect_flow_complexity', },
            { Header: 'Iterations Count', accessor: d => formatNumber(d.iterations_count), id: 'iterations_count', },
            { Header: 'Perfect OpenMP + MPI + Pthread', accessor: d => formatNumber(d.perfect_openmp_mpi_pthread), id: 'perfect_openmp_mpi_pthread', },
            { Header: 'Perfect OpenMP + MPI + Pthread + Perfect Load Distribution', accessor: d => formatNumber(d.perfect_openmp_mpi_pthread_load_distribution), id: 'perfect_openmp_mpi_pthread_load_distribution', },
            { Header: 'No Scalar Integer Potential Speedup', accessor: d => formatNumber(d.speedup_if_clean), id: 'speedup_if_clean', },
            { Header: 'FP Vectorised Potential Speedup', accessor: d => formatNumber(d.speedup_if_fp_vect), id: 'speedup_if_fp_vect', },
            { Header: 'Fully Vectorised Potential Speedup', accessor: d => formatNumber(d.speedup_if_fully_vectorised), id: 'speedup_if_fully_vectorised', },
            { Header: 'FP Arithmetic Only Potential Speedup', accessor: d => formatNumber(d.speedup_if_FP_only), id: 'speedup_if_FP_only', }
        ]
    },
    {
        groupName: 'experimentSummary',
        Header: 'Experiment Summary',

        columns: [
            { Header: 'Compilation Options', accessor: 'compilation_flags', id: 'compilation_flags', },
            { Header: '-O2/O3', accessor: 'o2_o3', id: 'o2_o3', width: 50 },
            { Header: 'ICL/HSW', accessor: 'icl_hsw', id: 'icl_hsw', width: 50 },
            { Header: 'FLTO', accessor: 'flto', id: 'flto', width: 50 },
            { Header: 'fno-tree-vectorize', accessor: 'fno_tree_vec', id: 'fno_tree_vec', width: 50 },
            { Header: 'Model Name', accessor: 'model_name', id: 'model_name' },
            { Header: 'Number of Cores', accessor: d => formatNumber(d.number_of_cores), id: 'number_of_cores', }
        ]
    },

];