export const getFormattedDate = (date: Date) => {
    if (!date) {
        return "Invalid date";
    }

    return date.toLocaleDateString("en-GB");
};
