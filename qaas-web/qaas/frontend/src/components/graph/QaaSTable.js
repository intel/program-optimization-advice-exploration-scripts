import React from 'react';
import CategoryTable from './CategoryTable';

const QaaSTable = () => {
    const columns = React.useMemo(
        () => [
            {
                Header: 'Main Column',
                columns: [
                    {
                        Header: 'Subcolumn 1',
                        accessor: 'subcolumn1',
                    },
                    {
                        Header: 'Subcolumn 2',
                        accessor: 'subcolumn2',
                    },
                ],
            },
            {
                Header: 'Other Column',
                accessor: 'otherColumn',
            },
        ],
        []
    );

    const data = React.useMemo(
        () => [
            {
                subcolumn1: 'Value 1',
                subcolumn2: 'Value 2',
                otherColumn: 'Value 3',
            },
            // Add more data rows as needed
        ],
        []
    );

    return <CategoryTable columns={columns} data={data} />;
};

export default QaaSTable;
