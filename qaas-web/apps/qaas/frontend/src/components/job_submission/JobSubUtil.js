import { createTheme } from '@mui/material/styles';

export const updateState = (setState, path, value) => {
    setState(prevState => {
        // recursively update the state
        const updatePath = (current, path, value) => {
            const [first, ...rest] = path;
            if (rest.length === 0) {
                current[first] = value;
                return current;
            }
            current[first] = updatePath(current[first] || {}, rest, value);
            return current;
        };

        // clone the previous state to avoid direct mutation
        const newState = JSON.parse(JSON.stringify(prevState));
        updatePath(newState, path, value);
        return newState;
    });
};
const getValueByPath = (input, path) => {
    return path.reduce((acc, part) => acc && acc[part], input);
};

export const JOB_SUB_THEME = createTheme({
    palette: {
        primary: {
            main: '#2f889a',
        },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    fontSize: '1rem',
                },
            },
        },
        MuiRadio: {
            styleOverrides: {
                root: {
                    color: '#2f889a',
                    '&.Mui-checked': {
                        color: '#2f889a',
                    },
                    '&:hover': {
                        backgroundColor: 'rgba(47, 136, 154, 0.04)',
                    },
                },
            },
        },
    },
});

export const validateField = (value, field) => {
    let error = '';
    const requiredFields = [];
    if (requiredFields.includes(field) && !value.trim()) {
        error = 'This field is required.';
        return error;
    }

    if (field === 'USER' && !/^\w+$/.test(value)) {
        error = 'Invalid username. Only alphanumeric characters are allowed.';
    }

    return error;
};