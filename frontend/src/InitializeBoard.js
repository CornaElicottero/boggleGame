import React, {useState, useEffect, useRef} from 'react';
import CheckWord from "./CheckWord";


const InitializeBoard = (board) => {
  const [isPressed, setIsPressed] = useState(false);
  const [wordForCheck, setWordForCheck] = useState('');
  const [currentLetter, setCurrentLetter] = useState(null);


  useEffect(() => {
    if (currentLetter) {
      setWordForCheck(prevWord => prevWord + currentLetter);
    }
  }, [currentLetter]);

  const handleWrapperMouseDown = () => {
    setIsPressed(true);
    const boardBuffer = board
  };

  const handleWrapperMouseUp = () => {
    setIsPressed(false);
    const word = wordForCheck
    CheckWord(word.toLowerCase())
    setWordForCheck('')
  };

const handleLetterMouseEnter = (letter) => {
    if (isPressed) {
      setCurrentLetter(letter);
    }
  };

  const handleLetterMouseLeave = () => {
    setCurrentLetter(null);
  };

  const Wrapper = ({ children }) => {
    return (
      <div
        className="wrapper"
        onMouseDown={handleWrapperMouseDown}
        onMouseUp={handleWrapperMouseUp}
      >
        {children}
      </div>
    );
  };

  const Letter = ({ letter }) => {
    const [isEntered, setIsEntered] = useState(false)
    const className = `letter${isEntered ? '_pressed' : ''}`;
    const isEnteredRef = useRef(false);

  const handleMouseEnter = () => {
  if (isPressed && !isEnteredRef.current) {
    handleLetterMouseEnter(letter);
  }

  if (isPressed) {
    setIsEntered(true);
    isEnteredRef.current = true;
  }
};
    return (
      <div
        className={className}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleLetterMouseLeave}
      >
        {letter}
      </div>
    );
  };

  const CurrentWord = ({ currentWord }) => {
    return (
      <div className="current">
        {currentWord}
      </div>
    );
  };
  // const CheckWord = ({ word }) => {
  //   const [status, setStatus] = useState('');
  //
  // useEffect(() => {
  //   fetch(`http://10.13.13.56:8000/in_dictionary?word=${word}`)
  //     .then(response => response.json())
  //     .then(data => setStatus(data.status));
  // }, [word]);
  //
  // return console.log(status);
// };
  return (
    <div>
      {/*<CheckWord status = {data.status}/>*/}
      <CurrentWord currentWord={wordForCheck} />
      <Wrapper>
        {board.map((row, rowIndex) => (
          <div className="row" key={rowIndex}>
            {row.map((cell, cellIndex) => (
              <Letter letter={cell} key={`${rowIndex}-${cellIndex}`} />
            ))}
          </div>
        ))}
      </Wrapper>
    </div>
  );
};

export default InitializeBoard;
