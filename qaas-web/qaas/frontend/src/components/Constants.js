export const RANGES = ['< 1.1X', '1.1-1.2X', '1.2-1.5X', '1.5-2X', '2-4X', '> 4X'];
export const DEFAULT_COLOR_SCHEME = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F', '#B276B2', '#DECF3F', '#F15854'];
export function categorizeSpeedup(speedup) {
    if (speedup < 1.1) return '< 1.1X';
    if (speedup < 1.2) return '1.1-1.2X';
    if (speedup < 1.5) return '1.2-1.5X';
    if (speedup < 2) return '1.5-2X';
    if (speedup < 4) return '2-4X';
    return '> 4X';
}
