import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { GenerateBoard, Authorization, Login, Registration } from "./pages/index.js";
import './index.css';

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" exact element={<Authorization/>} />
                <Route path="/game" element={<GenerateBoard />} />
                <Route path="/sign-up" element={<Registration/>} />
                <Route path="/login" element={<Login />}/>
            </Routes>
        </BrowserRouter>
    );
};

export default App
