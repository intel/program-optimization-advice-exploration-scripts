// DrawerItem.js
import React from 'react';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';

const DrawerItem = ({ level, text, path, children, navigateToSection, selectedItem, hasChildren }) => {
    const isSelected = selectedItem === path;
    return (
        <ListItem>
            <ListItemButton
                className={`level level${level} ${isSelected ? 'highlight-color' : ''} hover-color`}
                onClick={() => navigateToSection(path, children)}
            >
                <ListItemText primary={text} />
                {hasChildren && <ArrowForwardIosIcon fontSize="small" />}
            </ListItemButton>
        </ListItem>
    );
};

export default DrawerItem;
