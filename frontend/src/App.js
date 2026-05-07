import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Player from './Player';
import Team from './Team';
import './App.css';

function App() {
  return (
    <Router>
      <Navbar />

      <Routes>
        <Route path="/" element={<div className="home-page"></div>} />
        <Route path="/player/:name" element={<Player />} />
        <Route path="/team/:name" element={<Team />} />
      </Routes>
    </Router>
  );
}

export default App;
