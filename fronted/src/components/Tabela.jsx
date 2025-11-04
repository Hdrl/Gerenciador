import React from "react";
import Table from "react-bootstrap/Table";
import Form from "react-bootstrap/Form";
import "bootstrap/dist/css/bootstrap.min.css";

function Tabela({ columns, data, onChangeCheckBox, selectedItemId }) {
  return (
    <Table striped bordered hover responsive size="sm">
      <thead>
        <tr>
          <th>#</th>
          {columns.map((col) => (
            <th key={col.key}>{col.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.length === 0 ? (
          <tr>
            <td colSpan={columns.length + 1} className="text-center text-muted">
              Nenhum registro encontrado.
            </td>
          </tr>
        ) : (
          data.map((row) => (
            <tr
              key={row.id || row[columns[0].key]}
              className={selectedItemId === row.id ? "table-primary" : ""}
            >
              <td>
                <Form.Check
                  type="checkbox"
                  id={`check-${row.id}`}
                  checked={selectedItemId === row.id}
                  onChange={() => onChangeCheckBox(row.id)}
                />
              </td>
              {columns.map((col) => (
                <td key={col.key}>{row[col.key] ? row[col.key] : "-"}</td>
              ))}
            </tr>
          ))
        )}
      </tbody>
    </Table>
  );
}

export default Tabela;
