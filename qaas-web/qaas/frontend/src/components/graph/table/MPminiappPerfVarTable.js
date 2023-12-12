import React from "react";
import CustomReactTable from "./CustomReactTable";
import { getGeneralColor } from "../../Constants";

const columns = [
    { Header: 'MiniApp', accessor: 'mini_app' },
    {
        Header: 'Scaling mode',
        accessor: 'scaling_mode',
        Cell: ({ value }) => {
            const color = value.includes('Weak') || value.includes('Hybrid') ? getGeneralColor('YellowHighlight') : 'inherit';
            return <div style={{ backgroundColor: color }}>{value}</div>;
        }

    },
    {
        Header: '#Cores/#Sockets',
        accessor: 'cores_per_sockets',
        Cell: ({ value }) => {
            const color = value.includes('16') ? getGeneralColor('YellowHighlight') : 'inherit';
            return <div style={{ backgroundColor: color }}>{value}</div>;
        }
    },
    {
        Header: '#MPI/affinity',
        accessor: 'mpi_per_affinity',
        Cell: ({ value }) => {
            const color = value.includes('2') ? getGeneralColor('Lose') : value.includes('32') ? getGeneralColor('BlueHighlight') : value.includes('NA') ? getGeneralColor('YellowHighlight') : 'inherit';
            return <div style={{ backgroundColor: color }}>{value}</div>;
        }
    },
    {
        Header: '#MPI/affinity',
        accessor: 'omp_per_affinity',
        Cell: ({ value }) => {
            const color = value.includes('24') ? getGeneralColor('Lose') : value.includes('1') ? getGeneralColor('BlueHighlight') : value.includes('48') ? getGeneralColor('YellowHighlight') : 'inherit';
            return <div style={{ backgroundColor: color }}>{value}</div>;
        }
    },
    { Header: 'Gflops', accessor: 'gflops' },
    {
        Header: 'Par. Eff W.r 1 core',
        accessor: 'eff_1_core',
        Cell: ({ value }) => {
            const color = value.includes('96') ? getGeneralColor('YellowHighlight') : 'inherit';
            return <div style={{ backgroundColor: color }}>{value}</div>;
        }
    },

];

const data = [
    { mini_app: 'MiniQMC', scaling_mode: 'Weak', cores_per_sockets: '32/2', mpi_per_affinity: '32/Scat.', omp_per_affinity: '1/Scat.', gflops: '409.61', eff_1_core: '0.61' },
    { mini_app: 'Kripke', scaling_mode: 'Strong', cores_per_sockets: '48/2', mpi_per_affinity: '2/Scat.', omp_per_affinity: '24/Scat.', gflops: '64.18', eff_1_core: '0.78' },
    { mini_app: 'Clvrlf ++', scaling_mode: 'Strong', cores_per_sockets: '32/2', mpi_per_affinity: '32/Scat.', omp_per_affinity: '1/Scat.', gflops: '140.70', eff_1_core: '0.52' },
    { mini_app: 'Clvrlf F', scaling_mode: 'Strong', cores_per_sockets: '16/2', mpi_per_affinity: '16/Scat.', omp_per_affinity: '1/Scat.', gflops: '41.41', eff_1_core: '0.67' },
    { mini_app: 'AMG', scaling_mode: 'Hybrid', cores_per_sockets: '32/2', mpi_per_affinity: '32/Scat.', omp_per_affinity: '1/Scat.', gflops: '19.55', eff_1_core: '0.52' },
    { mini_app: 'CoMD', scaling_mode: 'Strong', cores_per_sockets: '48/2', mpi_per_affinity: '2/Scat.', omp_per_affinity: '24/Scat.', gflops: '87.73', eff_1_core: '0.66' },
    { mini_app: 'HACC', scaling_mode: 'Strong', cores_per_sockets: '48/2', mpi_per_affinity: '1/NA.', omp_per_affinity: '48/Com.', gflops: '794.96', eff_1_core: '0.96' }
];


export default function MPminiappPerfVarTable() {
    return (
        <div className='graphContainer'>
            <CustomReactTable columns={columns} data={data} />
            <div className="plot-title">
            Fig. Parvar&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mp miniapp performance varieties - 1 node/2 socket HW

            </div>
        </div>
    );
}

