import { render, screen, waitFor } from "@testing-library/react";
import SelectStage from "./SelectStage";
import { buildTextFile } from "../../../helpers/test/testBuilders";
import userEvent from "@testing-library/user-event";
import {
    DOCUMENT_UPLOAD_STATE as documentUploadStates, UPLOAD_STAGE
} from "../../../types/pages/UploadDocumentsPage/types";
import { act } from "react-dom/test-utils";
import {PatientDetails} from "../../../types/components/types";


jest.mock("../../../helpers/utils/toFileList", () => []);

jest.mock("react-router");

describe("<UploadDocumentsPage />", () => {
    describe("with NHS number", () => {
        const setDocumentMock = jest.fn();
        const documentOne = buildTextFile("one", 100);
        const documentTwo = buildTextFile("two", 200);
        const documentThree = buildTextFile("three", 100);

        setDocumentMock.mockImplementation((document) => {document.state = documentUploadStates.SELECTED, document.id = 1});

        const mockPatientDetails: PatientDetails = {
            nhsNumber: 111111111,
            familyName: "test",
            givenName: ["Gremlin", "Junior"],
            birthDate: new Date("5/12/2022"),
            postalCode: "BS37 5DH",
        }

        it("renders the page", () => {

            render(<SelectStage setDocuments={setDocumentMock}
                                uploadDocuments={() => {}}
                                stage={UPLOAD_STAGE.Selecting}
                                setStage={() => {}}
                                documents={[]}
            />)

            expect(screen.getByRole("heading", { name: "Upload documents" })).toBeInTheDocument();
            expect(screen.getByText(mockPatientDetails.nhsNumber)).toBeInTheDocument();
            expect(screen.getByLabelText("Select file(s)")).toBeInTheDocument();
            expect(screen.getByRole("button", { name: "Upload" })).toBeInTheDocument();
            expect(screen.getByRole("button", { name: "Upload" })).toBeDisabled();

            act(() => {
            userEvent.upload(screen.getByLabelText("Select file(s)"), [documentOne, documentTwo, documentThree]);
            });
            expect(screen.getByText(documentOne.name)).toBeInTheDocument();
            expect(screen.getByText(documentTwo.name)).toBeInTheDocument();
            expect(screen.getByText(documentThree.name)).toBeInTheDocument();
            expect(screen.getByRole("button", { name: "Upload" })).toBeEnabled();

        });

        it("removes selected file", async () => {

            render(<SelectStage setDocuments={setDocumentMock}
                uploadDocuments={() => {}}
                stage={UPLOAD_STAGE.Selecting}
                setStage={() => {}}
                documents={[]}
            />)
            act(() => {
                userEvent.upload(screen.getByLabelText("Select file(s)"), [documentOne, documentTwo, documentThree]);
            });
            // const documentOneName = await screen.findByText(documentOne.name)

            expect(screen.getByText(documentOne.name)).toBeInTheDocument()

            const removeFile = await screen.findByRole("link", {name: `Remove ${documentOne.name} from selection`})
            console.log(!!removeFile);
            act(() => {
                userEvent.click(removeFile)
            })
    
            expect(screen.queryByText(documentOne.name)).not.toBeInTheDocument();
        });
    });
});