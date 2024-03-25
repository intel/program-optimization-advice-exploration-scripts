// export default MainPage;
import React, { useState, useEffect } from 'react';
import TopBar from './TopBar';
import './css/main.css'
import Title from './Title';
import ApplicationTable from './data/ApplicationTable';
import FilterComponent from '../components/filters/FilterComponent'
import axios from 'axios';
import { REACT_APP_API_BASE_URL } from './Constants';
import AllLoopsSpeedupRangeGraph from './graphs/AllLoopsSpeedupRangeGraph';
const MainPage = () => {
    const [data, setData] = useState([]);
    const [filteredData, setFilteredData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filters, setFilters] = useState([]);
    // State for handling page changes
    const [totalRecords, setTotalRecords] = useState(0);

    //get initial data
    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const result = await axios.post(`${REACT_APP_API_BASE_URL}/get_application_table_info_lore`, {});
            setData(result.data.data);
            setFilteredData(result.data.data);
            setTotalRecords(result.data.totalCount); // replace `totalCount` with the actual property name
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        setIsLoading(false);
    };

    const handleFilter = (newFilters) => {
        setFilters(newFilters);
        filterData(newFilters);
    };

    const filterData = async (filters) => {
        const filterParams = {};
        filters.forEach(filter => {
            filterParams[filter.type] = `${filter.operator}_${filter.value}`;
        });

        setIsLoading(true);
        try {
            const result = await axios.post(`${REACT_APP_API_BASE_URL}/get_application_table_info_lore`, { filters: filterParams });
            setData(result.data.data);
            setFilteredData(result.data.data);
            setTotalRecords(result.data.totalCount); // replace `totalCount` with the actual property name
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        setIsLoading(false);
    };




    return (
        <div>
            <TopBar />
            <div className='page-container'>
                <Title text="List of Benchmarks and Workloads" />
                {/* The filter component */}
                <FilterComponent data={data} onFilter={handleFilter} />
                <AllLoopsSpeedupRangeGraph />
                <ApplicationTable
                    data={filteredData}
                    isLoading={isLoading}


                />

            </div>
        </div>
    );
};

export default MainPage;
