export const RANGES = ['< 1.1X', '1.1-1.2X', '1.2-1.5X', '1.5-2X', '2-4X', '> 4X'];

export const GENERAL_COLORS = {
    'Win': '#FFABAB',
    'Lose': '#B9FFC9',
};

export const APP_COLORS = {
    'AMG': '#99C1B9',
    'HACC': '#FFEE93',
    'CoMD': '#D4A5A5',
    'ClovF': '#A8E6CF',
    'Miniqmc': '#FDFFAB',
    'Kripke': '#F9C0C0',
    'Clov++': '#B4A7D6',

};

export const COMPILER_COLORS = {
    'ICX': '#FAD2E1',
    'ICC': '#C7CEEA',
    'GCC': '#E3EAA7',
    'TIE': '#FFD3B4',
    'Tie': '#FFD3B4',
};

export const PROCESSOR_COLORS = {
    'ICL': '#FF6B6B',
    'SPR': '#89CFF0',
    'Zen4': '#60d394',
    'G3E': '#FFD700',
    'Intel ICL': '#FF6B6B',
    'Intel SPR': '#89CFF0',
    'AMD Zen4': '#60d394',
    'AWS G3E': '#FFD700'
}

export const PROCESSOR_POINT_SHAPE = {
    'ICL': 'circle',
    'SPR': 'square',
    'Zen4': 'diamond',
    'G3E': 'cross',
    'Intel ICL': 'circle',
    'Intel SPR': 'square',
    'AMD Zen4': 'diamond',
    'AWS G3E': 'cross'
}

export function getProcessorPointStyle(processor) {
    return PROCESSOR_POINT_SHAPE[processor];

}
export function getProcessorColor(processor) {
    return PROCESSOR_COLORS[processor];
}

export function getGeneralColor(type) {
    return GENERAL_COLORS[type];
}

export function getAppColor(app) {
    return APP_COLORS[app];
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
        pad: 4
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
        b: 10,
        t: 10,
        pad: 4
    },
    paper_bgcolor: 'rgba(0,0,0,0)',

    plot_bgcolor: 'rgba(0,0,0,0)',
};