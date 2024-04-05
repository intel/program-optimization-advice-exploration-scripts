import Dropdown from './Dropdown';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { REACT_APP_API_BASE_URL } from './Constants';
function HardwareDropdown({ current_src_loop_id }) {


  const [options, setOptions] = useState([]);

  useEffect(() => {
    axios.post(`${REACT_APP_API_BASE_URL}/get_lore_cpu_info_for_specific_loop`, {
      current_src_loop_id
    })
      .then(response => {
        setOptions(response.data);
      })
      .catch(error => {
        console.error('Error fetching options:', error);
      });
  }, []);

  return (
    <Dropdown options={options} />
  );
}

export default HardwareDropdown;