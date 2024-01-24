import moment from 'moment';

export function unixTimestamp() {
    return moment().unix();
}
