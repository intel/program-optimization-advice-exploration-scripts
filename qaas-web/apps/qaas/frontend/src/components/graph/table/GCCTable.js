import React from "react";
import CustomReactTable from "./CustomReactTable";
const columns = [
    { Header: 'Compiler', accessor: 'vendor' },
    { Header: 'Compiler Version', accessor: 'version' },
    { Header: 'Compilation Date', accessor: 'date' },

];

const data = [
    { vendor: 'GCC', version: '13.1.1', date: '20230429', }

];


export default function GCCTable() {
    return (
        <div className='graphContainer'>
            <CustomReactTable columns={columns} data={data} />

        </div>
    );
}

