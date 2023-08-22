import { render, screen, waitFor } from "@testing-library/react";
import SelectStage from "./SelectStage";
import { buildTextFile } from "../../../helpers/test/testBuilders";
import userEvent from "@testing-library/user-event";
import {DOCUMENT_UPLOAD_STATE as documentUploadStates} from "../../../types/pages/UploadDocumentsPage/types";
import { act } from "react-dom/test-utils";




jest.mock("react-router");

describe("<UploadDocumentsPage />", () => {
    describe("with NHS number", () => {
        it("renders the page", () => {
            const setDocumentMock = jest.fn();
            const documentOne = buildTextFile("one", 100);
            const documentTwo = buildTextFile("two", 200);
            const documentThree = buildTextFile("three", 100);

            setDocumentMock.mockImplementation((document) => {document.state = documentUploadStates.SELECTED, document.id = 1});
            
            render(<SelectStage setDocuments={setDocumentMock}/>)
                        
            expect(screen.getByRole("heading", { name: "Upload documents" })).toBeInTheDocument();
            expect(screen.getByLabelText("Select file(s)")).toBeInTheDocument();
            expect(screen.getByRole("button", { name: "Upload" })).toBeInTheDocument();
            act(() => {
            userEvent.upload(screen.getByLabelText("Select file(s)"), [documentOne, documentTwo, documentThree]);
            });
            expect(screen.getByText(documentOne.name)).toBeInTheDocument();
            expect(screen.getByText(documentTwo.name)).toBeInTheDocument();
            expect(screen.getByText(documentThree.name)).toBeInTheDocument();
        });
    });
});
