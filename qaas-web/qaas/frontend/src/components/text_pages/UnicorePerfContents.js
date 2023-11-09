import React from 'react';
import UnicorePerfGFlopsLineGraph from '../graph/line/UnicorePerfGFlopsLineGraph';
import UnicorePerfTable from '../graph/table/UnicorePerfTable';
export default function UnicorePerfContents() {
    return (
        <div className="textPageContainer">
            <h1>Unicore performance comparisons</h1>
            <p>
                Several current unicore systems were run on a set of 7 simple HPC miniapps, all compiled with a good default compiler per machine.
                We summarize the results using basic QaaS views. Fig. uni shows two recent Intel systems (Sapphire Rapids - SPR, and Ice Lake - ICL)
                as well as AWS Graviton G3E and AMD Zen4. The numbers above each point show the ratio of the best to the worst performance of the 4 systems,
                using the color of the winning system. So, the left-most point shows that Graviton 3E is 1.41X faster than ICL for the AMG code.

            </p>
            <p>
                The second unicore view, Fig. utab, gives background information about the codes and systems, together with the numerical perf values plotted in Fig. uni,
                which shows exact Gf values for each machine. In this view, we can see that G3E and Zen4 are within 10% of each other. Both figures illustrate the fact
                that performance leadership and ranking varies a lot across application types and architectures.
            </p>
            <UnicorePerfGFlopsLineGraph />
            <UnicorePerfTable />



        </div>
    );


}