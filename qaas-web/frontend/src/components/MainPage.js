import React, { useState, useEffect } from 'react';
import TopBar from './TopBar';
import './css/main.css'
import Title from './Title';
import ApplicationTable from './data/ApplicationTable';
import FilterComponent from './filters/FilterComponent';
import axios from 'axios';

const MainPage = () => {
    const [selectedRows, setSelectedRows] = useState([]);
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filters, setFilters] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async (filters = []) => {
        setIsLoading(true);
        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_application_table_info_ov`, {
                filters,
            });
            setData(result.data.data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        setIsLoading(false);
    };
    const handleFilter = (newFilters) => {
        setFilters(newFilters);
        fetchData(newFilters);
    };

    return (
        <div >
            <TopBar selectedRows={selectedRows} setSelectedRows={setSelectedRows} />
            <div className="page-container">
                <Title />
                <div><FilterComponent data={data} onFilter={handleFilter} /></div>


                {isLoading
                    ? <p>Loading data, please wait...</p>
                    : <ApplicationTable
                        data={data}
                        isLoading={isLoading}
                        selectedRows={selectedRows}
                        setSelectedRows={setSelectedRows}
                    />
                }
            </div>
        </div>
    );
};

export default MainPage;
