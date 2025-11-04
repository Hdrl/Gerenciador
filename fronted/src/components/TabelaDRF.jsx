import React, { useState, useEffect } from "react";
import Tabela from "./Tabela";
import apiClient from "../api/apiClient";
import {
  Card,
  ButtonGroup,
  Button,
  Container,
  Col,
  Row,
  Spinner,
  Alert,
} from "react-bootstrap";
import { Link } from "react-router-dom"; // IMPORTADO
import { PlusCircle, PencilSquare, Trash } from "react-bootstrap-icons";

// Adicione a prop 'basePath' para construir os links
// Ex: basePath="/produtos"
function TabelaDRF({ apiUrl, basePath }) {
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [encontrados, setEncontrados] = useState(0);
  const [selectedItem, setSelectedItem] = useState(null);
  const [reload, setReload] = useState(0);

  // A lógica de 'viewMode' foi REMOVIDA

  function handlerCheckBox(id) {
    if (selectedItem === id) {
      setSelectedItem(null);
    } else {
      setSelectedItem(id);
    }
  }

  const handleDelete = () => {
    if (!selectedItem) return;

    if (window.confirm("Tem certeza que deseja excluir o item selecionado?")) {
      apiClient
        .delete(`${apiUrl}${selectedItem}/`)
        .then(() => {
          setReload((r) => r + 1);
          setSelectedItem(null);
        })
        .catch((err) => {
          console.error("Erro ao excluir:", err);
          alert("Não foi possível excluir o item.");
        });
    }
  };

  // Funções handleAddClick, handleEditClick, handleCancel, handleSave foram REMOVIDAS
  // Elas não são mais necessárias aqui

  useEffect(() => {
    setLoading(true);

    const fetchData = apiClient.get(apiUrl);
    const fetchMetadata = apiClient.options(apiUrl);

    Promise.all([fetchData, fetchMetadata])
      .then(([dataResponse, metadataResponse]) => {
        let fields = null;
        if (metadataResponse && metadataResponse.actions) {
          fields =
            metadataResponse.actions.POST || metadataResponse.actions.PUT;
        } else if (metadataResponse) {
          fields = metadataResponse.POST || metadataResponse.PUT;
        }

        if (!fields) {
          throw new Error(
            "Não foi possível encontrar os metadados (fields) na resposta OPTIONS."
          );
        }

        const colunasFormatadas = Object.keys(fields)
          .filter((key) => fields[key].read_only === false && key !== "id")
          .map((key) => ({
            key: key,
            label: fields[key].label,
          }));

        if (fields.id) {
          colunasFormatadas.unshift({ key: "id", label: "ID" });
        }

        const dados = dataResponse.results || dataResponse;

        const choiceMap = {};
        Object.keys(fields)
          .filter((key) => fields[key].type === "choice" && fields[key].choices)
          .forEach((key) => {
            // Cria um mapa para este campo específico, ex: 'unidade_medida'
            const mapDoCampo = {};
            fields[key].choices.forEach((choice) => {
              // Ex: mapDoCampo["UN"] = "Unidade"
              mapDoCampo[choice.value] = choice.display_name;
            });
            choiceMap[key] = mapDoCampo;
          });
        const colunasChoice = Object.keys(choiceMap); 
        const dadosFormatados = dados.map((row) => {
          const newRow = { ...row };

          colunasChoice.forEach((colKey) => {
            const rawValue = row[colKey];

            if (rawValue && choiceMap[colKey][rawValue]) {
              newRow[colKey] = choiceMap[colKey][rawValue]; 
            }
          });

          return newRow;
        });

        setEncontrados(dados.length);
        setData(dadosFormatados);
        setColumns(colunasFormatadas);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Erro ao buscar dados ou metadados da API:", error);
        setError("Não foi possível carregar os dados.");
        setLoading(false);
      });
  }, [apiUrl, reload]);

  if (loading) {
    return (
      <Container className="mt-4 text-center">
        <Spinner animation="border" />
        <p>Carregando...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col md={12}>
          {/* A lógica de 'viewMode' foi REMOVIDA daqui */}
          <Card className="mb-3">
            <Card.Body>
              <ButtonGroup size="sm">
                <Button
                  as={Link} // MODIFICADO
                  to={`${basePath}/novo`} // MODIFICADO
                  variant="success"
                  className="me-2"
                >
                  <PlusCircle className="me-1" /> Adicionar
                </Button>
                <Button
                  as={Link} // MODIFICADO
                  to={selectedItem ? `${basePath}/${selectedItem}` : "#"} // MODIFICADO
                  variant="primary"
                  className="me-2"
                  disabled={!selectedItem}
                >
                  <PencilSquare className="me-1" /> Editar
                </Button>
                <Button
                  variant="danger"
                  onClick={handleDelete}
                  disabled={!selectedItem}
                >
                  <Trash className="me-1" /> Excluir
                </Button>
              </ButtonGroup>
            </Card.Body>
          </Card>
          <Tabela
            columns={columns}
            data={data}
            onChangeCheckBox={handlerCheckBox}
            selectedItemId={selectedItem}
          />
          {encontrados > 0 && <div>{encontrados} Registros Encontrados</div>}
        </Col>
      </Row>
    </Container>
  );
}

export default TabelaDRF;
