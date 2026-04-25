import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Search from './Search';
import Player from './Player';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Search />} />
        <Route path="/player/:name" element={<Player />} />
      </Routes>
    </Router>
  );
}

export default App;
