export type ErrorMessageMap<T extends string> = Record<
    T,
    {
        inline: string;
        errorBox: string;
    }
>;

export type ErrorMessageListItem<T extends string> = {
    error: T;
    linkId?: string;
    details?: string;
};

export type GroupedErrorRecords<T extends string> = Partial<
    Record<T, { linkIds: string[]; errorMessage: string }>
>;

export type GroupErrors<T extends string> = (
    errors: ErrorMessageListItem<T>[],
) => GroupedErrorRecords<T>;
