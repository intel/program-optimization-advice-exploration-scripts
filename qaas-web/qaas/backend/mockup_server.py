
import pandas as pd

from flask import Flask
from flask_cors import CORS
from flask import jsonify

def calculate_speedup(time_comp, baseline_compiler):
    baseline_time = time_comp.get(baseline_compiler, 0)
    if baseline_time == 0:
        return []

    win_lose_list = []
    for compiler, time in time_comp.items():
        speedup = baseline_time / time
        if speedup < 1:
            converted_speedup = 1 / speedup
            win_lose_list.append({'winner': baseline_compiler, 'loser': compiler, 'speedup': converted_speedup})
    return win_lose_list

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route('/get_qaas_compiler_comparison_historgram_data', methods=['GET'])
    def get_qaas_compiler_comparison_historgram_data():
        df = pd.read_excel('/host/home/yjiao/QaaS_Min_Max_Unicore_Perf_Default.xlsx', header=3)

        # convert columns to numeric, replacing errors with NaN
        df['Best (option) perf. (s)'] = pd.to_numeric(df['Best (option) perf. (s)'], errors='coerce')
        df['ICX: -O3 -march=native'] = pd.to_numeric(df['ICX: -O3 -march=native'], errors='coerce')

  
        
        # List to store unique compilers
        compilers = ['ICX', 'ICC', 'GCC']

        applications = []
        delta = 0.03  # 3% threshold

        #get the execution time back
        df['ICX'] = df['Best (option) perf. (s)'] * df['ICX: -O3 -march=native']
        df['ICC'] = df['Best (option) perf. (s)'] * df['ICC: -O3 -march=native']
        df['GCC'] = df['Best (option) perf. (s)'] * df['GCC: -O3 -march=native']


      
        #one row is one application
        for index, row in df.iterrows():
            app_name = row['Unnamed: 0']
            if pd.isna(app_name):
                break
            icx_speedup = row['ICX: -O3 -march=native']
            icc_speedup = row['ICC: -O3 -march=native']
            gcc_speedup = row['GCC: -O3 -march=native']

            #if there is empty value just continue
            if pd.isna(icx_speedup) or pd.isna(icc_speedup) or pd.isna(gcc_speedup):
                continue
            
      
            speedups = {'ICX': icx_speedup, 'ICC': icc_speedup, 'GCC': gcc_speedup}

            best_compiler_set = sorted(set(row['Best compiler'].split("/")))
            is_n_way_tie = len(best_compiler_set) == 3

            #if it is a tie just look at next application
            if is_n_way_tie:
                applications.append({
                'application': app_name,
                'is_n_way_tie': is_n_way_tie,
                'n_way' : len(best_compiler_set)
                })
                continue

            best_compiler = best_compiler_set[0].upper()


            best_time_key = f'{best_compiler}qaas'
            time_comp = {'ICX': row['ICX'],'ICC': row['ICC'], 'GCC': row['GCC'], best_time_key: row['Best (option) perf. (s)']}
            all_win_lose = []

            for baseline_compiler in ['ICX', 'ICC', 'GCC', best_time_key]:
                win_lose = calculate_speedup(time_comp, baseline_compiler)
                all_win_lose.extend(win_lose)

          
            applications.append({
                'application': app_name,
                'win_lose': all_win_lose,
                'is_n_way_tie': is_n_way_tie
            })
        print(applications)

        # print(applications)
        return jsonify({
            'compilers': compilers,
            'applications': applications
        })

    
    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True,port=5002)