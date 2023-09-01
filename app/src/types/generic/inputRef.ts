import type { MutableRefObject } from 'react';
import type { RefCallBack } from 'react-hook-form';

export interface InputRef extends MutableRefObject<HTMLInputElement | null>, RefCallBack {}
