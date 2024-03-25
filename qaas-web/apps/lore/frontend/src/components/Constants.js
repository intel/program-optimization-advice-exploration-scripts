export const REACT_APP_API_BASE_URL = '/lore/api'

export const RANGES = ['0-0.33', '0.33-0.5', '0.5-0.85', '0.85-1.0', '1.0-1.15', '1.15-2', '2-3', '3-4', '>4'];
export const DEFAULT_COLOR_SCHEME = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F', '#B276B2', '#DECF3F', '#F15854'];
export function assignColorsToRanges(ranges) {
    return ranges.map((_, index) => DEFAULT_COLOR_SCHEME[index % DEFAULT_COLOR_SCHEME.length]);
};

export const COMPILER_COLORS = {
    'ICX': '#FAA43A',
    'icx': '#FAA43A',

    'ICC': 'rgba(255, 99, 132, 0.6)',
    'icc': 'rgba(255, 99, 132, 0.6)',

    'GCC': 'rgba(54, 162, 235, 0.6)',
    'gcc': 'rgba(54, 162, 235, 0.6)',

    'TIE': '#FFD3B4',
    'Tie': '#FFD3B4',
};
export function getCompilerColor(compiler) {
    return COMPILER_COLORS[compiler];
}

export const SPEEDUP_R_COLOR = 'rgba(255, 99, 132, 0.6)';
export const SPEEDUP_M_COLOR = 'rgba(54, 162, 235, 0.6)';
