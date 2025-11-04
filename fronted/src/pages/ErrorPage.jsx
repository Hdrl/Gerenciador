import React from "react";
import { useRouteError } from "react-router-dom";
import { Container, Row, Col, Alert } from "react-bootstrap";
import Sidebar from "../components/Sidebar";

function ErrorPage() {
  const error = useRouteError();

  return (
    <div className="d-flex">
      <Sidebar />
      <Container fluid className="mt-4">
        <Row>
          <Col md={{ span: 8, offset: 2 }}>
            <Alert variant="danger">
              <h4>Oops! Algo deu errado.</h4>
              <p>
                {error?.statusText || error?.message || "Erro desconhecido."}
              </p>
            </Alert>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default ErrorPage;
