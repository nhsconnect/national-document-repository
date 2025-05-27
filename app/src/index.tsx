import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';
import 'pdfjs-viewer-element';
import PdfjsViewerElement from 'pdfjs-viewer-element';

declare module 'react' {
    namespace JSX {
        interface IntrinsicElements {
            'pdfjs-viewer-element': React.DetailedHTMLProps<
                React.AllHTMLAttributes<PdfjsViewerElement>,
                HTMLElement
            >;
        }
    }
}

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
);
