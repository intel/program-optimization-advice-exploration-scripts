import React from 'react';
import UnicorePerfGFlopsLineGraph from '../../graph/line/UnicorePerfGFlopsLineGraph';
import UnicorePerfTable from '../../graph/table/UnicorePerfTable';
import { Link } from 'react-router-dom';
import { useHighlightNavigation } from '../../hooks/useHighlightNavigation';
export default function UnicorePerfContents() {
    useHighlightNavigation();

    return (
        <div className="textPageContainer">
            <h1>Unicore performance comparisons</h1>
            <p>
                Several current unicore systems were used to run on a set of 7 simple HPC miniapps,
                all compiled per machine with a good default compiler. We summarize the results
                using basic QaaS views.

                {' '}<Link className='link'
                    to="/qaas/overview/unicore_performance_comparisons#figuni"
                >Fig. uni</Link>{' '}

                compares 4 systems: two recent Intel systems
                (Sapphire Rapids - SPR, and Ice Lake - ICL) as well as AWS Graviton G3E and AMD Zen4.
                The numbers above each point show the ratio of the best to the worst performance of the
                4 systems, using the color of the winning system. So, the left-most point shows that Graviton
                3E is 1.41X faster than ICL for the AMG code. See here for
                {' '}
                <Link className='def-link'
                    to="/system_config"
                > architectural details </Link>
                of these machines.


            </p>
            <p>
                The second unicore view,
                {' '}<Link className='link'
                    to="/qaas/overview/unicore_performance_comparisons#figutab"
                >Fig. utab</Link>{', '}


                gives background information about the codes and systems,
                together with exact Gf performance values for each machine plotted in Fig. uni. In this view,
                we can see that G3E and Zen4 both have portability (compilation) difficulties on some miniapps. Both figures illustrate the fact
                that performance leadership and ranking varies a lot across application types and architectures.
            </p>
            <div className='multiple-graph-container'>
                <UnicorePerfGFlopsLineGraph />


                <UnicorePerfTable />

            </div>





        </div>
    );


}