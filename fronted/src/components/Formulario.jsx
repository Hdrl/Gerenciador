import React from "react";
import { Form, Button, Spinner, Alert } from "react-bootstrap";

function GenericForm({
  config,
  formData,
  onDataChange,
  onSubmit,
  validationErrors,
  title,
  loading,
  onCancel,
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  const renderField = (fieldConfig) => {
    const {
      name,
      label,
      type,
      options,
      placeholder,
      defaultOptionLabel,
      required,
      readOnly,
      helpText,
    } = fieldConfig;

    const error = validationErrors[name] ? validationErrors[name][0] : null;

    const commonProps = {
      name: name,
      value: formData[name] || "",
      onChange: onDataChange,
      isInvalid: !!error,
      placeholder: placeholder,
      required: required,
      readOnly: readOnly,
    };

    if (type === "checkbox") {
      return (
        <Form.Group className="mb-3" controlId={name}>
          <Form.Check
            type="checkbox"
            label={
              <>
                {label}
                {required && <span className="text-danger ms-1">*</span>}
              </>
            }
            name={name}
            checked={!!formData[name]}
            onChange={(e) =>
              onDataChange({ target: { name, value: e.target.checked } })
            }
            isInvalid={!!error}
            readOnly={readOnly}
          />
          {helpText && <Form.Text muted>{helpText}</Form.Text>}
          <Form.Control.Feedback type="invalid">{error}</Form.Control.Feedback>
        </Form.Group>
      );
    }

    return (
      <Form.Group className="mb-3" controlId={name}>
        <Form.Label>
          {label}
          {required && <span className="text-danger ms-1">*</span>}
        </Form.Label>

        {type === "select" ? (
          <Form.Select {...commonProps} aria-label={label}>
            <option value="">{defaultOptionLabel || `Selecione...`}</option>
            {options &&
              options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
          </Form.Select>
        ) : (
          <Form.Control type={type} {...commonProps} />
        )}

        {helpText && !error && <Form.Text muted>{helpText}</Form.Text>}

        <Form.Control.Feedback type="invalid">{error}</Form.Control.Feedback>
      </Form.Group>
    );
  };

  const globalErrors =
    validationErrors.global || validationErrors.non_field_errors;

  return (
    <Form onSubmit={handleSubmit} noValidate>
      {title && <h3>{title}</h3>}

      {globalErrors && <Alert variant="danger">{globalErrors[0]}</Alert>}

      {config.map((field) => (
        <React.Fragment key={field.name}>{renderField(field)}</React.Fragment>
      ))}

      <div className="d-flex gap-2">
        <Button variant="primary" type="submit" disabled={loading}>
          {loading ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-2"
              />
              Salvando...
            </>
          ) : onCancel ? (
            "Atualizar"
          ) : (
            "Salvar"
          )}
        </Button>

        {onCancel && (
          <Button variant="secondary" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
        )}
      </div>
    </Form>
  );
}

export default GenericForm;