import React from 'react';

const Scoreboard = ({correctWords}) => {
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

export default Scoreboard
