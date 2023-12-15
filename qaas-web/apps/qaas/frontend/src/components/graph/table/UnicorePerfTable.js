import React from "react";
import CustomReactTable from "./CustomReactTable";
import { getCompilerColor } from "../../Constants";
import '../../css/graph.css'
const columns = [
    { Header: 'Mini-Apps', accessor: 'miniApp' },
    { Header: 'Intel SKL 2015', accessor: 'skl' },
    { Header: 'Intel ICL 2021', accessor: 'icl' },
    { Header: 'Intel SPR 3.9 GHz 2023', accessor: 'spr' },
    { Header: 'AMD Zen4 2022', accessor: 'zen4' },
    { Header: 'AWS G3E 2.6 GHz2022', accessor: 'g3e' },
];

const data = [
    { miniApp: 'Miniqmc', skl: '13.41', icl: '20.67', spr: '24.30', zen4: '19.33', g3e: '16.30' },
    { miniApp: 'AMG', skl: '0.75', icl: '1.23', spr: '1.21', zen4: '1.55', g3e: '1.71' },
    { miniApp: 'Kripke (large)', skl: '1.54', icl: '2.86', spr: '3.71', zen4: '3.15', g3e: '3.44' },
    { miniApp: 'CoMD', skl: '1.94', icl: '3.75', spr: '5.06', zen4: '4.36', g3e: '3.56' },
    { miniApp: 'HACCmk', skl: '12.87', icl: '21.49', spr: '23.96', zen4: 'NA', g3e: 'NA' },
    { miniApp: 'CloverLeaf CC', skl: 'NA', icl: '13.12', spr: '15.16', zen4: 'NA', g3e: 'NA' },
    { miniApp: 'CloverLeaf FC', skl: 'NA', icl: '4.61', spr: '4.42', zen4: 'NA', g3e: 'NA' },
];


function processData(data) {
    //sort table by flops
    return [...data].sort((a, b) => parseFloat(a.spr) - parseFloat(b.spr));
}
const sortedData = processData(data);


export default function UnicorePerfTable() {
    return (
        <div className='graphContainer'>



            <CustomReactTable columns={columns} data={sortedData} />
            <div className="plot-title" id="figutab">Fig. utab&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Performance [Gf] for 7 miniapps on 5 systems</div>

        </div>
    );
}

