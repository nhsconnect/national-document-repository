import getMergedPdfBlob from './pdfMerger';

// Mock PDF merger
const mockAdd = vi.fn();
const mockSetMetadata = vi.fn();
const mockSaveAsBlob = vi.fn();

vi.mock('pdf-merger-js/browser', () => ({
    default: vi.fn(() => ({
        add: mockAdd,
        setMetadata: mockSetMetadata,
        saveAsBlob: mockSaveAsBlob,
    })),
}));

describe('getMergedPdfBlob', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';

        // Reset mocks
        mockAdd.mockClear().mockResolvedValue(undefined);
        mockSetMetadata.mockClear().mockResolvedValue(undefined);
        mockSaveAsBlob
            .mockClear()
            .mockResolvedValue(new Blob(['test'], { type: 'application/pdf' }));
        URL.createObjectURL = vi.fn().mockReturnValue('blob:test-url');
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('should return expected blob', async () => {
        const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });

        const mockBlob = new Blob(['test pdf content'], { type: 'application/pdf' });
        mockSaveAsBlob.mockResolvedValue(mockBlob);

        const blob = await getMergedPdfBlob([file]);

        expect(blob).toBe(mockBlob);
    });
});