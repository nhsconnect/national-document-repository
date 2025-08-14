export const getFormattedDate = (date: Date) => {
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });
};

export const formatDateWithDashes = (date: Date): string => {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();

    return `${day}-${month}-${year}`;
};

export const getFormattedDateFromString = (dateString: string | undefined): string => {
  if (!dateString) {
    return '';
  }
  return getFormattedDate(new Date(dateString));
};