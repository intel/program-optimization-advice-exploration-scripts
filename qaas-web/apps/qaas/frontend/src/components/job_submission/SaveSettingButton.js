import React, { useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { useStepper } from '../contexts/StepperSettingContext';
const SaveSettingButton = ({ input }) => {
    const [filename, setFilename] = useState('defaultFilename.json');
    const [isDialogOpen, setDialogOpen] = useState(false);
    const { fetchSettings } = useStepper();

    const handleSaveSetting = async () => {
        try {
            await axios.post(`${process.env.REACT_APP_API_BASE_URL}/save_input_json`, {
                json: input,
                filename: filename,
            });
            // close the dialog after saving
            setDialogOpen(false);
            //force fetch settings to update the context
            await fetchSettings(true);
        } catch (error) {
            console.error('Error saving setting:', error);
        }
    };

    const handleOpenDialog = () => {
        setDialogOpen(true);
    };

    const handleCloseDialog = () => {
        setDialogOpen(false);
    };

    return (
        <div>
            <Button onClick={handleOpenDialog}>
                Save Current Setting
            </Button>
            <Dialog open={isDialogOpen} onClose={handleCloseDialog}>
                <DialogTitle>Save Setting</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="filename"
                        label="Filename"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={filename}
                        onChange={(e) => setFilename(e.target.value)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancel</Button>
                    <Button onClick={handleSaveSetting}>Save</Button>
                </DialogActions>
            </Dialog>
        </div>
    );
};

export default SaveSettingButton;
