import React from "react";
import { Container } from "react-bootstrap";
import TabelaDRF from "../components/TabelaDRF"; // (Ajuste o caminho se necessário)
import Menu from "../components/Menu";

function ListagemPage({apiUrl, basePath, itensMenu=null}) {
  return (
    <Container fluid className="mt-4">
        {itensMenu? <Menu items={itensMenu}/>:''}
      <TabelaDRF apiUrl={apiUrl} basePath={basePath}></TabelaDRF>
    </Container>
  );
}

export default ListagemPage;