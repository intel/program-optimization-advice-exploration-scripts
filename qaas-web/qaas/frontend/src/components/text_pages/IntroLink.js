import React from 'react';
import { Link } from 'react-router-dom';
export default function IntroLink() {
    return (
        <p>
            This brief introduction to QaaS has covered many topics that are expanded to fuller explanations in the
            Broad QaaS Introduction [BQI].
            If your main interest is in submitting your own job to run, you may proceed to Section 2
            {' '}
            <Link className='link'
                to="/input"
            > click job submission</Link>
            .
            {' '}
            The
            <Link className='link'
                to="/qaas/cq_overview"
            >   Broad QaaS Introduction </Link>
            {' '}
            should serve as a reference document to further questions that may
            arise about QaaS analyses, as you proceed.
        </p>
    )

}