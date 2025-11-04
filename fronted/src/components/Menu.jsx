// GenericMenuTabs.js
import React from 'react';
import { Tabs, Tab } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

/**
 * Um componente de menu genérico que renderiza Abas (Tabs) 
 * com base em um array de itens.
 *
 * @param {string} defaultActiveKey - (Opcional) A 'key' do item que deve vir ativo.
 * @param {Array<Object>} items - Um array de objetos de configuração da aba.
 * Cada objeto deve ter: 
 * - key: (string) Identificador único (para o eventKey)
 * - title: (string) O texto que aparece na aba
 * - content: (React.ReactNode) O JSX a ser renderizado no painel
 */
function Menu({ items = [], defaultActiveKey }) {
  const activeKey = defaultActiveKey || (items.length > 0 ? items[0].key : null);

  return (
    <Tabs 
      defaultActiveKey={activeKey} 
      id="generic-menu-tabs" 
      className="mt-3"
      //mountOnEnter
      //unmountOnExit 
    >
      {items.map((item) => (
        <Tab 
          key={item.key} 
          eventKey={item.key} 
          title={item.title}
        >
          {item.content}
        </Tab>
      ))}
      
    </Tabs>
  );
}

export default Menu;