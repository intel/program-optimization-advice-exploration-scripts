import React, { useState, useEffect, useMemo } from 'react';
import Table from './table';
import '../css/table.css';
import ApplicationSubTable from './ApplicationSubTable';
import { GroupToggleButton } from './GroupToggleButton';
import { TABLE_COLOR_SCHEME, APPLICATION_TABLE_COLUMNS } from '../Constants';
//resurive function to find toggleable columes
const findToggleableColumns = (cols) => {
    let toggleable = [];
    cols.forEach(col => {
        if (col.columns) {
            toggleable = [...toggleable, ...findToggleableColumns(col.columns)];
        } else if (col.show === false) {
            toggleable.push(col.id);
        }
    });
    return toggleable;
};

const ApplicationTable = React.memo(({ data, baseline, setBaseline }) => {
    const [hiddenChildColumns, setHiddenChildColumns] = useState([]);
    useEffect(() => {
        let defaultHiddenColumns = findToggleableColumns(columns);
        setHiddenChildColumns(defaultHiddenColumns);
    }, [columns]);



    //hid or show group columns
    const toggleGroup = (groupName) => {
        const group = columns.find(col => col.id === `${groupName}_parent`) || columns.find(col => col.groupName === groupName);

        if (group && group.columns) {
            const toggleableColumns = findToggleableColumns(group.columns);

            if (toggleableColumns.some(id => hiddenChildColumns.includes(id))) {
                setHiddenChildColumns(prev => prev.filter(id => !toggleableColumns.includes(id)));
            } else {
                setHiddenChildColumns(prev => [...prev, ...toggleableColumns]);
            }
        }
    };





    // add color to colums
    const columns = APPLICATION_TABLE_COLUMNS;






    //filtered out all visible cols
    const visibleColumns = columns.map(col => {
        if (col.columns) {
            const visibleChildColumns = col.columns.filter(subCol => !hiddenChildColumns.includes(subCol.id));
            return {
                ...col,
                columns: visibleChildColumns
            };
        }
        return col;
    });

    const renderSubComponent = (row) => {
        return (
            <ApplicationSubTable data={row.row.original['run_data']} baseline={baseline} setBaseline={setBaseline} />
        );
    };




    return (
        <div >

            <div className="center">
                <GroupToggleButton

                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                />
                <Table
                    data={data}
                    columns={visibleColumns}
                    SubComponent={(row) => renderSubComponent(row)}
                    hiddenColumns={hiddenChildColumns}

                    defaultPageSize={10}
                />
            </div>
        </div>
    );
})


export default ApplicationTable;