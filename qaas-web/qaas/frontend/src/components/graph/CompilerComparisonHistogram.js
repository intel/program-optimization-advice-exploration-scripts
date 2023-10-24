import React, { useState, useEffect } from 'react';
import Histogram from './Histogram';
import axios from "axios";
import { RANGES } from '../Constants';
import { categorizeSpeedupDynamic, COMPILER_COLORS, getCompilerColor } from '../Constants';
import { DEFAULT_COLOR_SCHEME } from "../Constants";
import { Chart, registerables } from "chart.js"
import HistogramBinSlider from './HistogramBinSlider';
import { BarTextPlugin } from './GraphPlugin';
export default function CompilerComparisonHistogram() {
    const [chartData, setChartData] = useState(null);
    const [leftMostBin, setLeftMostBin] = useState(1.1);
    const [rawData, setRawData] = useState(null);



    const handleSliderChange = (newValue) => {
        setLeftMostBin(newValue);
    };



    //set raw data first time
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_qaas_compiler_comparison_historgram_data`)
            .then((response) => {
                setRawData(response.data);


            })

    }, [])


    //change data when slide
    useEffect(() => {
        if (rawData) { // check if rawData exists
            const newChartData = {
                winerData: processData(rawData, true, leftMostBin),
                loserData: processData(rawData, false, leftMostBin)
            };
            setChartData(newChartData);
        }
    }, [rawData, leftMostBin]);


    if (!chartData) {
        return <div>testLoading...</div>
    }



    function processData(data, is_use_winer_color, leftMostBin) {
        const dynamicRanges = [
            `< ${leftMostBin}X`,
            `${leftMostBin}-1.2X`,
            '1.2-1.5X',
            '1.5-2X',
            '2-4X',
            '> 4X'
        ];
        let datasets = [];
        let addedToLegend = new Set(); // unique legends

        data.applications.forEach(app => {
            if (app.is_n_way_tie) {
                let counts = dynamicRanges.map(() => 0);
                let bestCompilerSpeedup = 1; // Assuming speedup is 1 in case of a tie
                let range = categorizeSpeedupDynamic(bestCompilerSpeedup, leftMostBin);
                counts[dynamicRanges.indexOf(range)] = 1;

                datasets.push({
                    label: addedToLegend.has("TIE") ? "" : "TIE",
                    data: counts,
                    backgroundColor: COMPILER_COLORS['TIE'],
                    barText: dynamicRanges.map(r => r === range ? `${app.application}: ${app.n_way}-way tie` : ""),
                    barPercentage: 1.0,
                    categoryPercentage: 1.0,
                });

                addedToLegend.add("TIE");
                return;
            }

            // Flatten win-lose data if not a tie
            const allWinLose = app.win_lose;

            allWinLose.forEach(winLoseData => {
                let counts = dynamicRanges.map(() => 0);
                let range = categorizeSpeedupDynamic(winLoseData.speedup, leftMostBin);
                counts[dynamicRanges.indexOf(range)] = 1;

                let compilerLabel = is_use_winer_color ? winLoseData.winner.substring(0, 3) : winLoseData.loser.substring(0, 3);
                console.log(compilerLabel)
                datasets.push({
                    label: addedToLegend.has(compilerLabel) ? "" : compilerLabel,
                    data: counts,
                    backgroundColor: getCompilerColor(compilerLabel),
                    barText: dynamicRanges.map(r => r === range ? `${app.application}: ${winLoseData.winner}/${winLoseData.loser}` : ""),
                    barPercentage: 1.0,
                    categoryPercentage: 1.0,
                });

                addedToLegend.add(compilerLabel); // avoid repeating legends
            });
        });

        return {
            labels: dynamicRanges,
            datasets: datasets,
            xAxis: 'Speedup Range',
            yAxis: 'Count'
        };
    }


    const chartOptions = {
        plugins: {
            legend: {
                labels: {
                    filter: function (item, chart) {
                        return ['ICX', 'ICC', 'GCC', 'TIE'].includes(item.text); //make sure it is unqiue
                    }
                }
            },
            tooltip: {
                enabled: false
            },
            barText: BarTextPlugin
        }
    };

    Chart.register(...registerables, BarTextPlugin);


    return (
        <div>

            <Histogram data={chartData.winerData} options={chartOptions} />
            <HistogramBinSlider onChange={handleSliderChange} />

        </div >
    )
}