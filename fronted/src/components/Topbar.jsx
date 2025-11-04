// Topbar.jsx
import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Dropdown, Breadcrumb } from 'react-bootstrap';
import { Link, useMatches } from 'react-router-dom';

function Topbar({ username = 'Usuário', onLogout }) {
  const matches = useMatches();
  const [breadcrumbs, setBreadcrumbs] = useState([]);

  useEffect(() => {
    const calculatedBreadcrumbs = matches
      .filter((match) => Boolean(match.handle?.breadcrumb))
      .map((match) => ({
        breadcrumb: typeof match.handle.breadcrumb === 'function'
        ? match.handle.breadcrumb(match)
        : match.handle.breadcrumb,
        pathname: match.pathname
      }));

    
    setBreadcrumbs(calculatedBreadcrumbs);

  }, [matches]); 

  const handleLogout = (e) => {
    e.preventDefault();
    if (onLogout) {
      onLogout();
    }
  };

  return (
    <Navbar expand="lg" bg="light" className="border-bottom p-3">
      
      <Breadcrumb listProps={{ className: "mb-0" }}>
        {breadcrumbs.map((crumb, index) => {
          const isLast = index === breadcrumbs.length - 1;
          return (
            <Breadcrumb.Item
              key={crumb.pathname}
              linkAs={!isLast ? Link : 'span'}
              linkProps={!isLast ? { to: crumb.pathname } : {}}
              active={isLast}
            >
              {crumb.breadcrumb}
          </Breadcrumb.Item>

          );
        })}
      </Breadcrumb>
      
      <Nav className="ms-auto">
        <Dropdown align="end">
          <Dropdown.Toggle 
            variant="light" 
            id="dropdownUser2"
            className="d-flex align-items-center text-dark text-decoration-none"
          >
            <i className="bi bi-person-circle fs-4 me-2"></i>
            <strong>{username}</strong>
          </Dropdown.Toggle>
          
          <Dropdown.Menu className="text-small shadow">
            <Dropdown.Item as={Link} to="/configuracoes">
              <i className="bi bi-gear me-2"></i>Configurações
            </Dropdown.Item>
            <Dropdown.Item as={Link} to="/perfil">
              <i className="bi bi-person me-2"></i>Perfil
            </Dropdown.Item>
            <Dropdown.Divider />
            <Dropdown.Item onClick={handleLogout} className="text-danger">
              <i className="bi bi-box-arrow-right me-2"></i>Sair
            </Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </Nav>
    </Navbar>
  );
}

export default Topbar;