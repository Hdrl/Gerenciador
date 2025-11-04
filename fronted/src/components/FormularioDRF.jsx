import React, { useState, useEffect, useCallback } from "react";
import apiClient from "../api/apiClient";
import { Alert, Spinner } from "react-bootstrap";
import GenericForm from "./formulario";

const mapDrfTypeToHtml = (drfType) => {
  switch (drfType) {
    case "string":
    case "field":
      return "text";
    case "integer":
    case "float":
    case "decimal":
      return "number";
    case "boolean":
      return "checkbox";
    case "choice":
      return "select";
    case "date":
      return "date";
    case "datetime":
      return "datetime-local";
    case "email":
      return "email";
    case "url":
      return "url";
    case "password":
      return "password";
    default:
      return "text";
  }
};

const convertOptionsToConfig = (optionsData, mode) => {
  let fields = null;

  if (optionsData && optionsData.actions) {
    fields = optionsData.actions[mode];
    if (!fields && mode === "PUT") {
      fields = optionsData.actions["POST"];
    }
  }

  if (!fields && optionsData) {
    fields = optionsData[mode];
    if (!fields && mode === "PUT") {
      fields = optionsData["POST"];
    }
  }

  if (!fields && optionsData) {
    fields = optionsData[mode.toLowerCase()];
    if (!fields && mode === "PUT") {
      fields = optionsData["post"];
    }
  }

  if (!fields) {
    console.error(
      `[FormularioDRF] Erro: Não foi possível encontrar os metadados para o modo '${mode}'. (Fallback de POST também falhou)`
    );
    console.log("Resposta OPTIONS recebida:", optionsData);
    return [];
  }

  return Object.keys(fields)
    .map((fieldName) => {
      const field = fields[fieldName];

      if (field.read_only && mode === "POST") {
        return null;
      }

      const configItem = {
        name: fieldName,
        label: field.label,
        type: mapDrfTypeToHtml(field.type),
        required: field.required,
        readOnly: field.read_only,
        helpText: field.help_text,
        options: null,
      };

      if (configItem.type === "select" && field.choices) {
        configItem.options = field.choices.map((choice) => ({
          value: choice.value,
          label: choice.display_name,
        }));
      }

      return configItem;
    })
    .filter(Boolean);
};

function FormularioDRF({ url, itemId, onSave, onCancel }) {
  const [formConfig, setFormConfig] = useState([]);
  const [formData, setFormData] = useState({});
  const [validationErrors, setValidationErrors] = useState({});

  const [loadingConfig, setLoadingConfig] = useState(true);
  const [loadingData, setLoadingData] = useState(false);
  const [loadingSubmit, setLoadingSubmit] = useState(false);

  const [error, setError] = useState(null);

  const isEditMode = !!itemId;

  useEffect(() => {
    setLoadingConfig(true);
    setError(null);
    setFormConfig([]);

    apiClient
      .options(url)
      .then((response) => {
        if (!response) {
          console.error(
            "[FormularioDRF] A resposta OPTIONS foi bem-sucedida, mas a resposta (data) está vazia.",
            response
          );
          setError("A API não retornou metadados válidos.");
          setLoadingConfig(false);
          return;
        }

        const mode = isEditMode ? "PUT" : "POST";

        const config = convertOptionsToConfig(response, mode);

        if (config.length === 0) {
          setError("Erro ao processar os metadados da API.");
        }

        setFormConfig(config);
      })
      .catch((err) => {
        console.error("Erro ao buscar metadados (OPTIONS):", err);
        setError("Não foi possível carregar a configuração do formulário.");
      })
      .finally(() => {
        setLoadingConfig(false);
      });
  }, [url, isEditMode]);

  useEffect(() => {
    if (isEditMode && formConfig.length > 0) {
      setLoadingData(true);
      setError(null);

      apiClient
        .get(`${url}${itemId}/`)
        .then((response) => {
          setFormData(response);
        })
        .catch((err) => {
          console.error(`Erro ao buscar dados do item ${itemId}:`, err);
          setError("Não foi possível carregar os dados para edição.");
        })
        .finally(() => {
          setLoadingData(false);
        });
    } else if (!isEditMode) {
      setFormData({});
    }
  }, [url, itemId, isEditMode, formConfig]);

  const handleDataChange = (e) => {
    if (!e || !e.target) {
      console.warn("handleDataChange chamado com um evento inválido:", e);
      return;
    }

    const { name, value, type, checked } = e.target;

    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = () => {
    setLoadingSubmit(true);
    setValidationErrors({});

    const request = isEditMode
      ? apiClient.put(`${url}${itemId}/`, formData)
      : apiClient.post(url, formData);

    request
      .then((response) => {
        alert(isEditMode ? "Item atualizado!" : "Item criado!");
        setLoadingSubmit(false);
        if (onSave) {
          onSave(response);
        }
        if (!isEditMode) {
          setFormData({});
        }
      })
      .catch((err) => {
        // --- INÍCIO DA MODIFICAÇÃO ---
        // 'err' é o objeto que o interceptor rejeitou.
        // Pode ser:
        // 1. O data (ex: { descricao: ["..."] }) vindo do 'error.response.data'
        // 2. O objeto { general: 'API offline...' }
        // 3. O objeto { general: 'Erro inesperado...' }

        // Se 'err' for um objeto, não for nulo, e NÃO tiver a chave 'general',
        // podemos assumir que é um erro de validação 400.
        if (typeof err === "object" && err !== null && !err.general) {
          console.log("ERROS DE VALIDAÇÃO (via interceptor):", err);
          setValidationErrors(err);
        } else {
          // Se for 'API offline' ou outro erro
          console.error("Erro global (via interceptor):", err);
          setValidationErrors({
            global: err.general || "Ocorreu um erro inesperado.",
          });
        }
        // --- FIM DA MODIFICAÇÃO ---
        setLoadingSubmit(false);
      });
  };

  if (loadingConfig || loadingData) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Carregando...</p>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  return (
    <GenericForm
      config={formConfig}
      formData={formData}
      onDataChange={handleDataChange}
      onSubmit={handleSubmit}
      validationErrors={validationErrors}
      loading={loadingSubmit}
      onCancel={isEditMode ? onCancel : null}
    />
  );
}

export default FormularioDRF;
