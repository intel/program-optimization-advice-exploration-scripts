import React, { useState, useEffect } from "react";
import CustomReactTable from "./CustomReactTable";
import { getGeneralColor, formatValue, REACT_APP_API_BASE_URL } from "../../Constants";
import axios from "axios";

const columns = [
    { Header: 'MiniApp', accessor: 'miniapp' },
    { Header: 'Best total Gf', accessor: 'best_total_gf' },

    {
        Header: '#Cores used', columns: [
            {
                Header: 'ICL /48',
                accessor: 'cores_icl',
                Cell: ({ value }) => {
                    const stringValue = value != null ? value.toString() : '';

                    const color = stringValue.includes('All') ? getGeneralColor('Win') : 'inherit'; //  Green for 'All 48'
                    return <div style={{ backgroundColor: color }}>{stringValue}</div>;
                }
            },
            {
                Header: 'SPR /64',
                accessor: 'cores_spr',
                Cell: ({ value }) => {
                    const stringValue = value != null ? value.toString() : '';


                    const color = stringValue.includes('All') ? getGeneralColor('Win') : 'inherit'; //  Green for 'All 64'
                    return <div style={{ backgroundColor: color }}>{stringValue}</div>;
                }
            },
        ]
    },
    {
        Header: 'Ratios SPR/ICL: Freq ratio = .79', columns: [
            {
                Header: 'SPR/ICL Total cores ratio',
                accessor: 'total_cores_ratio',
                Cell: ({ value }) => {
                    const stringValue = value != null ? value.toString() : '';
                    const color = stringValue.includes('1.33') ? getGeneralColor('Win') : 'inherit'; //  1.33 green 
                    return <div style={{ backgroundColor: color }}>{stringValue}</div>;
                }
            }
        ]
    }
];




export default function MpratioTable() {

    const [chartData, setChartData] = useState([]);
    useEffect(() => {
        axios.get(`${REACT_APP_API_BASE_URL}/get_mpratio_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processData(rawData);

                setChartData(preparedData);



            })

    }, [])

    function processData(rawData) {
        if (!rawData || Object.keys(rawData).length === 0) {
            return [];
        }
        const formattedData = [];
        const numRows = rawData.miniapp.length;

        for (let i = 0; i < numRows; i++) {
            formattedData.push({
                miniapp: rawData.miniapp[i],
                best_total_gf: formatValue(rawData.best_total_gf[i]),
                cores_icl: rawData.cores_icl[i] === 48 ? 'All 48' : formatValue(rawData.cores_icl[i]),
                cores_spr: rawData.cores_spr[i] === 64 ? 'All 64' : formatValue(rawData.cores_spr[i]),
                total_cores_ratio: formatValue(rawData.total_cores_ratio[i]),
            });
        }

        return formattedData;
    }
    return (
        <div className='graphContainer'>
            <CustomReactTable columns={columns} data={chartData} />
            <div className="plot-title" id="figmpratio">
                Fig. MPratio&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ICL and SPR Multicore Use Differences for 7 Miniapps

            </div>
        </div>
    );
}

