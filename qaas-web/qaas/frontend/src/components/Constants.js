export const RANGES = ['< 1.1X', '1.1-1.2X', '1.2-1.5X', '1.5-2X', '2-4X', '> 4X'];
export const DEFAULT_COLOR_SCHEME = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F', '#B276B2', '#DECF3F', '#F15854'];
// export const DEFAULT_COLOR_SCHEME = [
//     '#A8A8A8', // Pastel Gray
//     '#A1CFE8', // Pastel Blue
//     '#FFD1A1', // Pastel Orange
//     '#A8D5BA', // Pastel Green
//     '#F7BAD4', // Pastel Pink
//     '#D4B16A', // Pastel Gold
//     '#D1A1D1', // Pastel Purple
//     '#F7E07E', // Pastel Yellow
//     '#F7A4A5'  // Pastel Red
// ];
export function categorizeSpeedup(speedup) {
    if (speedup < 1.1) return '< 1.1X';
    if (speedup < 1.2) return '1.1-1.2X';
    if (speedup < 1.5) return '1.2-1.5X';
    if (speedup < 2) return '1.5-2X';
    if (speedup < 4) return '2-4X';
    return '> 4X';
}
export const COMPILER_COLORS = {
    'ICX': DEFAULT_COLOR_SCHEME[0],
    'ICC': DEFAULT_COLOR_SCHEME[1],
    'GCC': DEFAULT_COLOR_SCHEME[2],
    'TIE': DEFAULT_COLOR_SCHEME[3]
};
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