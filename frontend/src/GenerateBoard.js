import React, {useState, useEffect, useRef} from 'react';


const GenerateBoard = () => {
  const [board, setBoard] = useState([]);
  const [isEntered, setIsEntered] = useState([]);
  const [isPressed, setIsPressed] = useState([]);
  const [wordForCheck, setWordForCheck] = useState('');
  const [currentWord, setCurrentWord] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [lastIndex, setLastIndex] = useState (0)
  const [wordStatus, setWordStatus] = useState(null);
  const [correctWords, setCorrectWords] = useState([]);
  const [isValidWord, setIsValidWord] = useState(false)
  useEffect(() => {
    fetch('http://10.13.13.56:8000/generate')
      .then(response => response.json())
      .then(data => setBoard(data.board))
  }, [])

  const handleMouseDown = (item, index) => {
    const updatedIsPressed = [...isPressed]
    updatedIsPressed[index] = true;
    setIsPressed(updatedIsPressed);
    setIsTyping(true)
    const updatedIsEntered = [...isEntered];
    updatedIsEntered[index] = true;
    setIsEntered(updatedIsEntered);
    setWordForCheck(prevWord => prevWord + item.toLowerCase())
    setLastIndex(index)
    console.log(lastIndex)
  };

  const handleWrapperMouseUp = () => {
    setIsPressed([]);
    setIsEntered([])
    setCurrentWord(wordForCheck)
    setWordForCheck('')
    setIsTyping(false)
  };
  const handleWrapperMouseLeave = () => {
    setIsPressed([]);
    setIsEntered([]);
    setCurrentWord('')
    setWordForCheck('');
    setIsTyping(false);
  }
  const Wrapper = ({ children }) => {
    return (
      <div
        className="wrapper"
        onMouseUp={handleWrapperMouseUp}
        onMouseLeave={handleWrapperMouseLeave}
      >
        {children}
      </div>
    );
  };
    const handleMouseEnter = (item, index) => {
      if ((isPressed[index] || isTyping) && !isEntered[index] && (Math.abs(Math.floor(index / 4) - Math.floor(lastIndex / 4)) <= 1 && Math.abs(index % 4 - lastIndex % 4) <= 1 && (Math.floor(index / 4) - Math.floor(lastIndex / 4) !== 0 || (index % 4 - lastIndex % 4) !== 0))){
      const updatedIsEntered = [...isEntered];
      console.log(isEntered)
      updatedIsEntered[index] = true;
      setIsEntered(updatedIsEntered);
      setWordForCheck(prevWord => prevWord + item.toLowerCase())
      setLastIndex(index)
      }
    }
    // const handleMouseDown = (index) => {
    //   const updatedIsPressed = [...isPressed]
    //   console.log(isPressed)
    //   updatedIsPressed[index] = true;
    //   setIsPressed(updatedIsPressed)
    //   console.log(isPressed)
    // }
  const CurrentWord = ({ currentWord }) => {
    return (
      <div className="current">
        {currentWord}
      </div>
    );
  };
  const CheckWord = ({ word }) => {
  const [wordStatus, setWordStatus] = useState(null);
  const [correctWords, setCorrectWords] = useState([]);

  useEffect(() => {
    let isMounted = true;

    const fetchWordStatus = async () => {
      try {
        const response = await fetch(`http://10.13.13.56:8000/in_dictionary?word=${word}`);
        const data = await response.json();

        if (isMounted) {
          setWordStatus(data.status);

          if (data.status && !correctWords.includes(word)) {
            setCorrectWords(prevWords => [...prevWords, word]);
          }
        }
      } catch (error) {
        console.error('Error fetching word status:', error);
      }
    };

    if (word) {
      fetchWordStatus();
    } else {
      setWordStatus(null);
    }

    return () => {
      isMounted = false;
    };
  }, [word, correctWords]);

  return <div className="current">{wordStatus ? "Слово есть в словаре" : "Слова нет в словаре"}</div>;
};

  const Scoreboard = ({wordStatus}) => {
    return(
        <div className={"player_zone"}>
            <div className={"scoreboard"}>
              <div className={"name"}>zageev</div>
              {/*<div className={"name"} key={}>{player_one}</div>*/}
          {correctWords.map((word, index) => (
            <div className={"word"} key={index}>{word}</div>
          ))}
            </div>
            <div className={"scoreboard"}>
              <div className={"name"}>elicot2346</div>
          {correctWords.map((word, index) => (
            <div className={"word"} key={index}>{word}</div>
          ))}
            </div>
        </div>
    )
  }
  return (
    <div className={"game_wrapper"}>
      <CheckWord word={currentWord}/>
      <CurrentWord currentWord={wordForCheck} />
      <Wrapper>
        {board.flat().map((item, index) => (
              <div
                className={`letter${isPressed && isEntered[index] ? '_pressed' : ''}`}
                onMouseEnter={() => handleMouseEnter(item, index)}
                onMouseDown={() => handleMouseDown(item, index)}
                key={index}
              >
                {item}
              </div>
            ))}
      </Wrapper>
      <Scoreboard wordStatus={wordStatus}/>
    </div>
  );
};

export default GenerateBoard;