import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import { AiTwotoneDelete } from "react-icons/ai";
import axios from 'axios';
import Box from '@mui/material/Box';
import TotalTimeSpeedupGraph from './graph/TotalTimeSpeedupGraph';
import './css/TopBar.css'
import { REACT_APP_API_BASE_URL } from './Constants';
const SelectedRunsDrawer = ({ isOpen, onClose, selectedRows, setSelectedRows, baseline, setBaseline, setShowGraph }) => {

    const handleFormSubmit = async () => {
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const response = await axios.post(`${REACT_APP_API_BASE_URL}/run_comparative_view_for_selected_runs`, selectedRows);
            newWindow.location.href = "#/generated?loading=false";
        } catch (error) {
            console.error('Error submitting data:', error);
        }
    };

    const handleUnselect = (index) => {
        setSelectedRows(selectedRows.filter((_, i) => i !== index));
    };

    const handleBaselineUnselect = () => {
        setBaseline(null);
    };

    const handleGraphButton = () => {
        setShowGraph(true);
        //close drawer so graph is brighter
        onClose()
    };

    //drawer will show the list and compared button would only show if some items are selected
    return (
        <Drawer anchor="right" open={isOpen} onClose={onClose}>

            <List>
                {selectedRows.map((row, index) => (
                    <ListItem key={index}>
                        <ListItemText primary={`Run ${index + 1}: ${row.timestamp}`} />
                        <ListItemSecondaryAction>
                            <AiTwotoneDelete onClick={() => handleUnselect(index)} />
                        </ListItemSecondaryAction>
                    </ListItem>
                ))}
            </List>


            {selectedRows.length > 0 ? (
                <button className="table-action-button" onClick={handleFormSubmit}>
                    Compare Selected Runs
                </button>
            ) : (
                <p className='drawer-no-selection-text'>No items have been selected</p>
            )}


            {baseline ? (
                <div>
                    <Box display="flex" alignItems="center">
                        <p>Baseline: {baseline.timestamp}</p>
                        <AiTwotoneDelete onClick={() => handleBaselineUnselect()} />
                    </Box>


                </div>
            ) : (
                <p className='drawer-no-selection-text'>No baseline have been selected</p>
            )}

            {selectedRows.length > 0 && baseline && (

                <button className="table-action-button" onClick={handleGraphButton}>
                    Show Hardware Comparison
                </button>
            )}

        </Drawer>


    );
};

export default SelectedRunsDrawer;