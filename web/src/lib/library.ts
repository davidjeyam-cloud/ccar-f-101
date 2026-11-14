import { useData } from './data'

/** Loads web/public/data/library/<name>.json (static content pages in the Library). The error is returned, never swallowed. */
export const useLibrary = <T,>(name: string) => useData<T>(`library/${name}.json`)
