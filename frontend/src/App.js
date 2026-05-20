import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Player from './Player';
import Team from './Team';
import Ask from './Ask';
import Home from './Home';
import './App.css';

function App() {
  return (
    <Router>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/player/:name" element={<Player />} />
        <Route path="/team/:name" element={<Team />} />
        <Route path="/ask" element={<Ask />} />
      </Routes>
    </Router>
  );
}

export default App;
