import { render, screen, waitFor } from "@testing-library/react";
import SelectStage from "./SelectStage";
import { buildTextFile } from "../../../helpers/test/testBuilders";
import userEvent from "@testing-library/user-event";
import {
    DOCUMENT_UPLOAD_STATE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates, UPLOAD_STAGE
} from "../../../types/pages/UploadDocumentsPage/types";
import { act } from "react-dom/test-utils";
import {PatientDetails} from "../../../types/components/types";




jest.mock("react-router");

describe("<UploadDocumentsPage />", () => {
    describe("with NHS number", () => {
        it("renders the page", () => {
            const setDocumentMock = jest.fn();
            const documentOne = buildTextFile("one", 100);
            const documentTwo = buildTextFile("two", 200);
            const documentThree = buildTextFile("three", 100);

            setDocumentMock.mockImplementation((document) => {document.state = documentUploadStates.SELECTED, document.id = 1});

            const mockPatientDetails: PatientDetails = {
                nhsNumber: 9999999999,
                familyName: "testPatient",
                givenName: ["Benedict", "Junior"],
                birthDate: new Date("9/13/2017"),
                postalCode: "SW8 3QJ",
            };

            render(<SelectStage setDocuments={setDocumentMock}
                                patientDetails={mockPatientDetails}
                                uploadDocuments={() => {}}
                                stage={UPLOAD_STAGE.Selecting}
                                setStage={() => {}}
                                documents={[]}
            />)

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