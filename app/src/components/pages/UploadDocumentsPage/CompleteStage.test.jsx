import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { act } from "react-dom/test-utils";
import {DOCUMENT_UPLOAD_STATE as documentUploadStates} from "../../../types/pages/UploadDocumentsPage/types";
import { buildTextFile } from "../../../helpers/test/testBuilders";
import CompleteStage from "./CompleteStage";
import { useNavigate } from "react-router";

jest.mock("react-router");

describe("<CompleteStage />", () => {
    describe("Show uploaded docs", () => {
       
        it(" ", async () => {
            const navigateMock = jest.fn();
            const documentOne = {file: buildTextFile("one", 100), state: documentUploadStates.FAILED, id: 1};
            const documentTwo = {file: buildTextFile("two", 200), state: documentUploadStates.SUCCEEDED, id: 2};
            const documentThree = {file: buildTextFile("three", 100), state: documentUploadStates.SUCCEEDED, id: 3};
            
            useNavigate.mockImplementation(() => navigateMock);

            render(<CompleteStage documents={[documentOne, documentTwo, documentThree]} />);
            
            expect(await screen.findByRole("heading", { name: "Upload Summary" })).toBeInTheDocument();

            userEvent.click(screen.getByLabelText("View successfully uploaded documents"));

            expect(screen.getByText(documentTwo.file.name)).toBeInTheDocument();
            expect(screen.getByText(documentThree.file.name)).toBeInTheDocument();
            expect(screen.getByRole("heading", { name: "There is a problem" })).toBeInTheDocument();
            expect(screen.getByText(`1 of 3 files failed to upload`));
            expect(screen.getByText("If you want to upload another patient's health record")).toBeInTheDocument();

            userEvent.click(screen.getByRole("button", { name: "Start Again" }));

            expect(navigateMock).toHaveBeenCalledWith('/');
        });
    });

   
});
