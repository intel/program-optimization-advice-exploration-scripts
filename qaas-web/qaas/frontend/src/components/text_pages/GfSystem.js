import React from 'react';

import totGfImage from '../imgs/totGf.png';

export default function GfSystem() {
    return (
        <div className="textPageContainer">
            <h1>C1.3.2 Gf / System</h1>
            <p>
                Here we show the top-performing systems for each app/domain, as measured by total Gf using
                as many processors as meet the efficiency threshold. Fig. totGf shows the number of cores used to exceed the efficiency threshold
                (for any replication factor – weak to strong DK check details see sect. C1.4.1.b). So these numbers exceed those of Fig.
                Gf/cor because of the number of efficiently used processors. This reflects the quality of the architecture
                (especially MHU and NUMA properties) as well as the application and its developer team.  The labels here show the system used, as in Fig. Gf/cor.
                Use colors for arch here, as compiler choice earlier
            </p>
            <div className='imageContainer'>
                <img src={totGfImage} alt="totGf Description" />
            </div>
            <p>
                For more details about these runs, click down (define hierarchy here)
                Note the similarities in ranking between Figs. Gf/core and totGf, however Cloverleaf Ftn shifted to a lower bin in
                Fig. totGf meaning that the parallelism in it was relatively weak (see scalability analysis in Sect //).


            </p>


        </div>
    );


}