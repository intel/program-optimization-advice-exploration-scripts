
import pandas as pd

from flask import Flask
from flask_cors import CORS
from flask import jsonify

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route('/get_qaas_compiler_comparison_historgram_data', methods=['GET'])
    def get_qaas_compiler_comparison_historgram_data():
        df = pd.read_excel('/host/home/yjiao/mock_QaaS_Min_Max_Unicore_Perf_Default.xlsx', header=3)
        
        # List to store unique compilers
        compilers = ['ICX', 'ICC', 'GCC']

        applications = []
        delta = 0.03  # 3% threshold

        for index, row in df.iterrows():
            app_name = row['Unnamed: 0']
            print(app_name)
            if pd.isna(app_name):
                break
            icx_speedup = row['ICX: -O3 -march=native']
            icc_speedup = row['ICC: -O3 -march=native']
            gcc_speedup = row['GCC: -O3 -march=native']

            speedups = {'ICX': icx_speedup, 'ICC': icc_speedup, 'GCC': gcc_speedup}
            print(row['Best compiler'])
            best_compiler_set = sorted(set(row['Best compiler'].split("/")))
            
            is_n_way_tie = len(best_compiler_set) == 3
            best_compiler = best_compiler_set[0].upper()


            #  maxc(WC/c) for all compilers
            max_speedup = max([icx_speedup, icc_speedup, gcc_speedup])
            is_n_way_tie = max_speedup < (1 + delta) 

            # Remove the best compiler from the dict
            del speedups[best_compiler]

            # Rank the other compilers
            ranked_compilers = sorted(speedups, key=speedups.get, reverse=True)

            applications.append({
                'application': app_name,
                'best_compiler': best_compiler,
                'losers': [{'compiler': loser, 'speedup': speedups[loser]} for loser in ranked_compilers],
                'is_n_way_tie': is_n_way_tie

            })

        print(applications)
        return jsonify({
            'compilers': compilers,
            'applications': applications
        })

    
    return app
