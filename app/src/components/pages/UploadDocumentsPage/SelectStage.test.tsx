import { render, screen } from "@testing-library/react";
import SelectStage from "./SelectStage";
import { buildTextFile } from "../../../helpers/test/testBuilders";
import userEvent from "@testing-library/user-event";
import {
    DOCUMENT_UPLOAD_STATE as documentUploadStates, UPLOAD_STAGE
} from "../../../types/pages/UploadDocumentsPage/types";
import { act } from "react-dom/test-utils";
import { PatientDetails } from "../../../types/components/types";

jest.mock("../../../helpers/utils/toFileList", () => ({
    __esModule: true,
    default: () => [],
}));

jest.mock("react-router");

describe("<UploadDocumentsPage />", () => {
    describe("upload documents with an NHS number", () => {
        const documentOne = buildTextFile("one", 100);
        const documentTwo = buildTextFile("two", 200);
        const documentThree = buildTextFile("three", 100);

        const setDocumentMock = jest.fn();
        setDocumentMock.mockImplementation((document) => {document.state = documentUploadStates.SELECTED, document.id = 1});

        const mockPatientDetails: PatientDetails = {
            nhsNumber: 111111111,
            familyName: "test",
            givenName: ["Gremlin", "Junior"],
            birthDate: new Date("5/12/2022"),
            postalCode: "BS37 5DH",
        }

        it("renders the page", () => {
            renderSelectStage(setDocumentMock);

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

        it("removes selected file only", async () => {
            renderSelectStage(setDocumentMock);

            act(() => {
                userEvent.upload(screen.getByLabelText("Select file(s)"), [documentOne, documentTwo, documentThree]);
            });

            expect(screen.getByText(documentOne.name)).toBeInTheDocument();

            const removeFile = await screen.findByRole("link", {name: `Remove ${documentOne.name} from selection`});

            act(() => {
                userEvent.click(removeFile);
            });
    
            expect(screen.queryByText(documentOne.name)).not.toBeInTheDocument();
            expect(screen.queryByText(documentTwo.name)).toBeInTheDocument();
            expect(screen.queryByText(documentThree.name)).toBeInTheDocument();
        });

        it("validates that all of the selected files are less than 5GB", async () => {
            renderSelectStage(setDocumentMock);

            const documentBig = buildTextFile("four", 6 * Math.pow(1024, 3));

            act(() => {
                userEvent.upload(screen.getByLabelText("Select file(s)"), [documentOne, documentTwo, documentThree, documentBig]);
            });

            expect(screen.getByText(documentBig.name)).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText("Upload"));
            });

            expect(await screen.findByText("Please ensure that all files are less than 5GB in size"));
        });

        it("warns the user if they have added the same file twice", async () => {
            const duplicateFileWarning = "There are two or more documents with the same name.";

            renderSelectStage(setDocumentMock);

            act(() => {
                userEvent.upload(screen.getByLabelText("Select file(s)"), [documentOne, documentOne]);
            });

            expect(await screen.findByText(duplicateFileWarning)).toBeInTheDocument();

            act(() => {
                userEvent.click(
                    screen.getAllByRole("link", {
                        name: `Remove ${documentOne.name} from selection`,
                    })[1]
                 );
            });

            expect(screen.queryByText(duplicateFileWarning)).not.toBeInTheDocument();
        });

        it("allows the user to add the same file again if they remove it", async () => {
            renderSelectStage(setDocumentMock);

            const selectFilesLabel = screen.getByLabelText("Select file(s)");

            act(() => {
                userEvent.upload(selectFilesLabel, documentOne);
            });

            const removeFile = await screen.findByRole("link", {name: `Remove ${documentOne.name} from selection`});

            act(() => {
                userEvent.click(removeFile);
            });
            act(() => {
                 userEvent.upload(selectFilesLabel, documentOne);
            });

            expect(await screen.findByText(documentOne.name)).toBeInTheDocument();
        });

        it("renders link to PCSE that opens in a new tab", () => {
            renderSelectStage(setDocumentMock);

            const pcseLink = screen.getByRole("link", { name: "Primary Care Support England" });
            expect(pcseLink).toHaveAttribute("href", "https://secure.pcse.england.nhs.uk/");
            expect(pcseLink).toHaveAttribute("target", "_blank");
        });
    });
});

const renderSelectStage = (setDocumentMock: jest.Mock) => {
    render (
        <SelectStage setDocuments={setDocumentMock}
                     uploadDocuments={() => {}}
                     stage={UPLOAD_STAGE.Selecting}
                     setStage={() => {}}
                     documents={[]}
        />
    )
}