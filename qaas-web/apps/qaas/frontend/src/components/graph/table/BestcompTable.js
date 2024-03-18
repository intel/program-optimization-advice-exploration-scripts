import React, { useState, useEffect } from "react";
import CustomReactTable from "./CustomReactTable";
import { getCompilerColor, formatValue } from "../../Constants";
import TooltipComponent from "../../TooltipComponent";
import axios from "axios";

const columns = [
    { Header: 'MiniApp', accessor: 'miniapp', },
    { Header: 'Language', accessor: 'language', },
    {
        Header: () => (
            <TooltipComponent id="best-compiler-tooltip" content={<span>Best Compiler Definition</span>}>
                Best Compiler
            </TooltipComponent>
        ),

        accessor: 'best_compiler'
    },
    { Header: 'Time (s)', accessor: 'ICL_time' },
    { Header: 'Best total Gf for ICL with Ec > .5', accessor: 'gflops' },
    { Header: '#Cores used/48', accessor: 'cores_used' },

    { Header: 'GF/core', accessor: 'gf_per_core' },
    { Header: 'Unicore Gf', accessor: 'unicore_gf' },
    { Header: 'Ratio of Unicore GF over GF/core', accessor: 'ratio_unicore_df_over_df_per_core' }

];





function BestCompTable() {

    const [chartData, setChartData] = useState([]);
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_bestcomp_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processData(rawData);

                setChartData(preparedData);



            })

    }, [])

    function processData(rawData) {
        const formattedData = [];
        if (!rawData || Object.keys(rawData).length === 0) {
            return [];
        }
        const numRows = rawData.miniapp.length;

        for (let i = 0; i < numRows; i++) {
            formattedData.push({
                miniapp: rawData.miniapp[i],
                language: 'NA',

                best_compiler: formatValue(rawData.best_compiler[i]),
                ICL_time: formatValue(rawData.ICL_time[i]),
                gflops: formatValue(rawData.gflops[i]),
                cores_used: formatValue(rawData.cores_used[i]),
                gf_per_core: formatValue(rawData.gf_per_core[i]),
                unicore_gf: formatValue(rawData.unicore_gf[i]),
                ratio_unicore_df_over_df_per_core: formatValue(rawData.ratio_unicore_df_over_df_per_core[i]),

            });
        }

        //last row is ratio exclude
        const dataToSort = formattedData.slice(0, -1);
        const lastRow = formattedData[formattedData.length - 1];
        dataToSort.sort((a, b) => parseFloat(b.gflops) - parseFloat(a.gflops));
        const sortedDataWithLastRow = [...dataToSort, lastRow];
        return sortedDataWithLastRow;
    }

    //ability to give row color
    function getCellStyles(cell) {
        //put color on last row
        const isLastRow = cell.row.index === chartData.length - 1;

        if (isLastRow) {
            return {
                className: 'custom-header'
            };
        }
        //apply styles only to the 'best_compiler' column cells
        if (cell.column.id === 'best_compiler') {
            return {
                style: {
                    backgroundColor: getCompilerColor(cell.value),

                },
            };
        }
        return {};
    }
    return (
        < >

            <CustomReactTable columns={columns} data={chartData} getCellProps={getCellStyles} />
            <div className="plot-title" id="figbestcomp">
                Fig. Bestcomp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                High-level architectural differences between ICL miniapp runs

            </div>

        </>
    );
}

export default BestCompTable;
