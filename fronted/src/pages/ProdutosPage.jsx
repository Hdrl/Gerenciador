import React from "react";
import { Container } from "react-bootstrap";
import Menu from "../components/Menu"; //
import TabelaDRF from "../components/TabelaDRF"; // (Ajuste o caminho se necessário)

function ProdutosPage() {
  const itensDoMenu = [
    {
      key: "produto-fabricado", //
      title: "Produto Fabricado", //
      //
      content: <TabelaDRF apiUrl="/api/produtos/" basePath="/produtos" />,
    },
    {
      key: "materia-prima", //
      title: "Matéria-Prima", //
      //
      content: (
        <TabelaDRF
          apiUrl="/api/materiasprimas/"
          basePath="/produtos/materiasprimas"
        />
      ),
    },
  ];

  return (
    <Container fluid className="mt-4">
      <Menu items={itensDoMenu} defaultActiveKey="produto-fabricado" />
    </Container>
  );
}

export default ProdutosPage;
