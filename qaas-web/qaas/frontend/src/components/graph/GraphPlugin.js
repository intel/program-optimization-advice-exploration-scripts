export const BarTextPlugin = {
    id: 'barText',
    afterDraw: (chart) => {
        const ctx = chart.ctx;
        ctx.save();
        ctx.font = "9px Verdana";
        chart.data.datasets.forEach((dataset, datasetIndex) => {
            const meta = chart.getDatasetMeta(datasetIndex);
            if (meta.hidden) return;

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            meta.data.forEach((bar, index) => {
                const label = dataset.barText && dataset.barText[index];
                if (label) {
                    ctx.fillText(label, bar.x, bar.y + bar.height / 2); //middle
                }
            });
        });
        ctx.restore();
    }
};

// helper function to calculate min and max values for a given label index
const calculateMinMaxForLabelIndex = (datasets, labelIndex) => {
    let maxValue = -Infinity;
    let maxValIndex = -1;
    let minVal = Infinity;
    let minValIndex = -1;

    datasets.forEach((dataset, datasetIndex) => {
        const value = dataset.data[labelIndex];
        if (value !== null) {
            if (value > maxValue) {
                maxValue = value;
                maxValIndex = datasetIndex;
            }
            if (value < minVal) {
                minVal = value;
                minValIndex = datasetIndex;
            }
        }
    });

    return { maxValue, maxValIndex, minVal, minValIndex };
};
const drawRatioLabel = (chart, ratio, labelIndex, maxValue, dataset, xAxis, yAxis) => {
    if (ratio !== null && dataset) {
        const ctx = chart.ctx;
        ctx.fillStyle = dataset.borderColor || 'black'; // use the borderColor of the dataset
        const x = xAxis.getPixelForValue(chart.data.labels[labelIndex]) - 15;
        const y = yAxis.getPixelForValue(maxValue) - 15; // offset from the top of the max value
        ctx.fillText(`${ratio.toFixed(2)}`, x, y);
    }
};
export const minMaxLineLabelPlugin = {
    id: 'minMax',
    afterDraw: (chart) => {
        const ctx = chart.ctx;
        const xAxis = chart.scales['x'];
        const yAxis = chart.scales['y'];

        chart.data.labels.forEach((label, labelIndex) => {
            const { maxValue, maxValIndex, minVal } = calculateMinMaxForLabelIndex(chart.data.datasets, labelIndex);

            // calculate min/max difference if min and max values are found

            if (maxValIndex !== -1) {
                const dataset = chart.data.datasets[maxValIndex];

                const percentDiff = maxValue / minVal;
                drawRatioLabel(chart, percentDiff, labelIndex, maxValue, dataset, xAxis, yAxis);
            }
        });
    }
};

export const minMaxMultipleLineLabelPlugin = {
    id: 'minMaxMultiple',
    afterDraw: (chart) => {
        const ctx = chart.ctx;
        const xAxis = chart.scales['x'];
        const yAxis = chart.scales['y'];

        chart.data.labels.forEach((label, labelIndex) => {
            const totalDatasets = chart.data.datasets.filter(dataset => !dataset.label.includes('per-core'));
            const perCoreDatasets = chart.data.datasets.filter(dataset => dataset.label.includes('per-core'));

            const { maxValue: totalMaxValue, maxValIndex: totalMaxValIndex, minVal: totalMinVal } = calculateMinMaxForLabelIndex(totalDatasets, labelIndex);
            const { maxValue: perCoreMaxValue, maxValIndex: perCoreMaxValIndex, minVal: perCoreMinVal } = calculateMinMaxForLabelIndex(perCoreDatasets, labelIndex);

            // rraw the ratio labels
            if (totalMaxValIndex !== -1) {
                const totalDataset = totalDatasets[totalMaxValIndex];

                const totalRatio = totalMaxValue / totalMinVal;
                drawRatioLabel(chart, totalRatio, labelIndex, totalMaxValue, totalDataset, xAxis, yAxis);
            }
            if (perCoreMaxValIndex !== -1) {
                const perCoreDataset = perCoreDatasets[perCoreMaxValIndex];

                const perCoreRatio = perCoreMaxValue / perCoreMinVal;
                drawRatioLabel(chart, perCoreRatio, labelIndex, perCoreMaxValue, perCoreDataset, xAxis, yAxis);
            }
        });
    }
};