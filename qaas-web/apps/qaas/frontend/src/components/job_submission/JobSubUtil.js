
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