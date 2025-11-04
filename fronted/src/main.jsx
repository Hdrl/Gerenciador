import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import ProdutosPage from "./pages/ProdutosPage.jsx"; // Corrigido o nome da importação
import FormularioPage from "./pages/FormularioPage";
import LayoutProdutos from "./layouts/layoutProdutos";
import "./index.css";
import ListagemPage from "./pages/ListagemPage.jsx";
import ErrorPage from "./pages/ErrorPage.jsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
    handle: { breadcrumb: "Início" },
    children: [
      {
        path: "projetos",
        element: <LayoutProdutos />,
        handle: { breadcrumb: "Projetos" },
        children: [
          {
            index: true,
            element: (
              <ListagemPage apiUrl="/api/projetos/" basePath="/projetos" />
            ),
          },
          {
            path: "novo",
            element: (
              <FormularioPage
                apiUrl="/api/projetos/"
                title="Projeto"
                listPath="/projetos"
              />
            ),
            handle: { breadcrumb: "Novo Projeto" },
          },
          {
            path: ":id",
            element: (
              <FormularioPage
                apiUrl="/api/projetos/"
                title="Projeto"
                listPath="/projetos"
              />
            ),
            handle: { breadcrumb: "Editar Projeto" },
          },
        ],
      },
      {
        path: "produtos",
        element: <LayoutProdutos />,
        handle: { breadcrumb: "Produtos" },
        children: [
          {
            index: true,
            element: (
              <ProdutosPage apiUrl="/api/produtos/" basePath="/produtos" />
            ),
          },
          {
            path: "novo",
            element: (
              <FormularioPage
                apiUrl="/api/produtos/"
                title="Produto Fabricado"
                listPath="/produtos"
              />
            ),
            handle: { breadcrumb: "Novo Produto" },
          },
          {
            path: ":id",
            element: (
              <FormularioPage
                apiUrl="/api/produtos/"
                title="Produto Fabricado"
                listPath="/produtos"
              />
            ),
            handle: { breadcrumb: "Editar Produto" },
          },
          {
            path: "materiasprimas",
            handle: { breadcrumb: "Matérias-Primas" },
            children: [
              {
                index: true,
                element: (
                  <ListagemPage
                    apiUrl="/api/materiasprimas/"
                    basePath="/produtos/materiasprimas"
                  />
                ),
              },
              {
                path: "novo",
                element: (
                  <FormularioPage
                    apiUrl="/api/materiasprimas/"
                    title="Matéria-Prima"
                    listPath="/produtos/materiasprimas"
                  />
                ),
                handle: { breadcrumb: "Nova Matéria-Prima" },
              },
              {
                path: ":id",
                element: (
                  <FormularioPage
                    apiUrl="/api/materiasprimas/"
                    title="Matéria-Prima"
                    listPath="/produtos/materiasprimas"
                  />
                ),
                handle: { breadcrumb: "Editar Matéria-Prima" },
              },
            ],
          },
        ],
      },
      {
        path: "ordemservico",
        element: <LayoutProdutos />,
        handle: { breadcrumb: "Ordem de Serviço" },
        children: [
          {
            index: true,
            element: (
              <ListagemPage
                apiUrl="/api/ordemservico/"
                basePath="/ordemservico"
              />
            ),
          },
          {
            path: "novo",
            element: (
              <FormularioPage
                apiUrl="/api/ordemservico/"
                title="Ordem de Serviço"
                listPath="/ordemservico"
              />
            ),
            handle: { breadcrumb: "Nova Ordem de Serviço" },
          },
          {
            path: ":id",
            element: (
              <FormularioPage
                apiUrl="/api/ordemservico/"
                title="Ordem de Serviço"
                listPath="/ordemservico"
              />
            ),
            handle: { breadcrumb: "Editar Ordem de Serviço" },
          },
        ],
      },
    ],
  },
]);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
