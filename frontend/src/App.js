import React from 'react';
import './App.css';
import MapGlobe from './components/MapGlobe';
import WorldIDAuth from './components/WorldIDAuth';

function App() {
  return (
    <div className="App">
      <WorldIDAuth>
        <MapGlobe />
      </WorldIDAuth>
    </div>
  );
}

export default App;
