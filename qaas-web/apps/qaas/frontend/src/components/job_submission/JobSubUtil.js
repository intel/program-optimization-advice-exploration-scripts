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
        MuiStepIcon: {
            styleOverrides: {
                root: {
                    fontSize: '36px',
                    fontWeight: 'bold',

                    '&.MuiStepIcon-active': {
                        color: '#2f889a',
                    },
                    '&.MuiStepIcon-completed': {
                        color: '#2f889a',
                    },
                },
            },
        },
        MuiStepLabel: {
            styleOverrides: {
                label: {
                    fontSize: '1.25em',

                    color: 'rgba(0, 0, 0, 0.87)',
                },
            },
        }
    },
});

export const OPTIONAL_BLOCK_THEME = createTheme({
    palette: {
        primary: {
            main: '#4da6b3',
        },
        text: {
            primary: '#a3a3a3',
        },
    },
    components: {
        MuiRadio: {
            styleOverrides: {
                root: {
                    color: '#83c5be',
                    '&.Mui-checked': {
                        color: '#83c5be',
                    },
                    '&:hover': {
                        backgroundColor: 'rgba(77, 166, 179, 0.04)',
                    },
                },
            },
        },
        MuiSelect: {
            styleOverrides: {
                select: {
                    color: '#a3a3a3',
                },
            },
        },
        MuiInputBase: {
            styleOverrides: {
                input: {
                    color: '#a3a3a3',
                },
            },
        },
        MuiInputLabel: {
            styleOverrides: {
                root: {
                    color: '#a3a3a3',
                    '&.Mui-focused': {
                        color: '#a3a3a3',
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