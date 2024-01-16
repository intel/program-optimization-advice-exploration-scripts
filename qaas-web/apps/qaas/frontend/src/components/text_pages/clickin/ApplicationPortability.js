

import React from 'react';

import { Link } from 'react-router-dom';

import QaaSValueImage from '../../imgs/qaas_value.png';

export default function ApplicationPortability() {
    return (
        <div className="textPageContainer">
            <h2>
                Application Portability
            </h2>
            <p>
                Porting an application involves several architectures, compilers and runtime libraries.
                The <em>causes</em> of portability failure across architectures may be weak compilers or runtime libraries,
                but <em>detecting</em> failure and clarifying its details can be extremely elusive. In its most vicious form,
                poor portability can be confused with poor performance and go undetected. Poor performance, however,
                can often be quantified and measured in various terms, so in practice, performance must be the starting point.
            </p>


            <p>
                The “performance portability” combination has been a topic promoted by the US department of energy and other government agencies, but as the Wikipedia article states correctly upfront, “there is no universal or agreed upon way to measure it.
                ” It is a qualitative topic, best avoided in favor of two separate quantitative discussions: defining high relative performance on any machine, and then dealing with code porting and performance per system.
            </p>

            <p>
                So, QaaS focuses on each topic separately, quantifying and measuring portability in several ways per system:
            </p>
            <ol>
                <li>Compiling executable code</li>
                <li>Executing the code “successfully,” i.e without a crash.</li>
                <li>Obtaining “correct” results – several definitions of correctness may be acceptable. </li>
                <li>Obtaining relatively high performance. </li>

            </ol>
            <p>
                High performance execution depends on the programmer having chosen and correctly used high-quality runtime libraries – for application-specific algorithms,
                to support parallelism of various types, etc.
            </p>

            <p>
                Runtime libraries can defeat portability on step 2. above – for example the interaction of MPI libraries with applications and architectures.
                QaaS experience shows that Intel MPI is the most portable, whereas MPICH, OpenMPI, and others can be much more difficult to port.
                See examples in text. Ironically, the DOE promotes “performance portability” but confounds portability by supporting the development of several conflicting dialects,
                instead of standardizing MPI.
            </p>
            <p>
                Similarly, step 1 requires a high-quality compiler, per architecture. QaaS has found that there are no universally highest-quality compilers for
                any machine tested – multi-compilation and result comparison is always required for best results, as discussed in the
                {' '}
                <Link className='link'
                    to="/qaas/overview/compiler_comparison"
                >compilation section</Link>
                .
            </p>

            <h2>
                QaaS added value
            </h2>

            <p>
                By making comparative runs, QaaS can be very effective in analyzing portability. Each of the 4 steps outlined above can be dealt with separately in QaaS. Thus, it can help pin down portability issues in detail.
            </p>

            <div className='imageContainer'>
                <img src={QaaSValueImage} alt="QaaSValueImage Description" />
            </div>



        </div>
    );


}

