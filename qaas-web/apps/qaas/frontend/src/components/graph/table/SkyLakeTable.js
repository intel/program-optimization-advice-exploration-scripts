import React from "react";
import CustomReactTable from "./CustomReactTable";
const columns = [
    { Header: 'Machine Name', accessor: 'machine_name' },
    { Header: 'Model Name', accessor: 'model_name' },
    { Header: 'Architecture', accessor: 'arch' },
    { Header: 'Micro Architecture', accessor: 'micro_arch' },
    { Header: 'Cache Size', accessor: 'cache_size' },
    { Header: 'Number of cores', accessor: 'cores' },
    { Header: 'OS Version', accessor: 'os' },
    { Header: 'Number of Sockets', accessor: 'sockets' },
    { Header: 'Number of Cores per Socket', accessor: 'cores_per_sockets' },


];

const data = [
    { machine_name: 'skylake', model_name: 'Intel(R) Xeon(R) Platinum 8170 CPU @ 2.10GHz', arch: 'x86_64', micro_arch: 'SKYLAKE', cache_size: '36608 KB', cores: '26', os: 'Linux 6.4.1-arch2-1 #1 SMP PREEMPT_DYNAMIC Tue, 04 Jul 2023 08:39:40 +0000', sockets: '2', 'cores_per_sockets': '26' },

];


export default function SkyLakeTable() {
    return (
        <div className='graphContainer'>
            <CustomReactTable columns={columns} data={data} />

        </div>
    );
}

