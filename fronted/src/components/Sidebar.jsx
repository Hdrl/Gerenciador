// 📁 src/components/Sidebar.jsx (Corrigido)

import React, { useState } from 'react';
import { Nav, Dropdown, Collapse } from 'react-bootstrap';
// 1. Importar NavLink em vez de Link
import { NavLink } from 'react-router-dom'; 
import './Sidebar.css';

function Sidebar({ username = 'Usuário', onLogout }) {
  
  const [producaoOpen, setProducaoOpen] = useState(false);

  const handleLogout = (e) => {
    e.preventDefault();
    if (onLogout) {
      onLogout();
    }
  };

  // Esta função ajuda a manter o código limpo
  const getNavLinkClass = ({ isActive }) => {
    // Retorna a classe 'text-white' sempre, e 'active-nav-item' se estiver ativo
    return `text-white ${isActive ? 'active-nav-item' : ''}`;
  };

  // Classe para os links do submenu
  const getSubmenuNavLinkClass = ({ isActive }) => {
    return `link-light rounded ${isActive ? 'active-nav-item' : ''}`;
  };

  return (
    <nav id="sidebar" className="d-flex flex-column flex-shrink-0 p-3 text-white bg-dark">
      {/* 2. Opcional: Mudei o Link da marca para NavLink também */}
      <NavLink to="/" className="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none">
        <i className="bi bi-calendar-check me-2 fs-4"></i>
        <span className="fs-4 sidebar-text">Gerenciador</span>
      </NavLink>
      
      <hr />
      
      <Nav variant="pills" className="flex-column mb-auto sidebar-nav">
        
        {/* --- EXEMPLO 1: Link com "end" (o antigo "exact") --- */}
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/projetos" 
            className={getNavLinkClass} // Usando a função
            //end // "end" é o novo "exact"
          >
            <i className="bi bi-house-door me-2"></i>
            <span className="sidebar-text">Projeto</span>
          </Nav.Link>
        </Nav.Item>

        {/* --- EXEMPLO 2: Links normais --- */}
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/produtos" 
            className={getNavLinkClass}
          >
            <i className="bi bi-box-seam-fill me-2"></i>
            <span className="sidebar-text">Produtos</span>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/demanda" 
            className={getNavLinkClass}
          >
            <i className="bi bi-credit-card-2-front me-2"></i>
            <span className="sidebar-text">Demanda</span>
          </Nav.Link>
        </Nav.Item>
        
        {/* O item de colapso não muda, pois não é um link */}
        <Nav.Item>
          <Nav.Link 
            onClick={() => setProducaoOpen(!producaoOpen)} 
            aria-controls="submenu-tarefas"
            aria-expanded={producaoOpen}
            className="text-white d-flex justify-content-between"
            style={{ cursor: 'pointer' }}
          >
            <span>
              <i className="bi bi-hammer me-2"></i>
              <span className="sidebar-text">Produção</span>
            </span>
            <i className={`bi bi-chevron-down sidebar-text ms-auto transition-chevron ${producaoOpen ? 'rotate-180' : ''}`}></i>
          </Nav.Link>
          
          <Collapse in={producaoOpen}>
            <div id="submenu-tarefas">
              <Nav className="flex-column ps-4 pt-1 small">
                {/* --- EXEMPLO 3: Link de Submenu --- */}
                <Nav.Item>
                  <Nav.Link 
                    as={NavLink} 
                    to="/ordemproducao" 
                    className={getSubmenuNavLinkClass} // Função de classe do submenu
                  >
                    Ordem Produção
                  </Nav.Link>
                </Nav.Item>
              </Nav>
            </div>
          </Collapse>
        </Nav.Item>

        {/* --- EXEMPLO 4: Links restantes --- */}
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/admin" 
            className={getNavLinkClass}
          >
            <i className="bi bi-list-task me-2"></i>
            <span className="sidebar-text">Cadastro</span>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/ordemservico" 
            className={getNavLinkClass}
          >
            <i className="bi bi-card-list me-2"></i>
            <span className="sidebar-text">Ordens de Serviço</span>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/atividades" 
            className={getNavLinkClass}
          >
            <i className="bi bi-card-list me-2"></i>
            <span className="sidebar-text">Atividades</span>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/relatorios" 
            className={getNavLinkClass}
          >
            <i className="bi bi-table me-2"></i>
            <span className="sidebar-text">Relatórios</span>
          </Nav.Link>
        </Nav.Item>
      </Nav>
      
      <hr />
      
      {/* O Dropdown do usuário não precisa de NavLink, está correto */}
      <Dropdown>
        <Dropdown.Toggle 
          id="dropdownUser1" 
          variant="dark" 
          className="d-flex align-items-center text-white text-decoration-none w-100"
        >
          <i className="bi bi-person-circle fs-4 me-2"></i>
          <strong className="sidebar-text">{username}</strong>
        </Dropdown.Toggle>
        
        <Dropdown.Menu className="dropdown-menu-dark text-small shadow">
          <Dropdown.Item onClick={handleLogout}>
            <i className="bi bi-box-arrow-right me-2"></i>Sair
          </Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
    </nav>
  );
}

export default Sidebar;