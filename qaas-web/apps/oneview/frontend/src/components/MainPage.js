import React, { useState, useEffect, useCallback } from 'react';
import TopBar from './TopBar';
import './css/main.css'
import Title from './Title';
import ApplicationTable from './data/ApplicationTable';
import FilterComponent from './filters/FilterComponent';
import axios from 'axios';
import TotalTimeSpeedupGraph from './graph/TotalTimeSpeedupGraph';
import { INITIAL_FILTERS } from './filters/InitialFilter';
import { Modal } from 'antd';
import AllSpeedupRangeGraph from './graph/AllSpeedupRangeGraph';
import { SelectionProvider } from './contexts/SelectionContext';
const MainPage = () => {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filters, setFilters] = useState(INITIAL_FILTERS);
    const [baseline, setBaseline] = useState(null);
    const [showGraph, setShowGraph] = useState(false);

    useEffect(() => {
        fetchData();
        fetchRunInfo();
    }, []);
    useEffect(() => {
        fetchRunInfo();
    }, [filters.Global['Run Info'].Program.value, filters.Global['Run Info']['Experiment Name'].value]);


    const fetchRunInfo = async () => {
        setIsLoading(true);
        console.log("program", filters.Global['Run Info'].Program.value, "exp name", filters.Global['Run Info']['Experiment Name'].value)
        try {
            const currentFilters = {
                program: filters.Global['Run Info'].Program.value,
                version: filters.Global['Run Info']['Experiment Name'].value,
            };
            const response = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/filter_run_info`, { filters: currentFilters });
            const newFilters = { ...filters };
            newFilters.Global['Run Info'].Program.choices = response.data.programs;
            newFilters.Global['Run Info']['Experiment Name'].choices = response.data.experiment_names;

            setFilters(newFilters); // update the state
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        setIsLoading(false);

    };
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
        fetchData(newFilters);
    };


    //function to not show graph
    const handleOk = () => {
        setShowGraph(false);
    };
    const handleCancel = () => {
        setShowGraph(false);

    };


    if (data.length === 0) {
        return <p>Loading data, please wait...</p>;
    }
    return (
        <SelectionProvider>

            <div>
                <div className="sticky-top">

                    <TopBar baseline={baseline} setBaseline={setBaseline} setShowGraph={setShowGraph} />
                </div>

                <div className="page-container">
                    <Title />
                    <div><FilterComponent data={data} onFilter={handleFilter} filters={filters} setFilters={setFilters} /></div>

                    {isLoading
                        ? <p>Loading data, please wait...</p>
                        :
                        <div>
                            {/* <AllSpeedupRangeGraph application_table_data={data} /> */}
                            <ApplicationTable
                                data={data}

                                baseline={baseline}
                                setBaseline={setBaseline}
                            />
                        </div>
                    }

                    {/* <Modal title="Comparison" open={showGraph} onOk={handleOk} onCancel={handleCancel}>
                    <TotalTimeSpeedupGraph selectedRows={selectedRows} baseline={baseline} open={showGraph} />
                </Modal> */}
                </div>
            </div>
        </SelectionProvider>
    );
};

export default MainPage;
