import React, { useState } from 'react';
import Badge from '@mui/material/Badge';
import { FaBookOpen } from "react-icons/fa";
import SelectedRunsDrawer from './SelectedRunDrawer';
import './css/TopBar.css'
const SelectedRunsBag = ({ selectedRows, setSelectedRows, baseline, setBaseline, setShowGraph }) => {
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);

    const toggleDrawer = () => {
        setIsDrawerOpen(!isDrawerOpen);
    };

    return (
        <>
            <Badge badgeContent={selectedRows.length} color="error" onClick={toggleDrawer}>
                <FaBookOpen className={baseline ? 'top-bar-badge-baseline' : 'top-bar-badge'} />
            </Badge>

            <SelectedRunsDrawer
                isOpen={isDrawerOpen}
                onClose={toggleDrawer}
                selectedRows={selectedRows}
                setSelectedRows={setSelectedRows}
                baseline={baseline}
                setBaseline={setBaseline}
                setShowGraph={setShowGraph}
            />
        </>
    );
};

export default SelectedRunsBag;