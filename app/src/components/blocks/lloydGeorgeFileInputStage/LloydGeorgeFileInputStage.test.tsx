import { fireEvent, render, screen } from '@testing-library/react';
import { buildPatientDetails, buildLgFile } from '../../../helpers/test/testBuilders';
import usePatient from '../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import LloydGeorgeFileInputStage, { Props } from './LloydGeorgeFileInputStage';
import { UploadDocument } from '../../../types/pages/UploadDocumentsPage/types';
import { useState } from 'react';

jest.mock('../../../helpers/utils/toFileList', () => ({
    __esModule: true,
    default: () => [],
}));
jest.mock('../../../helpers/hooks/usePatient');
jest.mock('react-router');
jest.mock('../../../helpers/hooks/useBaseAPIHeaders');
const setStageMock = jest.fn();
const mockedUsePatient = usePatient as jest.Mock;
const mockPatient = buildPatientDetails();

const lgDocumentOne = buildLgFile(1, 2, 'Joe Blogs');
const lgDocumentTwo = buildLgFile(2, 2, 'Joe Blogs');
const lgFiles = [lgDocumentOne, lgDocumentTwo];

const lgDocumentThreeNamesOne = buildLgFile(1, 2, 'Dom Jacob Alexander');
const lgDocumentThreeNamesTwo = buildLgFile(2, 2, 'Dom Jacob Alexander');
const lgFilesThreeNames = [lgDocumentThreeNamesOne, lgDocumentThreeNamesTwo];

const lgDocumentNonStandardCharacterNamesOne = buildLgFile(
    1,
    2,
    'DomžĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖ JacobŗŘřŚśŜŝŞşŠšŢţŤťŦŧ AŨũŪūŬŭŮůŰűŲer',
);
const lgDocumentNonStandardCharacterNamesTwo = buildLgFile(
    2,
    2,
    'DomžĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖ JacobŗŘřŚśŜŝŞşŠšŢţŤťŦŧ AŨũŪūŬŭŮůŰűŲer',
);
const lgFilesNonStandardCharacterNames = [
    lgDocumentNonStandardCharacterNamesOne,
    lgDocumentNonStandardCharacterNamesTwo,
];

describe('<LloydGeorgeFileInputStage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('upload documents with an NHS number', () => {
        it('renders the page', async () => {
            renderApp();

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText('NHS number: ' + formatNhsNumber(mockPatient.nhsNumber)),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Select files' })).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();
        });

        it('can upload documents to LG forms with multiple names using button', async () => {
            renderApp();

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText('NHS number: ' + formatNhsNumber(mockPatient.nhsNumber)),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgFilesThreeNames);
            });

            expect(await screen.findAllByText(lgDocumentThreeNamesOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentThreeNamesTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });

        it('can upload documents to LG forms with non standard characters using button', async () => {
            renderApp();

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText('NHS number: ' + formatNhsNumber(mockPatient.nhsNumber)),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();

            act(() => {
                userEvent.upload(
                    screen.getByTestId('button-input'),
                    lgFilesNonStandardCharacterNames,
                );
            });

            expect(
                await screen.findAllByText(lgDocumentNonStandardCharacterNamesOne.name),
            ).toHaveLength(1);
            expect(
                await screen.findAllByText(lgDocumentNonStandardCharacterNamesTwo.name),
            ).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });

        it('can upload documents to LG forms using button', async () => {
            renderApp();

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText('NHS number: ' + formatNhsNumber(mockPatient.nhsNumber)),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgFiles);
            });

            expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });

        it('can upload documents to LG forms using drag and drop when dataTransfer type is files', async () => {
            renderApp();

            const dropzone = screen.getByTestId('dropzone');

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText('NHS number: ' + formatNhsNumber(mockPatient.nhsNumber)),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();
            expect(
                screen.getByText('Drag and drop a file or multiple files here'),
            ).toBeInTheDocument();

            fireEvent.drop(dropzone, { dataTransfer: { files: lgFiles } });

            expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });
        it('can upload documents to LG forms using drag and drop when dataTransfer type is items', async () => {
            renderApp();
            const dropzone = screen.getByTestId('dropzone');

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText('NHS number: ' + formatNhsNumber(mockPatient.nhsNumber)),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();
            expect(
                screen.getByText('Drag and drop a file or multiple files here'),
            ).toBeInTheDocument();
            fireEvent.drop(dropzone, {
                dataTransfer: {
                    items: lgFiles.map((file) => ({
                        kind: 'file',
                        type: file.type,
                        getAsFile: () => file,
                    })),
                },
            });

            expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });
        it('can upload documents to LG forms using drag and drop and button', async () => {
            renderApp();
            const dropzone = screen.getByTestId('dropzone');

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();
            expect(
                screen.getByText('Drag and drop a file or multiple files here'),
            ).toBeInTheDocument();
            fireEvent.drop(dropzone, { dataTransfer: { files: [lgDocumentOne] } });

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgDocumentTwo);
            });
            expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });
        it('does upload and then remove a file', async () => {
            renderApp();

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgFiles);
            });

            expect(screen.getByText(lgDocumentOne.name)).toBeInTheDocument();

            const removeFile = await screen.findByRole('button', {
                name: `Remove ${lgDocumentOne.name} from selection`,
            });

            act(() => {
                userEvent.click(removeFile);
            });

            expect(screen.queryByText(lgDocumentOne.name)).not.toBeInTheDocument();
            expect(screen.getByText(lgDocumentTwo.name)).toBeInTheDocument();
        });
        it('does upload and then remove all a files', async () => {
            renderApp();

            expect(
                screen.queryByRole('button', {
                    name: `Remove all`,
                }),
            ).not.toBeInTheDocument();

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgFiles);
            });

            expect(screen.getByText(lgDocumentOne.name)).toBeInTheDocument();
            expect(screen.getByText(lgDocumentTwo.name)).toBeInTheDocument();

            const removeAll = screen.getByRole('button', {
                name: `Remove all`,
            });
            expect(removeAll).toBeInTheDocument();
            act(() => {
                userEvent.click(removeAll);
            });

            expect(screen.queryByText(lgDocumentOne.name)).not.toBeInTheDocument();
            expect(screen.queryByText(lgDocumentTwo.name)).not.toBeInTheDocument();
        });
        it('does not upload either forms if selected file is more than 5GB', async () => {
            renderApp();

            const documentBig = buildLgFile(3, 2, 'Joe Blogs', 6 * Math.pow(1024, 3));

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), documentBig);
            });

            expect(screen.getByText(documentBig.name)).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText('Please ensure that all files are less than 5GB in size'),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if selected file is not PDF', async () => {
            renderApp();

            const lgFileWithBadType = new File(
                ['test'],
                `1of2000_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf`,
                {
                    type: 'text/plain',
                },
            );

            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), lgFileWithBadType);
            });

            expect(screen.getByText(lgFileWithBadType.name)).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required file type. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if total number of file does not match file name', async () => {
            renderApp();

            const lgExtraFile = buildLgFile(3, 3, 'Joe Blogs');

            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), lgExtraFile);
            });

            expect(screen.getByText(lgExtraFile.name)).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required filename format. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if selected file does not match naming conventions', async () => {
            renderApp();

            const pdfFileWithBadName = new File(['test'], `test_not_up_to_naming_conventions.pdf`, {
                type: 'application/pdf',
            });
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), pdfFileWithBadName);
            });

            expect(screen.getByText(pdfFileWithBadName.name)).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required filename format. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if selected file number is bigger than number of total files', async () => {
            renderApp();

            const pdfFileWithBadNumber = buildLgFile(2, 1, 'Joe Blogs');
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), pdfFileWithBadNumber);
            });

            expect(screen.getByText(pdfFileWithBadNumber.name)).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required filename format. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if files do not match each other', async () => {
            renderApp();

            const joeBloggsFile = new File(
                ['test'],
                `1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf`,
                {
                    type: 'application/pdf',
                },
            );
            const johnSmithFile = new File(
                ['test'],
                `2of2_Lloyd_George_Record_[John Smith]_[9876543210]_[25-12-2019].pdf`,
                {
                    type: 'application/pdf',
                },
            );
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [
                    joeBloggsFile,
                    johnSmithFile,
                ]);
            });

            expect(screen.getByText(joeBloggsFile.name)).toBeInTheDocument();
            expect(screen.getByText(johnSmithFile.name)).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required filename format. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if two or more files match name/size', async () => {
            const duplicateFileWarning = 'There are two or more documents with the same name.';
            renderApp();

            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [
                    lgDocumentTwo,
                    lgDocumentTwo,
                ]);
            });

            expect(screen.getAllByText(lgDocumentTwo.name)).toHaveLength(2);

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'There are documents chosen that have the same name, a record with duplicate file names can not be uploaded because it does not match the required file format. Please check the files(s) and try again.',
                ),
            ).toBeInTheDocument();
            expect(screen.queryByText(duplicateFileWarning)).not.toBeInTheDocument();
        });

        it("does allow the user to add the same file again if they remove for '%s' input", async () => {
            renderApp();

            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [
                    lgDocumentOne,
                    lgDocumentTwo,
                ]);
            });

            const removeFile = await screen.findByRole('button', {
                name: `Remove ${lgDocumentOne.name} from selection`,
            });

            act(() => {
                userEvent.click(removeFile);
            });
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgDocumentOne]);
            });

            expect(await screen.findByText(lgDocumentOne.name)).toBeInTheDocument();
        });
    });

    const TestApp = (props: Partial<Props>) => {
        const [documents, setDocuments] = useState<Array<UploadDocument>>([]);

        return (
            <LloydGeorgeFileInputStage
                documents={documents}
                setDocuments={setDocuments}
                setStage={setStageMock}
                {...props}
            />
        );
    };

    const renderApp = (props?: Partial<Props>) => {
        render(<TestApp {...props} />);
    };
});
