import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Container, Row, Col, Card } from "react-bootstrap";
import FormularioDRF from "../components/FormularioDRF"; // Importa o formulário

/**
 * Esta é uma página "wrapper" genérica para o FormularioDRF.
 * @param {string} apiUrl - A URL da API (ex: "/api/produtos/").
 * @param {string} title - O título para o formulário (ex: "Produto").
 * @param {string} listPath - A rota para onde voltar (ex: "/produtos").
 */
function FormularioPage({ apiUrl, title, listPath }) {
  // Pega o 'id' da URL (ex: /produtos/:id)
  const { id } = useParams();
  const navigate = useNavigate();

  const pageTitle = id ? `Editar ${title}` : `Criar ${title}`;

  const handleSave = () => {
    navigate(listPath); // Volta para a lista
  };

  const handleCancel = () => {
    navigate(listPath); // Volta para a lista
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col md={10} lg={8} className="mx-auto">
          <Card>
            <Card.Body>
              <h3>{pageTitle}</h3>
              <FormularioDRF
                url={apiUrl}
                itemId={id} // Passa o ID da URL
                onSave={handleSave}
                onCancel={handleCancel}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default FormularioPage;
