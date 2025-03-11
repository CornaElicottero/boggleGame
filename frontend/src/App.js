import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { GenerateBoard, Authorization, Login, Registration } from "./pages/index.js";
import './index.css';
import { ToastContainer } from 'react-toastify'

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" exact element={<Authorization/>} />
                <Route path="/game" element={<GenerateBoard />} />
                <Route path="/sign-up" element={<Registration/>} />
                <Route path="/login" element={<Login />}/>
            </Routes>
            <ToastContainer
                position="bottom-center"
                autoClose={5000}
                hideProgressBar={false}
                newestOnTop
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="dark"
            />
        </BrowserRouter>
    );
};

export default App
