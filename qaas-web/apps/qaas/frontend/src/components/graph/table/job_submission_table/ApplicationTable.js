import React, { useState, useEffect, useMemo } from 'react';
import Table from './table';
import '../../../css/table.css';
import ApplicationSubTable from './ApplicationSubTable';

const ApplicationTable = React.memo(({ data }) => {


    // add color to colums
    const columns = [
        { Header: 'Application', accessor: 'app_name', },
        { Header: 'Timestamp', accessor: 'qaas_timestamp' },
        { Header: 'Archicture', accessor: 'arch' },
        { Header: 'Model', accessor: 'model' },
    ];;


    const renderSubComponent = (row) => {
        return (
            <ApplicationSubTable data={row.row['run_data']} />
        );
    };




    return (
        <div >

            <div className="center">
                <Table
                    data={data}
                    columns={columns}
                    SubComponent={(row) => renderSubComponent(row)}
                    defaultPageSize={10}
                />
            </div>
        </div>
    );
})


export default ApplicationTable;