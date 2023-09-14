// export default MainPage;
import React, { useState, useEffect } from 'react';
import TopBar from './TopBar';
import './css/main.css'
import Title from './Title';
import ApplicationTable from './data/ApplicationTable';
import FilterComponent from '../components/filters/FilterComponent'
import axios from 'axios';
import AllLoopsSpeedupRangeGraph from './graphs/AllLoopsSpeedupRangeGraph';
const MainPage = () => {
    const [data, setData] = useState([]);
    const [filteredData, setFilteredData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filters, setFilters] = useState([]);
    // State for handling page changes
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(10);
    const [totalRecords, setTotalRecords] = useState(0);

    //get initial data
    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async (page = 0, pageSize = 10) => {
        setIsLoading(true);
        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_application_table_info_lore`, { page, pageSize });
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
        //  reset to page 0 when filters are applied
        setPage(0);
        filterData(page, pageSize, newFilters);
    };

    const filterData = async (page = 0, pageSize = 10, filters) => {
        const filterParams = {};
        filters.forEach(filter => {
            filterParams[filter.type] = `${filter.operator}_${filter.value}`;
        });

        setIsLoading(true);
        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_application_table_info_lore`, { page, pageSize, filters: filterParams });
            setData(result.data.data);
            setFilteredData(result.data.data);
            setTotalRecords(result.data.totalCount); // replace `totalCount` with the actual property name
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        setIsLoading(false);
    };

    const handlePageChange = (newPage) => {
        setPage(newPage);
        fetchData(newPage, pageSize);
    };

    const handlePageSizeChange = (newPageSize) => {
        setPageSize(newPageSize);
        fetchData(page, newPageSize);
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
                    page={page}
                    pageSize={pageSize}
                    onPageChange={handlePageChange}
                    onPageSizeChange={handlePageSizeChange}
                    numPages={Math.ceil(totalRecords / pageSize)}

                />

            </div>
        </div>
    );
};

export default MainPage;
