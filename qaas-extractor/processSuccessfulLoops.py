import os
import pandas as pd

def process_successful_loops(extracted_codelets_dir, successful_loops):
    all_cycles_df = pd.DataFrame(columns = ['Loop', 'Cycles'])
    cycles_dicts = []
    for successfull_loop in successful_loops: 
        try:
            successfull_loop_path = os.path.join(extracted_codelets_dir, successfull_loop)
            cycle_csv = os.path.join(successfull_loop_path, 'cycles.csv')
            cycles_df = pd.read_csv(cycle_csv, skipinitialspace=True)
            median_cycles = cycles_df['cycles'].median()
            cycles_dicts.append({'Loop': successfull_loop, 'Cycles': median_cycles})
        except:
            pass
    all_cycles_df = pd.DataFrame.from_records(cycles_dicts)
    return all_cycles_df

def main():
    successful_loops = ['IJMatrix_parcsr_hypre_IJMatrixSetDiagOffdSizesParCSR_line199_miniapps_AMG_AMG_IJ_mv', 'IJMatrix_parcsr_hypre_IJMatrixSetDiagOffdSizesParCSR_line207_miniapps_AMG_AMG_IJ_mv', 'IJMatrix_parcsr_hypre_IJMatrixInitializeParCSR_line304_miniapps_AMG_AMG_IJ_mv', 'IJVector_parcsr_hypre_IJVectorSetValuesPar_line442_miniapps_AMG_AMG_IJ_mv', 'csr_matrix_hypre_CSRMatrixSetRownnz_line145_miniapps_AMG_AMG_seq_mv', 'amg_main_line317_miniapps_AMG_AMG_test', 'amg_BuildIJLaplacian27pt_line794_miniapps_AMG_AMG_test']
    extracted_codelets_dir = '/host/localdisk/cwong29/working/codelet_extractor_work/miniapps/extractor_work/amg/169-757-6568/replay_data/run'
    successful_loops = ['deblock_deblock_luma_c_line113_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'mc_pixel_avg_weight_wxh_line70_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'mc_mc_weight_line132_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'mc_mc_copy_line174_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'mc_hpel_filter_line187_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'mc_mc_chroma_line280_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'mc_frame_init_lowres_core_line385_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'pixel_x264_pixel_sad_16x16_line61_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'pixel_x264_pixel_var_16x16_line159_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'quant_quant_8x8_line48_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'quant_x264_decimate_score_internal_line181_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'quant_x264_decimate_score_internal_line193_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_common', 'me_x264_me_search_ref_line220_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_encoder', 'me_refine_subpel_line836_SPEC2017_benchmark_benchspec_CPU_525_x264_r_src_x264_src_encoder']
    extracted_codelets_dir = '/host/localdisk/cwong29/working/codelet_extractor_work/SPEC2017/extractor_work/525.x264_r/169-774-8956/replay_data/run'

    process_successful_loops(extracted_codelets_dir, successful_loops)


if __name__ == "__main__":
    main()