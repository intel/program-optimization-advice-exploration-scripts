export const RANGES = ['< 1.1X', '1.1-1.2X', '1.2-1.5X', '1.5-2X', '2-4X', '> 4X'];

export const GENERAL_COLORS = {
    'Win': '#B9FFC9',
    'Lose': '#FFABAB',
    'YellowHighlight': '#FFFF00',
    'BlueHighlight': '#ADD8E6'
};

export const APP_COLORS = {
    'AMG': '#99C1B9',
    'HACC': '#FFEE93',
    'CoMD': '#D4A5A5',
    'ClovF': '#A8E6CF',
    'Miniqmc': '#FDFFAB',
    'Kripke': '#F9C0C0',
    'Clov++': '#B4A7D6',
    'Gromcas': '#A0D9D9',
    'Qmcpack': '#FFD1BA',

};

export var COMPILER_COLORS = {
    'ICX': '#FAD2E1',
    'ICC': '#C7CEEA',
    'GCC': '#E3EAA7',
    'TIE': '#FFD3B4',
    'Tie': '#FFD3B4',
};

export var PROCESSOR_COLORS = {
    'ICL': '#FF6B6B',
    'SPR': '#89CFF0',
    'Zen4': '#60d394',
    'G3E': '#FFD700',
    'Intel ICL': '#FF6B6B',
    'Intel SPR': '#89CFF0',
    'AMD Zen4': '#60d394',
    'AWS G3E': '#FFD700'
}

export var PROCESSOR_POINT_SHAPE = {
    'ICL': 'circle',
    'SPR': 'square',
    'Zen4': 'diamond',
    'G3E': 'cross',
    'Intel ICL': 'circle',
    'Intel SPR': 'square',
    'AMD Zen4': 'diamond',
    'AWS G3E': 'cross'
}
var APP_NAME_MAP = {
    'amg': 'AMG',
    'AMG': 'AMG',
    'Amg': 'AMG',
    'haccmk': 'HACC',
    'HACCmk': 'HACC',
    'HACC': 'HACC',
    'comd': 'CoMD',
    'CoMD': 'CoMD',
    'cloverleaf cxx': 'Clov++',
    'CloverLeaf CXX': 'Clov++',
    'CloverLeaf1.4-CXX': 'Clov++',
    'cloverleaf fc': 'ClovF',
    'CloverLeaf FC': 'ClovF',
    'CloverLeaf1.3-FC': 'ClovF',
    'miniqmc': 'Miniqmc',
    'Miniqmc': 'Miniqmc',
    'kripke': 'Kripke',
    'Kripke': 'Kripke',
    'gromcas': 'Gromcas',
    'Gromcas': 'Gromcas',
    'qmcpack': 'Qmcpack',
    'Qmcpack': 'Qmcpack',
};



export function getProcessorPointStyle(processor) {
    return PROCESSOR_POINT_SHAPE[processor];

}
export function getProcessorColor(processor) {
    return PROCESSOR_COLORS[processor];
}

export function getGeneralColor(type) {
    return GENERAL_COLORS[type];
}
export function getAppName(app) {
    return APP_NAME_MAP[app] || app;
}

export function getAppColor(app) {
    const correct_app_name = APP_NAME_MAP[app] || app;
    return APP_COLORS[correct_app_name];
}
export function categorizeSpeedup(speedup) {
    if (speedup < 1.1) return '< 1.1X';
    if (speedup < 1.2) return '1.1-1.2X';
    if (speedup < 1.5) return '1.2-1.5X';
    if (speedup < 2) return '1.5-2X';
    if (speedup < 4) return '2-4X';
    return '> 4X';
}


export function getCompilerColor(compiler) {
    return COMPILER_COLORS[compiler];
}
export function categorizeSpeedupDynamic(speedup, leftMostBin) {
    if (speedup < leftMostBin) return `< ${leftMostBin}X`;
    if (speedup < 1.2) return `${leftMostBin}-1.2X`;
    if (speedup < 1.5) return '1.2-1.5X';
    if (speedup < 2) return '1.5-2X';
    if (speedup < 4) return '2-4X';
    return '> 4X';
}

export function categorizeIntoBin(dataPoint, bins) {
    let foundBin = null;

    bins.forEach(bin => {
        //remove all x or X
        const cleanBin = bin.replace(/[Xx]/g, '');
        if (cleanBin.includes('<')) {
            //  '<number' 
            const max = parseFloat(cleanBin.substring(1));
            if (dataPoint < max) {
                foundBin = bin;
            }
        } else if (cleanBin.includes('-')) {
            //  'start-end' 
            const [start, end] = cleanBin.split('-').map(Number);

            if (dataPoint >= start && dataPoint < end) {
                foundBin = bin;
            }
        } else if (cleanBin.includes('tie')) {
            //  'tie' 
            const tieBinUpperBound = parseFloat(bins[1].split('-')[0]);

            if (dataPoint < tieBinUpperBound) {
                foundBin = bin;
            }
        } else if (cleanBin.includes('>')) {
            //  '>' 
            const min = parseFloat(cleanBin.substring(1));
            if (dataPoint > min) {
                foundBin = bin;
            }

        }
    });

    return foundBin || 'out of range';
}

export const plotStyle = {
    family: "'Lato', Calibri, Arial, sans-serif",
    titleFontSize: '18px',
    gridcolor: '#CCCCCC',
};

export const baseLineLayout = {
    autosize: true,

    legend: {
        x: 0.2,
        xanchor: 'center',
        y: 0.9,
        yanchor: 'top',
        orientation: 'v'
    },
    margin: {
        l: 40,
        r: 40,
        b: 50,
        t: 0,
    },
    xaxis: {
        font: {
            family: plotStyle.fontFamily,
        },
    },
    yaxis: {
        font: {
            family: plotStyle.fontFamily,
        },
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
};

export const baseHistogramLayout = {
    bargap: 0, // no space between bars
    xaxis: {
        font: {
            family: plotStyle.fontFamily,
        },
    },
    yaxis: {
        font: {
            family: plotStyle.fontFamily,
        },
    },
    margin: {
        l: 40,
        r: 40,
        b: 20,
        t: 0,
    },
    paper_bgcolor: 'rgba(0,0,0,0)',

    plot_bgcolor: 'rgba(0,0,0,0)',
};

export function formatValue(value) {
    if (typeof value === 'number') {
        if (Number.isInteger(value)) {
            return value;
        } else {
            return value.toFixed(2);
        }
    } else if (value === null || value === undefined) {
        return 'NA';
    } else {
        return value;
    }
}