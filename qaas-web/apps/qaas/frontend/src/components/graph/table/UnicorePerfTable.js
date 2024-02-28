import React, { useState, useEffect } from "react";
import CustomReactTable from "./CustomReactTable";
import '../../css/graph.css'
import { getAppName } from '../../Constants';

import axios from "axios";


const columns = [
    { Header: 'Mini-Apps', accessor: 'Apps' },
    { Header: 'Intel SKL 2015', accessor: 'Intel SKL' },
    { Header: 'Intel ICL 2021', accessor: 'Intel ICL' },
    { Header: 'Intel SPR 3.9 GHz 2023', accessor: 'Intel SPR' },
    { Header: 'AMD Zen4 2022', accessor: 'AMD Zen4' },
    { Header: 'AWS G3E 2.6 GHz2022', accessor: 'AWS G3E' },
];

export default function UnicorePerfTable() {
    const [chartData, setChartData] = useState([]);
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_utab_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processData(rawData);
                setChartData(preparedData);



            })

    }, [])

    function formatValue(value) {
        if (typeof value === 'number') {
            return value.toFixed(2);
        } else if (value === null || value === undefined) {
            return 'NA';
        } else {
            return value;
        }
    }

    function processData(data) {
        if (!data.Apps || data.Apps.length === 0) {
            return [];
        }
        const numberOfRows = data.Apps.length;
        const processedData = [];
        //no data


        for (let i = 0; i < numberOfRows; i++) {
            let row = {};
            for (const key in data) {
                if (key === 'Apps') {
                    // unify app anme
                    row[key] = getAppName(data[key][i]);
                } else {
                    //  other columns, format value
                    row[key] = formatValue(data[key][i]);
                }
            }
            processedData.push(row);
        }

        // sort by spr
        return processedData.sort((a, b) => {
            const sprA = parseFloat(a["Intel SPR"]) || 0;
            const sprB = parseFloat(b["Intel SPR"]) || 0;
            return sprB - sprA;
        });
    }

    console.log(chartData)



    return (
        <div className='graphContainer'>



            <CustomReactTable columns={columns} data={chartData} />
            <div className="plot-title" id="figutab">Fig. utab&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Performance [Gf] for 7 miniapps on 5 unicore systems sorted on SPR</div>

        </div>
    );
}

