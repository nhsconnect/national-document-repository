import type { MutableRefObject } from 'react';
import type { RefCallBack } from 'react-hook-form';

export interface SelectRef extends MutableRefObject<HTMLSelectElement | null>, RefCallBack {}
