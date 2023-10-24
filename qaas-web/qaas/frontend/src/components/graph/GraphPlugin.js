export const BarTextPlugin = {
    id: 'barText',
    afterDraw: (chart) => {
        const ctx = chart.ctx;
        ctx.font = "9px Verdana";
        chart.data.datasets.forEach((dataset, datasetIndex) => {
            const meta = chart.getDatasetMeta(datasetIndex);
            if (meta.hidden) return;

            ctx.fillStyle = '#FFFFFF';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            meta.data.forEach((bar, index) => {
                const label = dataset.barText && dataset.barText[index];
                if (label) {
                    ctx.fillText(label, bar.x, bar.y + bar.height / 2); //middle
                }
            });
        });
    }
};