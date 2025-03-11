import React, {useEffect, useState} from 'react';
import Countdown from 'react-countdown'
import { toast } from 'react-toastify'
import { ToastComponent } from "./index";

const Scoreboard = ({ lobbyInfo, navigate }) => {
    const [isDisconnected, setIsDisconnected] = useState(false)
    useEffect(() => {
        if (isDisconnected){
            ToastComponent("Игрок отключился, игра окончена!", "error")
            setTimeout(() => {
                navigate("/")
            }, 5000)
        }
    }, [isDisconnected, navigate]);
    const renderer = ({ seconds, completed }) => {
        if (completed) {
            setIsDisconnected(true)
            return null
        } else {
            return <span>{seconds} секунд</span>
        }
    };
    return(
        <div className={"player_zone"}>
            {lobbyInfo.map((player, playerIndex) =>
                <div className={"scoreboard"} key={playerIndex}>
                    <div className={"name"}>
                        {player["player_status"] === true ? player["username"] :
                            <Countdown
                            date={Date.now() + 60000}
                            renderer={renderer}
                            onMount={() =>
                                ToastComponent("Игрок отключился, у него есть 60 секунд на переподключение!", "warn")}
                            onUnmount={() => ToastComponent("Игрок переподключился", "success")}
                            />
                        }
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
