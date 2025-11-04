import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css'; 

function App() {
  
  const [username, setUsername] = useState('Seu Usuário'); 

  const handleLogout = () => {
    console.log("Chamando API de logout...");
    // ex: fetch('/api/logout').then(() => setUsername(null));
  };

  return (
    <div className="d-flex w-100" id="main">
      
      <Sidebar username={username} onLogout={handleLogout} />
      <main className="w-100">
        <Topbar username={username} onLogout={handleLogout} />
        <div className="container-fluid p-4">
          <Outlet />
        </div>
      </main>
      
    </div>
  );
}

export default App;