import { render, screen } from "@testing-library/react";
import { act } from "react-dom/test-utils";
import {
    DOCUMENT_UPLOAD_STATE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates, UploadDocument
} from "../../../types/pages/UploadDocumentsPage/types";
import { buildTextFile } from "../../../helpers/test/testBuilders";
import UploadingStage from "./UploadingStage";


jest.mock("react-router");

describe("<UploadDocumentsPage />", () => {
    describe("with NHS number", () => {
        it("uploads documents and displays the progress", async () => {

            const uploadDocumentMock = jest.fn();
            const documentOne = {file: buildTextFile("one", 100), state: documentUploadStates.SELECTED, id: 1};
            const documentTwo = {file: buildTextFile("two", 200), state: documentUploadStates.SELECTED, id: 2};
            const documentThree = {file: buildTextFile("three", 100), state: documentUploadStates.SELECTED, id: 3};
            const uploadStateChangeTriggers = {};
            const resolvers = {};
            const triggerUploadStateChange = (document, state, progress) => {
                act(() => {
                    document.state = state;
                    document.progress = progress
                });
            };
            const resolveDocumentUploadPromise = (document) => {
                act(() => {
                    resolvers[document];
                });
            };

            uploadDocumentMock.mockImplementation(async (document, onUploadStateChange) => {
                uploadStateChangeTriggers[document.name] = onUploadStateChange;

                return new Promise((resolve) => {
                    resolvers[document.name] = resolve;
                });
            });

            render(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 0);

            expect(screen.queryByTestId("upload-document-form")).not.toBeInTheDocument();
            expect(
                screen.getByText("Do not close or navigate away from this browser until upload is complete.")
            ).toBeInTheDocument();


            triggerUploadStateChange(documentTwo, documentUploadStates.UPLOADING, 0);
            triggerUploadStateChange(documentThree, documentUploadStates.UPLOADING, 0);
            triggerUploadStateChange(documentOne, documentUploadStates.FAILED, 0);
            triggerUploadStateChange(documentThree, documentUploadStates.SUCCEEDED, 100);
            triggerUploadStateChange(documentTwo, documentUploadStates.SUCCEEDED, 100);


            resolveDocumentUploadPromise(documentOne);
            resolveDocumentUploadPromise(documentTwo);
            resolveDocumentUploadPromise(documentThree);
        });


        it("progress bar reflect the upload progress", async () => {
            const documentOne = {file: buildTextFile("one", 100), state: documentUploadStates.SELECTED, id: '1', progress: 0};
            const documentTwo = {file: buildTextFile("two", 200), state: documentUploadStates.SELECTED, id: '2', progress: 0};
            const documentThree = {file: buildTextFile("three", 100), state: documentUploadStates.SELECTED, id: '3', progress: 0};
            const triggerUploadStateChange = (document, state, progress) => {
                act(() => {
                    document.state = state;
                    document.progress = progress
                });
            };

            const renderResult = render(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);
            const rerender = () => {
                renderResult.rerender(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);
            }
            const getProgressBarValue = (document) => {
                return parseInt(screen.getByRole("progressbar", { name: `Uploading ${document.file.name}` }).value);
            };
            const getProgressText = (document) => {
                return screen.getByRole("status", { name: `${document.file.name} upload status` }).textContent;
            }

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 10);
            rerender();
            expect(getProgressBarValue(documentOne)).toEqual(10);
            expect(getProgressText(documentOne)).toContain("10% uploaded...");

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 70);
            rerender();
            expect(getProgressBarValue(documentOne)).toEqual(70);
            expect(getProgressText(documentOne)).toContain("70% uploaded...");

            triggerUploadStateChange(documentTwo, documentUploadStates.UPLOADING, 20);
            rerender();
            expect(getProgressBarValue(documentTwo)).toEqual(20);
            expect(getProgressText(documentTwo)).toContain("20% uploaded...");

            triggerUploadStateChange(documentTwo, documentUploadStates.SUCCEEDED, 100);
            rerender();
            expect(getProgressBarValue(documentTwo)).toEqual(100);
            expect(getProgressText(documentTwo)).toContain("Uploaded");

            triggerUploadStateChange(documentOne, documentUploadStates.FAILED, 0);
            rerender();
            expect(getProgressBarValue(documentOne)).toEqual(0);
            expect(getProgressText(documentOne)).toContain("failed");
        });
    });

});
