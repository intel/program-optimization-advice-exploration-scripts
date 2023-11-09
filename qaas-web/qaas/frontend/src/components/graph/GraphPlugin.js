import { getProcessorColor } from "../Constants";
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

export const multicorePerformanceHtmlLegendPlugin = {
    id: "htmlLegend",
    afterUpdate(chart) {
        //  legend items
        const legendItems = [
            { text: 'ICL total GFlops', lineStyle: 'solid', color: getProcessorColor('ICL') },
            { text: 'SPR total GFlops', lineStyle: 'solid', color: getProcessorColor('SPR') },
            { text: 'ICL per-core GFlops', lineStyle: 'dashed', color: getProcessorColor('ICL') },
            { text: 'SPR per-core GFlops', lineStyle: 'dashed', color: getProcessorColor('SPR') }
        ];

        // clear existing legend
        const legendContainer = document.getElementById("js-legend");
        legendContainer.innerHTML = '';

        const ul = document.createElement("ul");
        ul.style.listStyleType = 'none';
        ul.style.margin = 0;
        ul.style.padding = 0;

        legendItems.forEach((legendItem) => {
            const li = document.createElement("li");
            li.style.alignItems = 'center';
            li.style.cursor = 'pointer';
            li.style.display = 'flex';
            li.style.flexDirection = 'row';
            li.style.marginBottom = '5px';

            const boxSpan = document.createElement("span");
            boxSpan.style.display = 'inline-block';
            boxSpan.style.width = '20px';
            boxSpan.style.height = '20px';
            boxSpan.style.marginRight = '10px';
            boxSpan.style.position = 'relative';

            //line style
            if (legendItem.lineStyle === 'dashed') {
                boxSpan.style.borderBottom = `3px dashed ${legendItem.color}`;

            } else {
                boxSpan.style.borderBottom = `3px solid ${legendItem.color}`;
            }
            boxSpan.style.bottom = '9px'; //move line up 

            const shapeSpan = document.createElement("span");
            shapeSpan.style.display = 'block';
            shapeSpan.style.position = 'absolute';
            shapeSpan.style.bottom = '0';
            shapeSpan.style.left = '50%';
            shapeSpan.style.transform = 'translateX(-50%)';

            //  specific shapes based on the processor type
            if (legendItem.text.includes('ICL')) {

                shapeSpan.style.width = '6px';
                shapeSpan.style.height = '6px';
                shapeSpan.style.borderRadius = '50%';  //  circle
                shapeSpan.style.bottom = '-6px'; //move shapd down
                shapeSpan.style.border = `2px solid ${legendItem.color}`;
                shapeSpan.style.backgroundColor = 'transparent';
            } else if (legendItem.text.includes('SPR')) {
                // Create the larger triangle
                shapeSpan.style.width = '0';
                shapeSpan.style.height = '0';
                shapeSpan.style.borderLeft = '7px solid transparent'; // Width of the triangle
                shapeSpan.style.borderRight = '7px solid transparent'; // Width of the triangle
                shapeSpan.style.borderBottom = `10px solid ${legendItem.color}`; // Height and color of the triangle
                shapeSpan.style.bottom = '-10px';
                shapeSpan.style.transform = 'translateX(-50%) translateY(-6px)';

                // Create an inner triangle for the "transparent" part
                const innerShapeSpan = document.createElement("span");
                innerShapeSpan.style.width = '0';
                innerShapeSpan.style.height = '0';
                innerShapeSpan.style.borderLeft = '5px solid transparent'; // Width of the inner triangle
                innerShapeSpan.style.borderRight = '5px solid transparent'; // Width of the inner triangle
                innerShapeSpan.style.borderBottom = `10px solid white`; // Height and background color of the triangle (should be the color of your chart's background)
                innerShapeSpan.style.position = 'absolute';
                innerShapeSpan.style.top = '2px'; // Positioning the inner triangle inside the larger one
                innerShapeSpan.style.left = '50%';
                innerShapeSpan.style.transform = 'translateX(-50%) translateY(-100%)'; // Ensuring it stays centered

                // Append the inner triangle to the outer triangle's span
                shapeSpan.appendChild(innerShapeSpan);
            }

            boxSpan.appendChild(shapeSpan); // add the shape to the box
            li.appendChild(boxSpan);

            const textNode = document.createTextNode(legendItem.text);
            li.appendChild(textNode);

            ul.appendChild(li);
        });

        // add the custom legend to the container
        legendContainer.appendChild(ul);
    }
};
