import React, { useState } from 'react';
import TopBar from './TopBar';
import './css/main.css'
import Title from './Title';
import ApplicationTable from './data/ApplicationTable';

const MainPage = () => {
    const [selectedRows, setSelectedRows] = useState([]);

    return (
        <div className="parent-container">
            <TopBar selectedRows={selectedRows} setSelectedRows={setSelectedRows} />
            <Title />

            <ApplicationTable selectedRows={selectedRows} setSelectedRows={setSelectedRows} />

        </div>
    );
};

export default MainPage;
