import React, { useState, useEffect } from 'react';
import { useTable } from 'react-table';
import axios from 'axios';
import { REACT_APP_API_BASE_URL } from '../Constants';
export default function StaticFeatureList({ current_src_loop_id }) {



    const [data, setData] = useState([]);

    useEffect(() => {
        axios.post(`${REACT_APP_API_BASE_URL}/get_lore_static_loop_info_for_specific_loop`, {
            current_src_loop_id: current_src_loop_id
        })
            .then(response => {
                setData(response.data);
            })
            .catch(error => {
                console.error('Error fetching data: ', error);
            });
    }, [current_src_loop_id]);


    const columns = React.useMemo(
        () => [
            { Header: 'Column', accessor: 'column' },
            { Header: 'Value', accessor: 'value' },
        ],
        []
    );

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
    } = useTable({ columns, data });

    return (
        <div className='component-background'>
            <div className="table-container">
                <table {...getTableProps()} className="styled-table">
                    <tbody {...getTableBodyProps()}>
                        {rows.map((row, i) => {
                            prepareRow(row);
                            return (
                                <tr {...row.getRowProps()} className={i % 2 === 0 ? 'even-row' : 'odd-row'}>
                                    {row.cells.map(cell => {
                                        return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

