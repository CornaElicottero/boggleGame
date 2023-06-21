import React from 'react';


const CheckWord = (word) => {
    fetch(`http://10.13.13.56:8000/in_dictionary?word=${word}`)
      .then(response => response.json())
      .then(data => {
        if (data.status === true) {
          console.log(`${word} в словаре`);
        } else {
          console.log(`${word} не в словаре`);
        }
      })
      .catch(error => {
        console.error(error);
        console.log('Error checking word');
      });
  };


export default CheckWord