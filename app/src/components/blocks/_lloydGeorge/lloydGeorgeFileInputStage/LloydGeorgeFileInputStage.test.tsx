import { act, fireEvent, render, screen } from '@testing-library/react';
import { buildPatientDetails, buildLgFile } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import userEvent from '@testing-library/user-event';
import LloydGeorgeFileInputStage, { Props } from './LloydGeorgeFileInputStage';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import { useState } from 'react';
import { MomentInput } from 'moment';

import { fileUploadErrorMessages } from '../../../../helpers/utils/fileUploadErrorMessages';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';

jest.mock('../../../../helpers/utils/toFileList', () => ({
    default: () => [],
}));
jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

jest.mock('moment', () => {
    return (arg: MomentInput) => {
        if (!arg) {
            arg = '2020-01-01T00:00:00.000Z';
        }
        return jest.requireActual('moment')(arg);
    };
});

window.scrollTo = jest.fn() as jest.Mock;

const submitDocumentsMock = jest.fn();

const mockedUsePatient = usePatient as jest.Mock;
const mockPatient = buildPatientDetails();

const mockedUseNavigate = jest.fn();

const lgDocumentOne = buildLgFile(1, 2, 'John Doe');
const lgDocumentTwo = buildLgFile(2, 2, 'John Doe');
const lgFiles = [lgDocumentOne, lgDocumentTwo];

const lgDocumentThreeNamesOne = buildLgFile(1, 2, 'Dom Jacob Alexander');
const lgDocumentThreeNamesTwo = buildLgFile(2, 2, 'Dom Jacob Alexander');
const lgFilesThreeNames = [lgDocumentThreeNamesOne, lgDocumentThreeNamesTwo];
const mockPatientThreeWordsName = buildPatientDetails({
    givenName: ['Dom', 'Jacob'],
    familyName: 'Alexander',
});

const nonStandardCharName =
    'DomžĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖ JacobŗŘřŚśŜŝŞşŠšŢţŤťŦŧ AŨũŪūŬŭŮůŰűŲer';
const lgDocumentNonStandardCharacterNamesOne = buildLgFile(1, 2, nonStandardCharName);
const lgDocumentNonStandardCharacterNamesTwo = buildLgFile(2, 2, nonStandardCharName);
const lgFilesNonStandardCharacterNames = [
    lgDocumentNonStandardCharacterNamesOne,
    lgDocumentNonStandardCharacterNamesTwo,
];
const mockPatientNonStandardCharName = buildPatientDetails({
    givenName: nonStandardCharName.split(' ').slice(0, 2),
    familyName: nonStandardCharName.split(' ')[2],
});

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
            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });

        it('can upload documents to LG forms with multiple names using button', async () => {
            mockedUsePatient.mockReturnValue(mockPatientThreeWordsName);

            renderApp();

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    'NHS number: ' + formatNhsNumber(mockPatientThreeWordsName.nhsNumber),
                ),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgFilesThreeNames);
            });

            expect(await screen.findAllByText(lgDocumentThreeNamesOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentThreeNamesTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });

        it('can upload documents to LG forms with non standard characters using button', async () => {
            mockedUsePatient.mockReturnValue(mockPatientNonStandardCharName);

            renderApp();

            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    'NHS number: ' + formatNhsNumber(mockPatientNonStandardCharName.nhsNumber),
                ),
            ).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();

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
            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgFiles);
            });
            expect(screen.getByText(`${lgFiles.length} files chosen`)).toBeInTheDocument();
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
            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
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
            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
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
            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
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
        it('can select and then remove a file', async () => {
            renderApp();
            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), [
                    lgDocumentOne,
                    lgDocumentTwo,
                    lgDocumentThreeNamesOne,
                ]);
            });

            const removeFile = await screen.findByRole('button', {
                name: `Remove ${lgDocumentThreeNamesOne.name} from selection`,
            });

            act(() => {
                userEvent.click(removeFile);
            });

            expect(screen.getByText(lgDocumentOne.name)).toBeInTheDocument();
            expect(screen.getByText(lgDocumentTwo.name)).toBeInTheDocument();
            expect(screen.queryByText(lgDocumentThreeNamesOne.name)).not.toBeInTheDocument();
        });
        it('can select and then remove all files', async () => {
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
        it('does not upload if selected file is more than 5GB', async () => {
            renderApp();

            const documentBig = buildLgFile(1, 2, 'Joe Blogs', 6 * Math.pow(1024, 3));

            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), documentBig);
            });

            const errorBox = screen.getByTestId('error-box');
            expect(errorBox).toHaveTextContent(documentBig.name);
            expect(errorBox).toHaveTextContent(fileUploadErrorMessages.fileSizeError.message);

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(submitDocumentsMock).not.toBeCalled();
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
            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });
            expect(
                screen.getByText('There is a problem with some of your files'),
            ).toBeInTheDocument();

            const errorBox = screen.getByTestId('error-box');
            expect(errorBox).toHaveTextContent(lgFileWithBadType.name);

            expect(
                screen.getByText(fileUploadErrorMessages.fileTypeError.message),
            ).toBeInTheDocument();
            expect(
                screen.getByText(fileUploadErrorMessages.fileTypeError.errorBox),
            ).toBeInTheDocument();

            expect(submitDocumentsMock).not.toBeCalled();
        });

        it('does not upload LG form if total number of file does not match file name', async () => {
            renderApp();

            const lgExtraFile = buildLgFile(3, 3, 'John Doe');

            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), lgExtraFile);
            });

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });
            expect(
                screen.getByText('There is a problem with some of your files'),
            ).toBeInTheDocument();

            const errorBox = screen.getByTestId('error-box');
            expect(errorBox).toHaveTextContent(lgExtraFile.name);
            expect(errorBox).toHaveTextContent(
                fileUploadErrorMessages.fileNumberMissingError.errorBox,
            );

            expect(submitDocumentsMock).not.toBeCalled();
        });

        it('does not upload LG form if selected file does not match naming conventions', async () => {
            renderApp();

            const pdfFileWithBadName = new File(['test'], `test_not_up_to_naming_conventions.pdf`, {
                type: 'application/pdf',
            });
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), pdfFileWithBadName);
            });

            expect(screen.getAllByText(pdfFileWithBadName.name)).toHaveLength(2);

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                screen.getByText(fileUploadErrorMessages.generalFileNameError.message),
            ).toBeInTheDocument();
            expect(
                screen.getByText(fileUploadErrorMessages.generalFileNameError.errorBox),
            ).toBeInTheDocument();

            expect(submitDocumentsMock).not.toBeCalled();
        });

        it('does not upload LG form if selected file number is bigger than number of total files', async () => {
            renderApp();

            const pdfFileWithBadNumber = buildLgFile(2, 1, 'Joe Blogs');
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), pdfFileWithBadNumber);
            });

            const errorBox = screen.getByTestId('error-box');
            expect(errorBox).toHaveTextContent(pdfFileWithBadNumber.name);
            expect(errorBox).toHaveTextContent(
                fileUploadErrorMessages.fileNumberOutOfRangeError.errorBox,
            );

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(submitDocumentsMock).not.toBeCalled();
        });

        it('does not upload LG form if files does not match patient details', async () => {
            renderApp();

            const joeBloggsFile = new File(
                ['test'],
                `1of1_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf`,
                {
                    type: 'application/pdf',
                },
            );

            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [joeBloggsFile]);
                userEvent.click(screen.getByText('Upload'));
            });

            const errorBox = screen.getByTestId('error-box');
            expect(errorBox).toHaveTextContent(fileUploadErrorMessages.patientNameError.errorBox);
            expect(errorBox).toHaveTextContent(fileUploadErrorMessages.dateOfBirthError.errorBox);
            expect(errorBox).toHaveTextContent(fileUploadErrorMessages.nhsNumberError.errorBox);

            expect(submitDocumentsMock).not.toBeCalled();
        });

        it('does not upload LG form if two or more files match name/size', async () => {
            renderApp();

            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [
                    lgDocumentTwo,
                    lgDocumentTwo,
                ]);
            });

            const errorBox = screen.getByTestId('error-box');
            expect(errorBox).toHaveTextContent(lgDocumentTwo.name);

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(errorBox).toHaveTextContent(fileUploadErrorMessages.duplicateFile.errorBox);

            expect(submitDocumentsMock).not.toBeCalled();
        });

        it('does not upload LG form if no file was provided', async () => {
            renderApp();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(fileUploadErrorMessages.noFiles.message),
            ).toBeInTheDocument();

            expect(
                await screen.findByText(fileUploadErrorMessages.noFiles.errorBox),
            ).toBeInTheDocument();

            expect(window.scrollTo).toHaveBeenCalledWith(0, 0);

            expect(submitDocumentsMock).not.toBeCalled();
        });

        describe('Validation with patient details from PDS', () => {
            const setDocsAndClickUploadButton = (documents: File[]) => {
                return act(async () => {
                    userEvent.upload(screen.getByTestId(`button-input`), documents);
                    userEvent.click(screen.getByText('Upload'));
                });
            };

            it('does not upload LG if patient name does not match', async () => {
                mockedUsePatient.mockReturnValue(
                    buildPatientDetails({
                        givenName: ['Janet', 'Doe'],
                    }),
                );
                const documentsToUpload = [lgDocumentOne, lgDocumentTwo];

                renderApp();

                await setDocsAndClickUploadButton(documentsToUpload);

                expect(
                    await screen.findAllByText(fileUploadErrorMessages.patientNameError.message),
                ).toHaveLength(2);
                expect(
                    await screen.findAllByText(fileUploadErrorMessages.patientNameError.errorBox),
                ).toHaveLength(2);

                expect(submitDocumentsMock).not.toBeCalled();
            });

            it('does not upload LG if patient date of birth does not match', async () => {
                mockedUsePatient.mockReturnValue(
                    buildPatientDetails({
                        birthDate: '1993-04-05',
                    }),
                );
                const documentsToUpload = [lgDocumentOne, lgDocumentTwo];

                renderApp();

                await setDocsAndClickUploadButton(documentsToUpload);

                expect(
                    await screen.findAllByText(fileUploadErrorMessages.dateOfBirthError.message),
                ).toHaveLength(2);
                expect(
                    await screen.findAllByText(fileUploadErrorMessages.dateOfBirthError.errorBox),
                ).toHaveLength(2);

                expect(submitDocumentsMock).not.toBeCalled();
            });

            it('does not upload LG if patient nhs number does not match', async () => {
                mockedUsePatient.mockReturnValue(
                    buildPatientDetails({
                        nhsNumber: '2345678901',
                    }),
                );
                const documentsToUpload = [lgDocumentOne, lgDocumentTwo];

                renderApp();

                await setDocsAndClickUploadButton(documentsToUpload);

                expect(
                    await screen.findAllByText(fileUploadErrorMessages.nhsNumberError.message),
                ).toHaveLength(2);
                expect(
                    await screen.findAllByText(fileUploadErrorMessages.nhsNumberError.errorBox),
                ).toHaveLength(2);

                expect(submitDocumentsMock).not.toBeCalled();
            });

            it('can display multiple errors related to patient details check', async () => {
                mockedUsePatient.mockReturnValue(
                    buildPatientDetails({
                        givenName: ['Jack', 'Bloggs'],
                        birthDate: '1993-04-05',
                        nhsNumber: '2345678901',
                    }),
                );
                const documentsToUpload = [lgDocumentOne, lgDocumentTwo];

                renderApp();

                await setDocsAndClickUploadButton(documentsToUpload);

                const expectedErrors = [
                    fileUploadErrorMessages.nhsNumberError,
                    fileUploadErrorMessages.dateOfBirthError,
                    fileUploadErrorMessages.patientNameError,
                ];

                expectedErrors.forEach((errorType) => {
                    expect(screen.getAllByText(errorType.message)).toHaveLength(2);
                    expect(screen.getAllByText(errorType.errorBox)).toHaveLength(2);
                });

                expect(submitDocumentsMock).not.toBeCalled();
            });

            it('Is case-insensitive when comparing patient names', async () => {
                mockedUsePatient.mockReturnValue(
                    buildPatientDetails({
                        givenName: ['JOHN', 'Blogg'],
                        familyName: 'SMITH',
                    }),
                );
                const documentsToUpload = [
                    buildLgFile(1, 2, 'John Blogg Smith'),
                    buildLgFile(2, 2, 'John Blogg Smith'),
                ];

                renderApp();

                await setDocsAndClickUploadButton(documentsToUpload);

                expect(
                    screen.queryByText(fileUploadErrorMessages.patientNameError.message),
                ).not.toBeInTheDocument();

                expect(submitDocumentsMock).toHaveBeenCalled();
            });

            it('Handles accent chars NFC NFD differences when comparing patient names', async () => {
                mockedUsePatient.mockReturnValue(mockPatientNonStandardCharName);
                const documentsToUpload = [
                    buildLgFile(1, 2, nonStandardCharName.normalize('NFD')),
                    buildLgFile(2, 2, nonStandardCharName.normalize('NFD')),
                ];

                renderApp();

                await setDocsAndClickUploadButton(documentsToUpload);

                expect(
                    screen.queryByText(fileUploadErrorMessages.patientNameError.message),
                ).not.toBeInTheDocument();

                expect(submitDocumentsMock).toHaveBeenCalled();
            });
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

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            renderApp();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when error box appears (file name error)', async () => {
            renderApp();
            act(() => {
                userEvent.upload(screen.getByTestId('button-input'), lgFilesThreeNames);
            });

            await screen.findAllByText('The patient’s name does not match this filename');

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when error box appears (no file selected)', async () => {
            renderApp();
            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });

            await screen.findByText('You did not select any file to upload');

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    const TestApp = (props: Partial<Props>) => {
        const [documents, setDocuments] = useState<Array<UploadDocument>>([]);

        return (
            <LloydGeorgeFileInputStage
                documents={documents}
                setDocuments={setDocuments}
                submitDocuments={submitDocumentsMock}
                {...props}
            />
        );
    };

    const renderApp = (props?: Partial<Props>) => {
        render(<TestApp {...props} />);
    };
});
