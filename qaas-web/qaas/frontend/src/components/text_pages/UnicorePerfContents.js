import React from 'react';
import UnicorePerfGFlopsLineGraph from '../graph/line/UnicorePerfGFlopsLineGraph';
import UnicorePerfTable from '../graph/table/UnicorePerfTable';
import { Link } from 'react-router-dom';
import IntroLink from './IntroLink';
export default function UnicorePerfContents() {
    return (
        <div className="textPageContainer">
            <h1>Unicore performance comparisons</h1>
            <p>
                Several current unicore systems were run on a set of 7 simple HPC miniapps,
                all compiled per machine with a good default compiler. We summarize the results
                using basic QaaS views. Fig. uni compares 4 systems: two recent Intel systems
                (Sapphire Rapids - SPR, and Ice Lake - ICL) as well as AWS Graviton G3E and AMD Zen4.
                The numbers above each point show the ratio of the best to the worst performance of the
                4 systems, using the color of the winning system. So, the left-most point shows that Graviton
                3E is 1.41X faster than ICL for the AMG code. For architectural details of these machines,
                {' '}
                <Link className='link'
                    to="/system_config"
                > click here </Link>
                .


            </p>
            <p>
                The second unicore view, Fig. utab, gives background information about the codes and systems,
                together with exact Gf performance values for each machine plotted in Fig. uni. In this view,
                we can see that G3E and Zen4 both have portability(compilation) difficulties on some miniapps. Both figures illustrate the fact
                that performance leadership and ranking varies a lot across application types and architectures.
            </p>
            <div className='multiple-graph-container'>
                <UnicorePerfGFlopsLineGraph />
                <UnicorePerfTable />
            </div>





        </div>
    );


}