import React from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import { AiTwotoneDelete } from "react-icons/ai";
import axios from 'axios';
import './css/TopBar.css'
const SelectedRunsDrawer = ({ isOpen, onClose, selectedRows, setSelectedRows }) => {

    const handleFormSubmit = async () => {
        const newWindow = window.open(`/generated?loading=true`, "_blank");

        try {
            const response = await axios.post(`/api/run_comparative_view_for_selected_runs`, selectedRows);
            newWindow.location.href = "/generated?loading=false";
        } catch (error) {
            console.error('Error submitting data:', error);
        }
    };

    const handleUnselect = (index) => {
        setSelectedRows(selectedRows.filter((_, i) => i !== index));
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
        </Drawer>
    );
};

export default SelectedRunsDrawer;