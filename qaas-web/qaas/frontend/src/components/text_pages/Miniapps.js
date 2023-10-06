import React from 'react';

import bestcompImage from '../imgs/bestcomp.png';
import appGainImage from '../imgs/appgain.png';
import { Link } from 'react-router-dom';

export default function Miniapps() {
    return (
        <div className="textPageContainer">
            <h1>C1.1.1 Miniapps</h1>
            <p>
                The overall QaaS results for 7 miniapps run on Intel Ice Lake [Yue reference syst def] are discussed here.
                First the best compiler, then the benefits of QaaS are explained. The best compiler per miniapp is simply the
                compiler for which QaaS found a flag setting that beat all others; 48 cases were tested here –
                3 compilers with 16 flag settings each, see Fig. bestcomp.
            </p>
            <div className='imageContainer'>
                <img src={bestcompImage} alt="BestComp Description" />
            </div>

            <p>
                A.    At a high level, ISVs and multi-app developers, or CSPs and computer managers,
                are mostly interested in outcomes denominated in numbers of codes. Here we use 7 miniapps,
                and the QaaS benefits can be summarized (see Table appgain), as 2 ties, and various numbers of codes with up to more than 4X performance gains.

            </p>
            <div className='imageContainer'>
                <img src={appGainImage} alt="appGain Description" />
            </div>

            <p>
                For more details about the wins and losses of each compiler,
                see Section
                {' '}
                <Link
                    to="/compiler_details"

                >C.1.1.1 A </Link>
                {' '}
                or continue to
                {' '}
                <Link to="/apps">C.1.1.2 </Link>
                {' '}
                for similar discussions about applications.
            </p>





        </div>
    );


}