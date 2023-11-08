import React from "react";
import CustomReactTable from "./CustomReactTable";
import { getGeneralColor } from "../../Constants";
const columns = [
    { Header: 'MiniApp', accessor: 'miniApp' },
    { Header: 'Best total Gf', accessor: 'bestTotalGf' },

    {
        Header: '#Cores used', columns: [
            {
                Header: 'ICL /48',
                accessor: 'coresUsedICL',
                Cell: ({ value }) => {
                    const color = value.includes('1/3') ? getGeneralColor('Lose') : value.includes('All') ? getGeneralColor('Win') : 'inherit'; //  Red for '1/3 = 16',  Green for 'All 48'
                    return <div style={{ backgroundColor: color }}>{value}</div>;
                }
            },
            {
                Header: 'SPR /64',
                accessor: 'coresUsedSPR',
                Cell: ({ value }) => {
                    const color = value.includes('1/4') ? getGeneralColor('Lose') : value.includes('All') ? getGeneralColor('Win') : 'inherit'; //  Red for '1/4 = 16',  Green for 'All 64'
                    return <div style={{ backgroundColor: color }}>{value}</div>;
                }
            },
        ]
    },
    {
        Header: 'Ratios SPR/ICL', columns: [
            { Header: 'Freq ratio = .79', accessor: 'freqRatio' },
            { Header: 'SPR/ICL Total cores ratio', accessor: 'totalCoresRatio' }
        ]
    }
];

const data = [
    { miniApp: 'AMG', bestTotalGf: '19.55', coresUsedICL: '2/3 = 32', coresUsedSPR: '1/2 = 32', freqRatio: '.79', totalCoresRatio: '1.00' },
    { miniApp: 'Clvrlf F', bestTotalGf: '41.41', coresUsedICL: '1/3 = 16', coresUsedSPR: '1/4 = 16', freqRatio: '.79', totalCoresRatio: '1.00' },
    { miniApp: 'Kripke', bestTotalGf: '64.18', coresUsedICL: 'All 48', coresUsedSPR: 'All 64', freqRatio: '.79', totalCoresRatio: '1.33' },
    { miniApp: 'CoMD', bestTotalGf: '87.73', coresUsedICL: 'All 48', coresUsedSPR: 'All 64', freqRatio: '.79', totalCoresRatio: '1.33' },
    { miniApp: 'Clvrlf ++', bestTotalGf: '140.70', coresUsedICL: '2/3 = 32', coresUsedSPR: '1/2 = 32', freqRatio: '.79', totalCoresRatio: '1.00' },
    { miniApp: 'MiniQMC', bestTotalGf: '409.61', coresUsedICL: '2/3 = 32', coresUsedSPR: '1/2 = 32', freqRatio: '.79', totalCoresRatio: '1.00' },
    { miniApp: 'HACC', bestTotalGf: '794.96', coresUsedICL: 'All 48', coresUsedSPR: 'All 64', freqRatio: '.79', totalCoresRatio: '1.33' }
];


export default function MpratioTable() {
    return (
        <div className='graphContainer'>
            <CustomReactTable columns={columns} data={data} />
        </div>
    );
}

