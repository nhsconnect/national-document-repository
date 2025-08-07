import { fireEvent, render, screen } from '@testing-library/react';
import { act } from 'react';
import { buildLgFileOld, buildPatientDetails } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import userEvent from '@testing-library/user-event';
import LloydGeorgeFileInputStage, { Props } from './LloydGeorgeFileInputStage';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import { useState } from 'react';
import { fileUploadErrorMessages } from '../../../../helpers/utils/fileUploadErrorMessages';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../../helpers/utils/toFileList', () => ({
    default: () => [],
}));
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();

window.scrollTo = vi.fn() as Mock;

const submitDocumentsMock = vi.fn();

const mockedUsePatient = usePatient as Mock;
const mockPatient = buildPatientDetails();

const mockedUseNavigate = vi.fn();

const lgDocumentOne = buildLgFileOld(1, 2, 'John Doe');
const lgDocumentTwo = buildLgFileOld(2, 2, 'John Doe');
const lgFiles = [lgDocumentOne, lgDocumentTwo];

const lgDocumentThreeNamesOne = buildLgFileOld(1, 2, 'Dom Jacob Alexander');
const lgDocumentThreeNamesTwo = buildLgFileOld(2, 2, 'Dom Jacob Alexander');
const lgFilesThreeNames = [lgDocumentThreeNamesOne, lgDocumentThreeNamesTwo];
const mockPatientThreeWordsName = buildPatientDetails({
    givenName: ['Dom', 'Jacob'],
    familyName: 'Alexander',
});

const nonStandardCharName =
    'DomžĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖ JacobŗŘřŚśŜŝŞşŠšŢţŤťŦŧ AŨũŪūŬŭŮůŰűŲer';
const lgDocumentNonStandardCharacterNamesOne = buildLgFileOld(1, 2, nonStandardCharName);
const lgDocumentNonStandardCharacterNamesTwo = buildLgFileOld(2, 2, nonStandardCharName);
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
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        vi.clearAllMocks();
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

            expect(
                screen.getByRole('button', { name: 'Select the files you wish to upload' }),
            ).toBeInTheDocument();

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

            userEvent.upload(screen.getByTestId('button-input'), lgFilesThreeNames);

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

            userEvent.upload(screen.getByTestId('button-input'), lgFilesNonStandardCharacterNames);
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

            await userEvent.upload(screen.getByTestId('button-input'), lgFiles);
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

            userEvent.upload(screen.getByTestId('button-input'), lgDocumentTwo);
            expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });
        it('can select and then remove a file', async () => {
            renderApp();
            await userEvent.upload(screen.getByTestId('button-input'), [
                lgDocumentOne,
                lgDocumentTwo,
                lgDocumentThreeNamesOne,
            ]);

            const removeFile = await screen.findByRole('button', {
                name: `Remove ${lgDocumentThreeNamesOne.name} from selection`,
            });

            await userEvent.click(removeFile);

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

            await userEvent.upload(screen.getByTestId('button-input'), lgFiles);

            expect(screen.getByText(lgDocumentOne.name)).toBeInTheDocument();
            expect(screen.getByText(lgDocumentTwo.name)).toBeInTheDocument();

            const removeAll = screen.getByRole('button', {
                name: `Remove all`,
            });
            expect(removeAll).toBeInTheDocument();
            await userEvent.click(removeAll);

            expect(screen.queryByText(lgDocumentOne.name)).not.toBeInTheDocument();
            expect(screen.queryByText(lgDocumentTwo.name)).not.toBeInTheDocument();
        });

        it('does not upload LG form if no file was provided', async () => {
            renderApp();

            await userEvent.click(screen.getByText('Upload'));

            expect(
                await screen.findByText(fileUploadErrorMessages.noFiles.inline),
            ).toBeInTheDocument();

            expect(
                await screen.findByText(fileUploadErrorMessages.noFiles.errorBox),
            ).toBeInTheDocument();

            expect(window.scrollTo).toHaveBeenCalledWith(0, 0);

            expect(submitDocumentsMock).not.toBeCalled();
        });

        it("does allow the user to add the same file again if they remove for '%s' input", async () => {
            renderApp();

            userEvent.upload(screen.getByTestId(`button-input`), [lgDocumentOne, lgDocumentTwo]);

            const removeFile = await screen.findByRole('button', {
                name: `Remove ${lgDocumentOne.name} from selection`,
            });

            await userEvent.click(removeFile);
            await userEvent.upload(screen.getByTestId(`button-input`), [lgDocumentOne]);

            expect(await screen.findByText(lgDocumentOne.name)).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            renderApp();

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
