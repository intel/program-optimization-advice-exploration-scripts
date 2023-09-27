import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import minitopImage from '../imgs/minitop.png';
export default function CQOverviewPerformance() {
    return (
        <div className="textPageContainer">
            <h1>C1.1 Performance vs. compilers</h1>
            <p>
                The overall results for 7 miniapps on <Link to="/system_config/ice_lake">Intel Ice Lake </Link>are shown in
                <div className='imageContainer'>
                    <img src={minitopImage} alt="Minitop Description" />
                </div>
            </p>

            <p>
                From the viewpoint of winning most, ICX is best. But from the viewpoint of losing least, ICC is best.
                Because we only have 7 miniapps, the table can be regarded as preliminary with only small variations among all 3 compilers.
                Overall results for numerical libraries are shown in Table libtop.
            </p>

        </div>
    );


}