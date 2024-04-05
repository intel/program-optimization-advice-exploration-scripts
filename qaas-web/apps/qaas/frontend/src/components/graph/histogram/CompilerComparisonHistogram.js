import React, { useState, useEffect } from 'react';
import Histogram from './Histogram';
import axios from "axios";
import { RANGES } from '../../Constants';
import { categorizeSpeedupDynamic, COMPILER_COLORS, getCompilerColor } from '../../Constants';
import { DEFAULT_COLOR_SCHEME, REACT_APP_API_BASE_URL } from "../../Constants";
import { Chart, registerables } from "chart.js"
import HistogramBinSlider from './HistogramBinSlider';
import { BarTextPlugin } from '../GraphPlugin';
import FilterMenu from './FilterMenu';
import '../../css/graph.css'
import { INITIAL_FILTERS, getUnselectedFilters } from './FilterConstant';
Chart.register(...registerables);

export default function CompilerComparisonHistogram() {
    const [chartData, setChartData] = useState(null);
    const [leftMostBin, setLeftMostBin] = useState(1.1);
    const [rawData, setRawData] = useState(null);
    const [selectedFilters, setSelectedFilters] = useState(INITIAL_FILTERS);


    const applyFilters = () => {
        if (rawData) {
            // console.log("apply filter", selectedFilters)
            const filteredData = filterData(rawData, selectedFilters);
            // console.log(filteredData)
            setChartData(processData(filteredData, leftMostBin));
        }
    };
    //filter data that has selected = false
    const filterData = (data, filters) => {
        const unselectedFilters = getUnselectedFilters(filters);
        // console.log(unselectedFilters)
        //filer unselected applicaiton
        let filteredApplications = data.applications.filter((app) =>
            !unselectedFilters.includes(app.application)
        );
        //filter unselected compiler
        filteredApplications = filteredApplications.map((app) => {
            if (app.win_lose && app.win_lose.length) {
                const filteredWinLose = app.win_lose.filter(wl =>
                    !unselectedFilters.includes(wl.winner) &&
                    !unselectedFilters.includes(wl.loser)
                );

                // Return a new object if win_lose was modified, otherwise return the original app object
                return filteredWinLose.length === app.win_lose.length ? app : { ...app, win_lose: filteredWinLose };
            }
            return app;
        });
        //filter applications that have an empty win_lose array unless they are tied
        filteredApplications = filteredApplications.filter((app) => {
            return app.is_n_way_tie || (app.win_lose && app.win_lose.length > 0);
        });
        // console.log("data after filtered", filteredApplications)

        return {
            ...data,
            applications: filteredApplications,
        };
    };


    //slide change set bin
    const handleSliderChange = (newValue) => {
        setLeftMostBin(newValue);
    };



    //set raw data first time
    useEffect(() => {
        axios.get(`${REACT_APP_API_BASE_URL}/get_qaas_compiler_comparison_historgram_data`)
            .then((response) => {
                setRawData(response.data);


            })

    }, [])




    //change data when slide
    useEffect(() => {
        if (rawData) {
            setChartData(processData(rawData, leftMostBin));
        }
    }, [rawData, leftMostBin]);


    if (!chartData) {
        return <div>testLoading...</div>
    }



    function processData(data, leftMostBin) {
        const dynamicRanges = [
            `< ${leftMostBin}X`,
            `${leftMostBin}-1.2X`,
            '1.2-1.5X',
            '1.5-2X',
            '2-4X',
            '> 4X'
        ];
        let datasets = [];

        data.applications.forEach(app => {
            if (app.is_n_way_tie) {
                let counts = dynamicRanges.map(() => 0);
                let bestCompilerSpeedup = 1;
                let range = categorizeSpeedupDynamic(bestCompilerSpeedup, leftMostBin);
                counts[dynamicRanges.indexOf(range)] = 1;

                datasets.push({
                    label: "TIE",
                    data: counts,
                    backgroundColor: COMPILER_COLORS['TIE'],
                    barText: dynamicRanges.map(r => r === range ? `${app.application}: ${app.n_way}-way tie` : ""),
                    barPercentage: 1.0,
                    categoryPercentage: 1.0,
                });

                return;
            }

            // Flatten win-lose data if not a tie
            const allWinLose = app.win_lose;

            allWinLose.forEach(winLoseData => {
                let counts = dynamicRanges.map(() => 0);
                let range = categorizeSpeedupDynamic(winLoseData.speedup, leftMostBin);
                counts[dynamicRanges.indexOf(range)] = 1;

                let compilerLabel = winLoseData.winner.substring(0, 3)
                datasets.push({
                    label: compilerLabel,
                    data: counts,
                    backgroundColor: getCompilerColor(compilerLabel),
                    barText: dynamicRanges.map(r => r === range ? `${app.application}: ${winLoseData.winner}/${winLoseData.loser}` : ""),
                    //bin no space in bt
                    barPercentage: 1.0,
                    categoryPercentage: 1.0,
                });

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
            title: {
                display: true,
                text: 'Table Compare',

            },

            legend: {
                labels: {
                    //map compiler to the corresponding color
                    generateLabels: function () {
                        const compilerNames = ['ICX', 'ICC', 'GCC', 'TIE'];
                        return compilerNames.map((name) => ({
                            text: name,
                            fillStyle: getCompilerColor(name),
                            color: 'black'
                        }));
                    }
                }
            },
            tooltip: {
                enabled: false
            },
        },


    };

    // console.log("chart data", chartData)

    return (
        <div >
            <FilterMenu setSelectedFilters={setSelectedFilters} selectedFilters={selectedFilters} applyFilters={applyFilters} />
            <div className='graph-container-tall-histogram'>

                <Histogram data={chartData} options={chartOptions} plugins={[BarTextPlugin]} />
            </div>
            <HistogramBinSlider onChange={handleSliderChange} />

        </div >
    )
}