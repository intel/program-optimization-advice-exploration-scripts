import React, { useState, useEffect } from 'react';
import Histogram from './Histogram';
import axios from "axios";
import { RANGES } from '../Constants';
import { categorizeSpeedup } from '../Constants';
import { DEFAULT_COLOR_SCHEME } from "../Constants";
import { Chart, registerables } from "chart.js"

export default function CompilerComparisonHistogram() {
    const [winerData, setWinerData] = useState(null);
    const [loserData, setLoserData] = useState(null);
    const COMPILER_COLORS = {
        'ICX': DEFAULT_COLOR_SCHEME[0],
        'ICC': DEFAULT_COLOR_SCHEME[1],
        'GCC': DEFAULT_COLOR_SCHEME[2],
        'TIE': DEFAULT_COLOR_SCHEME[3]
    };

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_qaas_compiler_comparison_historgram_data`)
            .then((response) => {
                setWinerData(processData(response.data, true));
                setLoserData(processData(response.data, false));

            })

    }, [])

    if (!winerData || !loserData) {
        console.log("envvvvv variable", process.env.REACT_APP_API_BASE_URL)

        return <div>testLoading...</div>
    }



    function getCompilerColor(compiler) {
        return COMPILER_COLORS[compiler];
    }

    function processData(data, is_use_winer_color) {
        let datasets = [];
        let addedToLegend = new Set();  // unique legends

        data.applications.forEach(app => {


            if (app.is_n_way_tie) {
                let counts = RANGES.map(() => 0);
                let bestCompilerSpeedup = app.losers.find(loser => loser.compiler === app.best_compiler)?.speedup || 1; // default 1 if not found
                let range = categorizeSpeedup(bestCompilerSpeedup);
                counts[RANGES.indexOf(range)] = 1;
                let n = app.losers.length + 1;

                datasets.push({
                    label: addedToLegend.has("TIE") ? "" : "TIE",
                    data: counts,
                    backgroundColor: COMPILER_COLORS['TIE'],
                    barText: RANGES.map(r => r === range ? `${app.application}: ${n}-way tie` : "")
                });

                addedToLegend.add("TIE");
                return;  // move to the next application without processing losers
            }

            app.losers.forEach(loserData => {
                let counts = RANGES.map(() => 0);
                let range = categorizeSpeedup(loserData.speedup);
                counts[RANGES.indexOf(range)] = 1;
                let compilerLabel = is_use_winer_color ? app.best_compiler : loserData.compiler;
                console.log(is_use_winer_color, compilerLabel, app.application)

                datasets.push({
                    label: addedToLegend.has(compilerLabel) ? "" : compilerLabel,
                    data: counts,
                    backgroundColor: is_use_winer_color ? getCompilerColor(app.best_compiler) : getCompilerColor(loserData.compiler),
                    barText: RANGES.map(r => r === range ? `${app.application}: ${app.best_compiler}/${loserData.compiler}` : "")
                });

                addedToLegend.add(compilerLabel);  // avoid repeatkng legends
            });
        });

        return {
            labels: RANGES,
            datasets: datasets,
            xAxis: 'Speedup Range',
            yAxis: 'Count'
        };
    }

    const barTextPlugin = {
        id: 'barText',
        afterDraw: (chart) => {
            const ctx = chart.ctx;
            chart.data.datasets.forEach((dataset, datasetIndex) => {
                const meta = chart.getDatasetMeta(datasetIndex);
                if (meta.hidden) return;

                ctx.fillStyle = 'white';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                meta.data.forEach((bar, index) => {
                    const label = dataset.barText && dataset.barText[index];
                    if (label) {
                        ctx.fillText(label, bar.x, bar.y + bar.height / 2); //middle
                    }
                });
            });
        }
    };


    const chartOptions = {
        plugins: {
            legend: {
                labels: {
                    filter: function (item, chart) {
                        return ['ICX', 'ICC', 'GCC', 'TIE'].includes(item.text); //make sure it is unqiue
                    }
                }
            },
            barText: barTextPlugin
        }
    };

    Chart.register(...registerables, barTextPlugin);


    return (
        <div>
            <Histogram data={winerData} options={chartOptions} />
            <Histogram data={loserData} options={chartOptions} />

        </div>
    )
}