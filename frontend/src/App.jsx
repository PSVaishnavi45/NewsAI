
import { BrowserRouter, Routes, Route } from "react-router-dom";

import News from "./pages/News.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* NewsAI */}
        <Route path="/" element={<News />} />
        <Route path="/news" element={<News />} />

        {/* Authentication */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;

