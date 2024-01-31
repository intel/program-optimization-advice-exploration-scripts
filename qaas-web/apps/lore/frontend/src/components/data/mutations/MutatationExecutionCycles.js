import React from 'react';
import Table from '../table';
import DOMPurify from 'dompurify';

export default function MutatationExecutionCycles({ table_data }) {

    const transformedData = Object.keys(table_data).map((key) => {
        console.log({
            ...table_data[key],
            key: key,
        })
        return {
            ...table_data[key],
            key: key,
        };
    });

    const sanitizedTransformedData = DOMPurify.sanitize(transformedData)

    const columns = [

        {
            Header: 'Compiler',
            accessor: 'compiler'
        },
        {
            Header: 'Version',
            accessor: 'version'
        },
        {
            Header: 'CPU',
            accessor: 'cpu'
        },
        {
            Header: 'Reference (cc)',
            accessor: 'base'
        },
        {
            Header: 'Scalar(cc)',
            accessor: 'scalar'
        },

        {
            Header: 'SSE',
            accessor: 'sse'
        },
        {
            Header: 'AVX(cc)',
            accessor: 'avx'
        },
        {
            Header: 'AVX2(cc)',
            accessor: 'avx2'
        },

    ];

    return (
        <div>
            <Table
                data={sanitizedTransformedData}
                columns={columns}
                defaultPageSize={5}

            />

        </div>
    );
}
