export const INITIAL_FILTERS = [

    {
        text: 'HW & settings',
        id: 'hw_settings',
        children: [
            {
                text: 'Intel',
                id: 'intel',
                children: [
                    {
                        text: 'ICL',
                        id: 'icl',
                        selected: true,
                    },
                ]
            },
        ]
    },
    {
        text: 'Compiler & Flags',
        id: 'compiler_flags',
        children: [
            {
                text: 'GCC',
                id: 'gcc',
                selected: true,
            },
            {
                text: 'ICC',
                id: 'icc',
                selected: true,
            },
            {
                text: 'ICX',
                id: 'icx',
                selected: true,
            },
        ]
    },

    {
        text: 'Code & dataset',
        id: 'code_dataset',
        children: [
            {
                text: 'Miniapp',
                id: 'miniapp',
                children: [
                    {
                        text: 'miniqmc',
                        id: 'miniqmc',
                        selected: true,
                    },
                    {
                        text: 'kripke',
                        id: 'kripke',
                        selected: true,
                    },
                    {
                        text: 'CloverLeaf CXX',
                        id: 'cloverleaf_cxx',
                        selected: true,
                    },
                    {
                        text: 'CloverLeaf FC',
                        id: 'cloverleaf_fc',
                        selected: true,
                    },
                    {
                        text: 'AMG',
                        id: 'amg',
                        selected: true,
                    },
                    {
                        text: 'CoMD',
                        id: 'comd',
                        selected: true,
                    },
                    {
                        text: 'HACCmk',
                        id: 'haccmk',
                        selected: true,
                    },
                ]
            },
            {
                text: 'Realapp',
                id: 'realapp',
                children: [
                    {
                        text: 'gromacs',
                        id: 'gromacs',
                        selected: true,
                    },
                    {
                        text: 'qmcpack',
                        id: 'qmcpack',
                        selected: true,
                    },
                ],
            },

        ]
    },

];
//recursive function to update a box
export const updateFilterSelection = (items, itemId, checked) => {
    return items.map(subItem => {
        if (subItem.id === itemId) {
            return { ...subItem, selected: checked };
        }
        if (subItem.children) {
            return {
                ...subItem,
                children: updateFilterSelection(subItem.children, itemId, checked)
            };
        }
        // no match 
        return subItem;
    });
};


export const getUnselectedFilters = (filters) => {
    let unselected = [];
    const checkChildren = (children) => {
        children.forEach((child) => {
            if (child.selected === false) {
                unselected.push(child.text);
            }
            if (child.children) {
                checkChildren(child.children);
            }
        });
    };
    checkChildren(filters);
    return unselected;
};

export const resetFiltersRecursive = (filters) => {
    return filters.map(filter => {
        const updatedFilter = { ...filter, selected: true };

        if (filter.children && filter.children.length > 0) {
            updatedFilter.children = resetFiltersRecursive(filter.children);
        }

        return updatedFilter;
    });
};