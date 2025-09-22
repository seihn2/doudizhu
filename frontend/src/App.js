import React, { useState } from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import GameRoom from './components/GameRoom';
import RoomList from './components/RoomList';
import SingleGame from './components/SingleGame';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/single-game" element={<SingleGame />} />
            <Route path="/rooms" element={<RoomList />} />
            <Route path="/game/:roomId" element={<GameRoom />} />
          </Routes>
        </div>
      </Router>
    </ConfigProvider>
  );
}

export default App;