import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Auth from "./pages/Auth";
import Home from "./pages/Home";

const isAuthenticated = () => {
  return !!localStorage.getItem("token");
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Auth isLogin={true} />} />

        <Route
          path="/home"
          element={
            isAuthenticated() ? <Home /> : <Navigate to="/" />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;