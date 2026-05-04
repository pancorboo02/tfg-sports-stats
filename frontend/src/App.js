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
        <Route path="/" element={<div style={{ padding: 20 }}>Inicio</div>} />
        <Route path="/player/:name" element={<Player />} />
        <Route path="/team/:name" element={<Team />} />
      </Routes>
    </Router>
  );
}

export default App;
