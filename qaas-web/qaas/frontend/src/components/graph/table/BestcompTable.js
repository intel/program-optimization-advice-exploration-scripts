import React from "react";
import CustomReactTable from "./CustomReactTable";
import { getCompilerColor } from "../../Constants";
const columns = [
    { Header: 'MiniApp', accessor: 'miniApp', },
    { Header: 'Language', accessor: 'language', },
    { Header: 'Best Compiler', accessor: 'bestCompiler' },
    { Header: 'Time (s)', accessor: 'time' },
    { Header: 'Best total Gf for ICL with Ec > .5', accessor: 'gflops' },
    { Header: '#Cores used/48', accessor: 'coresUsed' },

    { Header: 'GF/core', accessor: 'gflopsPerCore' },
    { Header: 'Unicore Gf', accessor: 'unicoreGf' },
    { Header: 'Ratio of Unicore GF / GF/core', accessor: 'ratioUnicoreGfPerCore' }

];

const data = [
    { miniApp: 'MiniQMC', language: 'C/C++', bestCompiler: 'ICX', time: '71.94', gflops: '409.61', gflopsPerCore: '12.80', unicoreGf: '20.67', coresUsed: '32' },
    { miniApp: 'Kripke (large)', language: 'C++', bestCompiler: 'GCC', time: '76.72', gflops: '64.18', gflopsPerCore: '1.34', unicoreGf: '2.86', coresUsed: '48' },
    { miniApp: 'CloverLeaf (C++)', language: 'C++', bestCompiler: 'ICC', time: '58.34', gflops: '140.70', gflopsPerCore: '4.40', unicoreGf: '13.12', coresUsed: '32' },
    { miniApp: 'CloverLeaf (F)', language: 'Fortran', bestCompiler: 'ICC', time: '202.17', gflops: '41.41', gflopsPerCore: '2.59', unicoreGf: '4.61', coresUsed: '16' },
    { miniApp: 'AMG', language: 'C', bestCompiler: 'Tie', time: '51.05', gflops: '19.55', gflopsPerCore: '0.61', unicoreGf: '1.23', coresUsed: '32' },
    { miniApp: 'CoMD', language: 'C', bestCompiler: 'GCC', time: '24.00', gflops: '87.73', gflopsPerCore: '1.83', unicoreGf: '3.75', coresUsed: '48' },
    { miniApp: 'HACC', language: 'C', bestCompiler: 'Tie', time: '29.24', gflops: '794.96', gflopsPerCore: '16.56', unicoreGf: '21.45', coresUsed: '48' },
    { miniApp: 'Ratios r=max/min', language: '', bestCompiler: '', time: 'r = 8.4', gflops: 'r =40.66', gflopsPerCore: 'r =27.15', unicoreGf: 'r =17.4', coresUsed: 'Eff. > .5' },
];

function processData(data) {
    //sort table by flops
    return data.map(row => {
        const unicoreGf = parseFloat(row.unicoreGf);
        const gflopsPerCore = parseFloat(row.gflopsPerCore);
        let ratio;

        if (!isNaN(unicoreGf) && !isNaN(gflopsPerCore) && gflopsPerCore !== 0) {
            ratio = (unicoreGf / gflopsPerCore).toFixed(2);
        } else {
            ratio = '';
        }

        // Add the new property to the row
        return {
            ...row,
            ratioUnicoreGfPerCore: ratio
        };
    }).sort((a, b) => parseFloat(b.gflops) - parseFloat(a.gflops));
}
const sortedData = processData(data);

//ability to give row color
function getCellStyles(cell) {
    //apply styles only to the 'bestCompiler' column cells
    if (cell.column.id === 'bestCompiler') {
        return {
            style: {
                backgroundColor: getCompilerColor(cell.value),

            },
        };
    }
    return {};
}

function BestCompTable() {
    return (
        < >

            <div className='graphContainer'><CustomReactTable columns={columns} data={sortedData} getCellProps={getCellStyles} /></div>
            <div className="plot-title">
                Fig. Bestcomp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                High-level architectural differences between ICL miniapp runs

            </div>

        </>
    );
}

export default BestCompTable;
