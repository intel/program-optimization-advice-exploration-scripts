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
    'Zen4': '#E2F0CB',
    'G3E': '#C5C6C7',
    'ICLLIGHT': 'rgba(255, 107, 107, 0.5)',
    'SPRLIGHT': 'rgba(137, 207, 240, 0.5)',
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