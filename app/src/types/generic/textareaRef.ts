import type { MutableRefObject } from 'react';
import type { RefCallBack } from 'react-hook-form';

export interface TextAreaRef extends MutableRefObject<HTMLTextAreaElement | null>, RefCallBack {}
