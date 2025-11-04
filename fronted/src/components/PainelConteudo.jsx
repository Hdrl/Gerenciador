import React from 'react';

/**
 * Um painel de conteúdo genérico com um cabeçalho padrão.
 * @param {string} title - O título a ser exibido no cabeçalho.
 * @param {React.ReactNode} children - O conteúdo a ser renderizado dentro do painel.
 */
function ContentPanel({ title, children, buttons}) {
  return (
    <div className="border border-top-0 p-3">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">{title}</h5>
      </div>
      <div className="content-body">
        {children}
      </div>
    </div>
  );
}

export default ContentPanel;