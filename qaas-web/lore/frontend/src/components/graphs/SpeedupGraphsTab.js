import React from 'react';
import PieChart from './PieChart';
import { useState, useEffect } from 'react';
import TabSelector from '../data/TabSelector';
import LineGraph from './LineGrapah';
import Histogram from './Histogram'
import { RANGES } from '../Constants';
import { SPEEDUP_R_COLOR, SPEEDUP_M_COLOR, assignColorsToRanges } from '../Constants';
export default function SpeedupGraphsTab({ data }) {

    const tabs = ['Pie chart', 'Histogram', 'Unsorted line plot', 'Sorted line plot'];

    const [activeTab, setActiveTab] = useState('Pie chart');

    const generateData = (speedData) => {
        return RANGES.map(range => {
            if (range.includes('>')) {
                const min = parseFloat(range.split('>')[1]);
                return speedData.filter(speed => speed > min).length;
            } else {
                const [min, max] = range.split('-').map(Number);
                return speedData.filter(speed => speed >= min && speed < max).length;
            }
        });
    };


    const chartData = {
        labels: RANGES,
        datasets: [
            {
                label: 'Speedup R',
                data: generateData(data.map(d => d[Object.keys(d)[0]].speedup_r)),
                backgroundColor: SPEEDUP_R_COLOR,
                borderColor: SPEEDUP_R_COLOR

            },
            {
                label: 'Speedup M',
                data: generateData(data.map(d => d[Object.keys(d)[0]].speedup_m)),
                backgroundColor: SPEEDUP_M_COLOR,
                borderColor: SPEEDUP_M_COLOR

            }
        ]
    };

    const chartDataR = {
        title: 'Speedup R',
        labels: RANGES,
        datasets: [
            {
                label: 'Speedup R',
                data: generateData(data.map(d => d[Object.keys(d)[0]].speedup_r)),
                backgroundColor: assignColorsToRanges(RANGES)


            }
        ]
    };

    const chartDataM = {
        title: 'Speedup M',
        labels: RANGES,
        datasets: [
            {
                label: 'Speedup M',
                data: generateData(data.map(d => d[Object.keys(d)[0]].speedup_m)),
                backgroundColor: assignColorsToRanges(RANGES)


            }
        ]
    };

    const LineDataUnsorted = {
        labels: data.map((d, i) => i),
        datasets: [
            {
                label: 'Speedup R',
                data: data.map(d => d[Object.keys(d)[0]].speedup_r),
                backgroundColor: SPEEDUP_R_COLOR,
                borderColor: SPEEDUP_R_COLOR
            },
            {
                label: 'Speedup M',
                data: data.map(d => d[Object.keys(d)[0]].speedup_m),
                backgroundColor: SPEEDUP_M_COLOR,
                borderColor: SPEEDUP_M_COLOR
            }
        ]
    };

    const sortedData = [...data].sort((a, b) => a[Object.keys(a)[0]].speedup_r - b[Object.keys(b)[0]].speedup_r);

    const LineDataSorted = {
        labels: sortedData.map((d, i) => i),
        datasets: [
            {
                label: 'Speedup R',
                data: sortedData.map(d => d[Object.keys(d)[0]].speedup_r),
                backgroundColor: SPEEDUP_R_COLOR,
                borderColor: SPEEDUP_R_COLOR
            },
            {
                label: 'Speedup M',
                data: sortedData.map(d => d[Object.keys(d)[0]].speedup_m),
                backgroundColor: SPEEDUP_M_COLOR,
                borderColor: SPEEDUP_M_COLOR
            }
        ]
    };


    return (
        <div className="component-background" >
            <TabSelector activeTab={activeTab} setActiveTab={setActiveTab} tabs={tabs} />

            <div className='sub-tab-container'>
                {activeTab === 'Pie chart' &&
                    <div className="component-spacing">
                        <PieChart data={chartDataR} />
                        <PieChart data={chartDataM} />
                    </div>}

                {activeTab === 'Histogram' && <div className='speedup-graph-container'><Histogram data={chartData} /> </div>}
                {activeTab === 'Unsorted line plot' && <div className='speedup-graph-container'><LineGraph data={LineDataUnsorted} />  </div>}
                {activeTab === 'Sorted line plot' && <div className='speedup-graph-container'><LineGraph data={LineDataSorted} />  </div>}

            </div>

        </div>
    );
}