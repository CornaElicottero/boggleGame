import React from 'react';

const Scoreboard = ({playerInfo}) => {
    return(
        <div className={"player_zone"}>
            {playerInfo.map((player, playerIndex) =>
                <div className={"scoreboard"} key={playerIndex}>
                    <div className={"name"}>
                        {player["username"]}
                    </div>
                    {player["words"].map((word, wordIndex) => (
                        <div className={"word"} key={wordIndex}>
                            {word}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default Scoreboard
