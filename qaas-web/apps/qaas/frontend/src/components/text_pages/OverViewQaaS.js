import React from 'react';
import { Link } from 'react-router-dom';
import QaaSValueImage from '../imgs/qaas_value.png';

export default function OverViewQaaS() {
    return (
        <div className="textPageContainer">
            <h1>Overview of QaaS: Summaries of past runs   </h1>
            <p>
                This section uses key views of performance results to orient new QaaS users.

                See {' '}
                <Link className='link'
                    to="/qaas/overview/how_to_improve_performance"
                > philosophical background </Link>

                else proceed with the discussion of QaaS typical results. As examples, QaaS can search across architectures and compilers to find the best performance
                results per code, and we present unicore, compiler and multicore comparisons.


            </p>




            <h2>Unicore performance comparisons</h2>
            <p>
                We begin with

                <Link className='link'
                    to="/qaas/overview/unicore_performance_comparisons"
                >  introductory unicore results</Link>,
                because they reveal many basic ideas that can be useful in understanding HPC multicore
                results on the fastest parallel machines available. This is also an introduction to the QaaS service of Section 2
                (Automatic Application Improvement).

            </p>

            <h2>Compiler Comparison</h2>
            <p>
                Most computers have multiple processors/cores today, and applications can take advantage of them in various ways.
                {' '}
                <Link className='link'
                    to="/qaas/overview/compiler_comparison"
                >Compilers</Link>
                {' '}
                play larger roles as computations become more complex, so we continue the discussion of these topics here.
            </p>

            <h2>
                Multicore performance comparisons
            </h2>

            <p>
                This extends the unicore introduction above, and introduces some
                <Link className='link'
                    to="/qaas/overview/multicore_performance_comparisons"
                > introductory multicore system comparison metrics.</Link>
            </p>

            <h2>
                Application Portability
            </h2>
            <p>
                <Link className='link'
                    to="/qaas/overview/application_portability"
                >Application portability</Link> {' '}
                is a key aspect of computational quality, it depends on the openness and quality of compilers, runtime libraries, and available hardware systems.
                We will treat application portability and performacne as two distinct subjects.


            </p>


            <h2>
                Next steps
            </h2>


            <p>
                Above, we have covered unicore and MP architectural basics, as well as compilation basics. We used a few simple mini-applications to show
                some factual statements about these computations. We have not given many details about the codes, how QaaS works,
                or why it can be regarded as a reliable tool.

                <div className='container-next-to-paragraph'>
                    <p>If QaaS judges a computation as high-quality, it is. <br />
                        → Believe it and move on. </p>
                </div>
                The QaaS goal is to find performance improvements automatically,
                and show users how to take advantage of our findings. At a high level, results are more important than detailed explanations.
                Furthermore, because QaaS contains many tools, explanations can become intricate.
            </p>

            <p>
                This brief introduction to QaaS has covered many topics that are expanded to fuller explanations in the Broad QaaS Introduction [BQI].
                If your main interest is in submitting your own job to run, you may proceed to Section 2
                {' '}
                <Link className='link'
                    to="/input"
                >click job submission</Link>
                .
                {' '}
                <Link className='link'
                    to="/qaas/cq_overview"
                >Broad QaaS Introduction</Link>
                {' '}
                should serve as a reference document to further questions that may arise about QaaS analyses, as you proceed.
                Otherwise for a continuation of the QaaS discussion, BQI will expand on many of the topics and include whole applications,
                more systems, and some performance explanations.

            </p>











        </div>
    );


}