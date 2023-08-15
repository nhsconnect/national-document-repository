import React from "react";
import "./styles/App.scss";
import UploadDocumentsPage from "./pages/UploadDocumentsPage";
import Layout from "./components/layout";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ConfigProvider from "./providers/configProvider/ConfigProvider";
import config from "./config";

function App() {
  return (
    <ConfigProvider config={config}>
      <Router>
        <Layout>
          <Routes>
            <Route element={<HomePage />} path={"/"} />
            <Route element={<UploadDocumentsPage />} path={"/upload"} />
          </Routes>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;
