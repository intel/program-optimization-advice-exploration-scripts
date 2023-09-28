import React, { useState, useEffect } from 'react';
import Table from './table';
import '../css/table.css';
import ApplicationSubTable from './ApplicationSubTable';
import { GroupToggleButton } from './GroupToggleButton';
import { TABLE_COLOR_SCHEME, APPLICATION_TABLE_COLUMNS, STATIC_COLUMNS } from '../Constants';
function ApplicationTable({ data, selectedRows, setSelectedRows, baseline, setBaseline }) {
    const [expanded, setExpanded] = useState({});
    const [hiddenChildColumns, setHiddenChildColumns] = useState([]);
    useEffect(() => {
        // initialzie hiddenChildColumns based on STATIC_COLUMNS and default collapsed groups
        let defaultHiddenColumns = [];
        Object.keys(STATIC_COLUMNS).forEach(groupName => {
            const group = columns.find(col => col.groupName === groupName);
            if (group && group.columns) {
                const childColumns = group.columns.map(col => col.id).filter(id => !STATIC_COLUMNS[groupName].includes(id));
                defaultHiddenColumns = [...defaultHiddenColumns, ...childColumns];
            }
        });
        setHiddenChildColumns(defaultHiddenColumns);
    }, []);
    


    // add color to colums
    const columns = APPLICATION_TABLE_COLUMNS.map((col, index) => {
        if (col.columns) {
            const updatedSubColumns = col.columns.map(subCol => ({
                ...subCol,
                color: TABLE_COLOR_SCHEME[index % TABLE_COLOR_SCHEME.length]
            }));
            return { ...col, columns: updatedSubColumns };
        }
        return col;
    });




    //hid or show group columns
    const toggleGroup = (groupName) => {
        const group = columns.find(col => col.groupName === groupName);
        if (group && group.columns) {
            const staticColumns = STATIC_COLUMNS[groupName] || [];
            const childColumns = group.columns.map(col => col.id).filter(id => !staticColumns.includes(id));
    
            if (childColumns.some(id => hiddenChildColumns.includes(id))) {
                setHiddenChildColumns(prev => prev.filter(id => !childColumns.includes(id)));
            } else {
                setHiddenChildColumns(prev => [...prev, ...childColumns]);
            }
        }
    };

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
            <div style={{ padding: "20px" }}>
                <ApplicationSubTable data={row['run_data']} setSelectedRows={setSelectedRows} selectedRows={selectedRows}
                    baseline={baseline} setBaseline={setBaseline} />
            </div>
        );
    };

    const handleExpandedChange = (newExpanded) => {
        setExpanded(newExpanded);
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
                    SubComponent={(row) => renderSubComponent(row.original)}
                    expanded={expanded}
                    onExpandedChange={handleExpandedChange}
                    defaultPageSize={10}
                />
            </div>
        </div>
    );
}

export default ApplicationTable;
