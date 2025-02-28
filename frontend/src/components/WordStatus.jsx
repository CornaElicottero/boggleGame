// import {useEffect, useState} from "react";
//
// const WordStatus = ({ word, ws }) => {
//
//     checkWord(ws, word)
//     useEffect(() => {
//         fetch(`http://localhost:8000/api/checkWord?word=${word}`,{
//             method: 'GET',
//             credentials: 'include',
//             headers: {
//                 "Access-Control-Allow-Origin": "http://localhost:3000",
//             }
//         })
//             .then(response => response.json())
//             .then((data) => setWordStatus(data.status));
//     }, [word]);
//     // useEffect(() => {
//     //     if (wordStatus === true && !correctWords.includes(word)) {
//     //         setCorrectWords(prevWords => [...prevWords, word]);
//     //         // socket.send()
//     //     }
//     // }, [wordStatus]);
//     return (
//         <>
//             <div className="current">
//                 {wordStatus ? "Слово есть в словаре" : "Слова нет в словаре"}
//             </div>
//         </>
//     )
// }
//
// export default WordStatus