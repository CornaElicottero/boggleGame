import React, {useEffect, useState} from 'react';
import { useHistory } from 'react-router-dom';
import InitializeBoard from "./InitializeBoard";

const Dialog = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [game_code, setGame_code] = useState('');
  const [player_name, setPlayer_name] = useState('')
  const [board, setBoard] = useState([]);
  const closeDialog = () => {
    setIsOpen(false);
  };

let timerId;

const handleCodeChange = (e) => {
  clearTimeout(timerId);

  const game_code = e.target.value;
  setGame_code(game_code);
  if (game_code.length === 4) {
    timerId = setTimeout(async () => {
      try {
        const response = await fetch(`http://localhost:8000/games/${game_code}`);
        if (response.ok) {
          const data = await response.json();
          const boardArray = data.board
          .slice(2, -2)
          .split("},{")
          .map(row => row.split(",")); // Разделение каждой строки на элементы массива
          console.log(typeof(boardArray))
          setBoard(boardArray);
          console.log('Полученная доска:', board);
          // window.location.href = 'http://10.13.13.56:3000/join/${board}';
          const responseName = await fetch('http://localhost:8000/players/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({player_name}),
        });
        if (responseName.ok) {
          const data = await responseName.json();
          console.log('Player created:', data);
        } else {
          console.error('Failed to create player');
        }
          closeDialog();
        } else {
          console.error('Ошибка при получении доски');
        }
      } catch (error) {
        console.error('Ошибка при выполнении GET-запроса:', error);
      }
    }, 1000);
  }
};

  const handleNameChange = (e) => {
    setPlayer_name(e.target.value);
  };

  const handleNewGame = async (e) => {
    e.preventDefault();

    const response = await fetch('http://localhost:8000/players/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({player_name}),
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Player created:', data);
    } else {
      console.error('Failed to create player');
    }
    closeDialog();
  };
  return (
    <div>
      {isOpen && (
        <div className={"dialog-overlay"}>
          <div className={"dialog"}>
            <div>
            <input
              type="text"
              value={player_name}
              onChange={handleNameChange}
              placeholder="Имя"
              className={"dialog_name_input"}
              maxLength = "13"
            />
              </div>
            <div>
              <button onClick={handleNewGame} className={"new_game_btn"}>Новая игра</button>
              <p className={"dialog_text"}>или</p>
              <input
              type="text"
              value={game_code}
              onChange={handleCodeChange}
              placeholder="Код"
              className={"dialog_code_input"}
              maxLength = "4"
            />
            </div>
          </div>
        </div>
      )}
      {/*<InitializeBoard board={board} />*/}
    </div>
  );
};

export default Dialog;
